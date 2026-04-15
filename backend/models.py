import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String,
)
from sqlalchemy.orm import relationship

from database import Base


def _uuid():
    return str(uuid.uuid4())


def _utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=True)
    name = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    auth_provider = Column(String, nullable=False, default="email")
    auth_provider_id = Column(String, nullable=True)
    stripe_customer_id = Column(String, nullable=True, unique=True, index=True)
    is_vip = Column(Boolean, default=False)
    vip_expire_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    subscriptions = relationship("Subscription", back_populates="user")
    payments = relationship("Payment", back_populates="user")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    stripe_subscription_id = Column(String, unique=True, nullable=False, index=True)
    stripe_price_id = Column(String, nullable=False)
    plan_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    user = relationship("User", back_populates="subscriptions")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    stripe_payment_intent_id = Column(String, unique=True, nullable=True, index=True)
    stripe_invoice_id = Column(String, nullable=True)
    amount = Column(Integer, nullable=False)
    currency = Column(String, default="cny")
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=_utcnow)

    user = relationship("User", back_populates="payments")


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(String, primary_key=True, default=_uuid)
    stripe_event_id = Column(String, unique=True, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_utcnow)
