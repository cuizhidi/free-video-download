"""
Stripe subscription payment routes.

Security measures:
- Webhook signature verification on every event
- Idempotent event processing via webhook_events table
- Stripe Customer created once per user (stripe_customer_id)
- Checkout Sessions tied to authenticated users via client_reference_id
"""

import os
from datetime import datetime, timezone

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models import Payment, Subscription, User, WebhookEvent

router = APIRouter(prefix="/api/payment", tags=["payment"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
MONTHLY_PRICE_ID = os.getenv("STRIPE_MONTHLY_PRICE_ID", "")
YEARLY_PRICE_ID = os.getenv("STRIPE_YEARLY_PRICE_ID", "")
APP_URL = os.getenv("APP_URL", "http://localhost:5173")

PRICE_TO_PLAN = {}
if MONTHLY_PRICE_ID:
    PRICE_TO_PLAN[MONTHLY_PRICE_ID] = "monthly"
if YEARLY_PRICE_ID:
    PRICE_TO_PLAN[YEARLY_PRICE_ID] = "yearly"


# --------------- Schemas ---------------

class CheckoutRequest(BaseModel):
    plan: str  # "monthly" or "yearly"


class SubscriptionResponse(BaseModel):
    has_subscription: bool
    plan_type: str | None = None
    status: str | None = None
    current_period_end: str | None = None
    cancel_at_period_end: bool = False


# --------------- Helpers ---------------

def _get_or_create_customer(user: User, db: Session) -> str:
    """Ensure the user has a Stripe Customer, return customer ID."""
    if user.stripe_customer_id:
        return user.stripe_customer_id
    customer = stripe.Customer.create(
        email=user.email,
        name=user.name,
        metadata={"user_id": user.id},
    )
    user.stripe_customer_id = customer.id
    db.commit()
    return customer.id


def _sync_subscription(sub_data, user_id: str, db: Session):
    """Create or update local subscription record from Stripe subscription object."""
    stripe_sub_id = sub_data["id"]
    price_id = sub_data["items"]["data"][0]["price"]["id"] if sub_data["items"]["data"] else ""
    plan_type = PRICE_TO_PLAN.get(price_id, "unknown")

    period_start = datetime.fromtimestamp(sub_data["current_period_start"], tz=timezone.utc)
    period_end = datetime.fromtimestamp(sub_data["current_period_end"], tz=timezone.utc)

    sub = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == stripe_sub_id
    ).first()

    if sub:
        sub.status = sub_data["status"]
        sub.stripe_price_id = price_id
        sub.plan_type = plan_type
        sub.current_period_start = period_start
        sub.current_period_end = period_end
        sub.cancel_at_period_end = sub_data.get("cancel_at_period_end", False)
    else:
        sub = Subscription(
            user_id=user_id,
            stripe_subscription_id=stripe_sub_id,
            stripe_price_id=price_id,
            plan_type=plan_type,
            status=sub_data["status"],
            current_period_start=period_start,
            current_period_end=period_end,
            cancel_at_period_end=sub_data.get("cancel_at_period_end", False),
        )
        db.add(sub)

    user = db.query(User).filter(User.id == user_id).first()
    if user:
        if sub_data["status"] in ("active", "trialing"):
            user.is_vip = True
            user.vip_expire_at = period_end
        elif sub_data["status"] in ("canceled", "unpaid", "incomplete_expired"):
            user.is_vip = False
            user.vip_expire_at = None

    db.commit()


# --------------- Routes ---------------

@router.post("/create-checkout-session")
def create_checkout_session(
    req: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if req.plan == "monthly":
        price_id = MONTHLY_PRICE_ID
    elif req.plan == "yearly":
        price_id = YEARLY_PRICE_ID
    else:
        raise HTTPException(status_code=400, detail="无效的套餐类型")

    if not price_id:
        raise HTTPException(status_code=501, detail="支付功能未配置")

    customer_id = _get_or_create_customer(current_user, db)

    active_sub = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status.in_(["active", "trialing"]),
    ).first()
    if active_sub:
        raise HTTPException(status_code=400, detail="你已有有效订阅，无需重复购买")

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            customer=customer_id,
            client_reference_id=current_user.id,
            line_items=[{"price": price_id, "quantity": 1}],
            ui_mode="embedded",
            return_url=f"{APP_URL}/checkout/return?session_id={{CHECKOUT_SESSION_ID}}",
            metadata={"user_id": current_user.id, "plan": req.plan},
        )
    except stripe.StripeError as e:
        raise HTTPException(status_code=502, detail=f"Stripe 错误: {e.user_message or str(e)}")

    return {"client_secret": session.client_secret}


@router.get("/session-status")
def get_session_status(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.StripeError:
        raise HTTPException(status_code=404, detail="Session 不存在")

    return {
        "status": session.status,
        "payment_status": session.payment_status,
        "customer_email": session.customer_details.email if session.customer_details else None,
    }


@router.get("/subscription", response_model=SubscriptionResponse)
def get_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sub = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status.in_(["active", "trialing", "past_due"]),
    ).order_by(Subscription.created_at.desc()).first()

    if not sub:
        return SubscriptionResponse(has_subscription=False)

    return SubscriptionResponse(
        has_subscription=True,
        plan_type=sub.plan_type,
        status=sub.status,
        current_period_end=sub.current_period_end.isoformat() if sub.current_period_end else None,
        cancel_at_period_end=sub.cancel_at_period_end,
    )


@router.post("/create-portal-session")
def create_portal_session(
    current_user: User = Depends(get_current_user),
):
    if not current_user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="无支付记录")

    try:
        session = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=f"{APP_URL}/account",
        )
    except stripe.StripeError as e:
        raise HTTPException(status_code=502, detail=f"Stripe 错误: {e.user_message or str(e)}")

    return {"url": session.url}


# --------------- Webhook ---------------

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    if WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
    else:
        import json
        event = json.loads(payload)

    event_id = event.get("id", "")
    event_type = event.get("type", "")

    existing = db.query(WebhookEvent).filter(
        WebhookEvent.stripe_event_id == event_id
    ).first()
    if existing and existing.processed:
        return {"status": "already_processed"}

    if not existing:
        we = WebhookEvent(stripe_event_id=event_id, event_type=event_type)
        db.add(we)
        db.flush()
    else:
        we = existing

    try:
        _handle_event(event_type, event.get("data", {}).get("object", {}), db)
        we.processed = True
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {"status": "ok"}


def _handle_event(event_type: str, obj: dict, db: Session):
    if event_type == "checkout.session.completed":
        user_id = obj.get("client_reference_id") or obj.get("metadata", {}).get("user_id")
        sub_id = obj.get("subscription")
        if user_id and sub_id:
            sub_data = stripe.Subscription.retrieve(sub_id)
            _sync_subscription(sub_data, user_id, db)

    elif event_type in (
        "customer.subscription.updated",
        "customer.subscription.deleted",
    ):
        sub_data = obj
        customer_id = sub_data.get("customer")
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            _sync_subscription(sub_data, user.id, db)

    elif event_type == "invoice.payment_succeeded":
        customer_id = obj.get("customer")
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            pi_id = obj.get("payment_intent")
            if pi_id:
                exists = db.query(Payment).filter(
                    Payment.stripe_payment_intent_id == pi_id
                ).first()
                if not exists:
                    db.add(Payment(
                        user_id=user.id,
                        stripe_payment_intent_id=pi_id,
                        stripe_invoice_id=obj.get("id"),
                        amount=obj.get("amount_paid", 0),
                        currency=obj.get("currency", "cny"),
                        status="succeeded",
                    ))

            sub_id = obj.get("subscription")
            if sub_id:
                sub_data = stripe.Subscription.retrieve(sub_id)
                _sync_subscription(sub_data, user.id, db)

    elif event_type == "invoice.payment_failed":
        customer_id = obj.get("customer")
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            pi_id = obj.get("payment_intent")
            if pi_id:
                exists = db.query(Payment).filter(
                    Payment.stripe_payment_intent_id == pi_id
                ).first()
                if not exists:
                    db.add(Payment(
                        user_id=user.id,
                        stripe_payment_intent_id=pi_id,
                        stripe_invoice_id=obj.get("id"),
                        amount=obj.get("amount_due", 0),
                        currency=obj.get("currency", "cny"),
                        status="failed",
                    ))
            db.commit()
