from typing import Optional

import jwt as pyjwt
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from auth import decode_token
from database import get_db
from models import User


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
