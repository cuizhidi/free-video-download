from datetime import date, timezone
from typing import Optional

import jwt as pyjwt
from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from auth import decode_token
from database import get_db
from models import User, UsageCounter


def get_current_user(
    authorization: str = Header(..., description="Bearer <token>"),
    db: Session = Depends(get_db),
) -> User:
    """Require a valid JWT and return the authenticated user."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="无效的认证头")
    token = authorization[7:]
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="无效的 Token 类型")
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="无效的 Token")
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token 已过期，请重新登录")
    except pyjwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的 Token")

    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


def get_optional_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Optionally authenticate -- returns None when no valid token is present."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization[7:]
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
    except Exception:
        return None
    return db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()


def require_vip(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_vip:
        raise HTTPException(status_code=403, detail="该功能仅限 VIP 会员使用")
    return current_user


FREE_AI_DAILY_LIMIT = 3


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_and_increment_usage(
    usage_type: str,
    user: Optional[User],
    request: Request,
    db: Session,
) -> dict:
    """Check daily usage quota. Returns {"used": N, "limit": N, "is_vip": bool}.
    Raises HTTPException(403) if quota exceeded."""
    if user and user.is_vip:
        return {"used": 0, "limit": -1, "is_vip": True}

    today = date.today()

    if user:
        counter = db.query(UsageCounter).filter(
            UsageCounter.user_id == user.id,
            UsageCounter.usage_type == usage_type,
            UsageCounter.usage_date == today,
        ).first()
    else:
        ip = _get_client_ip(request)
        counter = db.query(UsageCounter).filter(
            UsageCounter.ip_address == ip,
            UsageCounter.user_id.is_(None),
            UsageCounter.usage_type == usage_type,
            UsageCounter.usage_date == today,
        ).first()

    current = counter.count if counter else 0

    if current >= FREE_AI_DAILY_LIMIT:
        raise HTTPException(
            status_code=403,
            detail={
                "error": f"今日免费额度已用完（{FREE_AI_DAILY_LIMIT} 次/天），升级 VIP 解锁无限使用",
                "code": "QUOTA_EXCEEDED",
                "used": current,
                "limit": FREE_AI_DAILY_LIMIT,
                "upgrade_url": "/checkout",
            },
        )

    if counter:
        counter.count += 1
    else:
        new_counter = UsageCounter(
            user_id=user.id if user else None,
            ip_address=_get_client_ip(request) if not user else None,
            usage_type=usage_type,
            usage_date=today,
            count=1,
        )
        db.add(new_counter)
    db.commit()

    return {"used": current + 1, "limit": FREE_AI_DAILY_LIMIT, "is_vip": False}


def get_usage_quota(
    usage_type: str,
    user: Optional[User],
    request: Request,
    db: Session,
) -> dict:
    """Read-only quota check (no increment)."""
    if user and user.is_vip:
        return {"used": 0, "limit": -1, "is_vip": True}

    today = date.today()

    if user:
        counter = db.query(UsageCounter).filter(
            UsageCounter.user_id == user.id,
            UsageCounter.usage_type == usage_type,
            UsageCounter.usage_date == today,
        ).first()
    else:
        ip = _get_client_ip(request)
        counter = db.query(UsageCounter).filter(
            UsageCounter.ip_address == ip,
            UsageCounter.user_id.is_(None),
            UsageCounter.usage_type == usage_type,
            UsageCounter.usage_date == today,
        ).first()

    current = counter.count if counter else 0
    return {"used": current, "limit": FREE_AI_DAILY_LIMIT, "is_vip": False}
