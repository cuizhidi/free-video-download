import os
import re
import uuid
from pathlib import Path

import jwt as pyjwt
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from database import get_db
from deps import get_current_user
from models import User, DownloadHistory

AVATAR_DIR = Path(__file__).parent / "data" / "avatars"
AVATAR_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}

router = APIRouter(prefix="/api/auth", tags=["auth"])

APP_URL = os.getenv("APP_URL", "http://localhost:5173")

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


# --------------- Schemas ---------------

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    avatar_url: str | None = None
    auth_provider: str
    is_vip: bool
    vip_expire_at: str | None = None
    created_at: str

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


# --------------- Helpers ---------------

def _user_resp(u: User) -> UserResponse:
    return UserResponse(
        id=u.id,
        email=u.email,
        name=u.name,
        avatar_url=u.avatar_url,
        auth_provider=u.auth_provider,
        is_vip=u.is_vip,
        vip_expire_at=u.vip_expire_at.isoformat() if u.vip_expire_at else None,
        created_at=u.created_at.isoformat() if u.created_at else "",
    )


def _tokens_for(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token({"sub": user.id}),
        refresh_token=create_refresh_token({"sub": user.id}),
        user=_user_resp(user),
    )


# --------------- Routes ---------------

@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    email = req.email.lower().strip()
    if not EMAIL_RE.match(email):
        raise HTTPException(status_code=400, detail="邮箱格式不正确")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="密码至少 6 位")
    if not req.name.strip():
        raise HTTPException(status_code=400, detail="请输入用户名")

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="该邮箱已注册")

    user = User(
        email=email,
        password_hash=hash_password(req.password),
        name=req.name.strip(),
        auth_provider="email",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _tokens_for(user)


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    if not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    return _tokens_for(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh(req: RefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = decode_token(req.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="无效的 Refresh Token")
        user_id = payload.get("sub")
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh Token 已过期，请重新登录")
    except pyjwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的 Refresh Token")

    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return _tokens_for(user)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return _user_resp(current_user)


@router.post("/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="仅支持 JPG/PNG/WebP/GIF 格式")
    data = await file.read()
    if len(data) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片大小不能超过 2MB")
    ext = file.filename.rsplit(".", 1)[-1] if "." in (file.filename or "") else "jpg"
    fname = f"{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    (AVATAR_DIR / fname).write_bytes(data)
    if current_user.avatar_url and current_user.avatar_url.startswith("/api/auth/avatar/"):
        old_name = current_user.avatar_url.split("/")[-1]
        old_path = AVATAR_DIR / old_name
        if old_path.exists():
            old_path.unlink(missing_ok=True)
    current_user.avatar_url = f"/api/auth/avatar/{fname}"
    db.commit()
    db.refresh(current_user)
    return _user_resp(current_user)


@router.get("/avatar/{filename}")
async def get_avatar(filename: str):
    from fastapi.responses import FileResponse
    filepath = AVATAR_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="头像不存在")
    return FileResponse(str(filepath), headers={"Cache-Control": "public, max-age=86400"})


@router.get("/download-history")
def get_download_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    total = db.query(DownloadHistory).filter(
        DownloadHistory.user_id == current_user.id
    ).count()
    items = db.query(DownloadHistory).filter(
        DownloadHistory.user_id == current_user.id
    ).order_by(DownloadHistory.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": h.id,
                "video_url": h.video_url,
                "video_title": h.video_title,
                "thumbnail": h.thumbnail,
                "platform": h.platform,
                "quality": h.quality,
                "filesize": h.filesize,
                "created_at": h.created_at.isoformat() if h.created_at else "",
            }
            for h in items
        ],
    }


# --------------- OAuth: shared helper ---------------

def _oauth_finish(provider: str, provider_id: str, email: str,
                  name: str, avatar_url: str | None, db: Session) -> str:
    """Find-or-create a user via OAuth, return a frontend redirect URL with tokens."""
    email = email.lower().strip()
    user = db.query(User).filter(User.email == email).first()

    if user:
        if not user.auth_provider_id:
            user.auth_provider = provider
            user.auth_provider_id = provider_id
        if avatar_url and not user.avatar_url:
            user.avatar_url = avatar_url
        db.commit()
        db.refresh(user)
    else:
        user = User(
            email=email,
            name=name or email.split("@")[0],
            avatar_url=avatar_url,
            auth_provider=provider,
            auth_provider_id=provider_id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access = create_access_token({"sub": user.id})
    refresh = create_refresh_token({"sub": user.id})
    return (
        f"{APP_URL}/oauth-callback"
        f"?access_token={access}"
        f"&refresh_token={refresh}"
        f"&user={_user_resp(user).model_dump_json()}"
    )


# --------------- OAuth: Google ---------------

@router.get("/google")
def google_redirect(redirect: str = Query("")):
    from oauth import GOOGLE_CLIENT_ID, google_authorize_url
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=501, detail="Google 登录未配置")
    callback = f"{APP_URL}/api/auth/google/callback"
    url = google_authorize_url(callback, state=redirect)
    return RedirectResponse(url)


@router.get("/google/callback")
async def google_callback(
    code: str = Query(...),
    state: str = Query(""),
    db: Session = Depends(get_db),
):
    from oauth import google_exchange_code, google_get_userinfo
    callback = f"{APP_URL}/api/auth/google/callback"
    try:
        tokens = await google_exchange_code(code, callback)
        info = await google_get_userinfo(tokens["access_token"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google 登录失败: {e}")

    redirect_url = _oauth_finish(
        provider="google",
        provider_id=str(info.get("id", "")),
        email=info.get("email", ""),
        name=info.get("name", ""),
        avatar_url=info.get("picture"),
        db=db,
    )
    return RedirectResponse(redirect_url)


# --------------- OAuth: GitHub ---------------

@router.get("/github")
def github_redirect(redirect: str = Query("")):
    from oauth import GITHUB_CLIENT_ID, github_authorize_url
    if not GITHUB_CLIENT_ID:
        raise HTTPException(status_code=501, detail="GitHub 登录未配置")
    callback = f"{APP_URL}/api/auth/github/callback"
    url = github_authorize_url(callback, state=redirect)
    return RedirectResponse(url)


@router.get("/github/callback")
async def github_callback(
    code: str = Query(...),
    state: str = Query(""),
    db: Session = Depends(get_db),
):
    from oauth import github_exchange_code, github_get_user
    callback = f"{APP_URL}/api/auth/github/callback"
    try:
        tokens = await github_exchange_code(code, callback)
        info = await github_get_user(tokens["access_token"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"GitHub 登录失败: {e}")

    email = info.get("email", "")
    if not email:
        raise HTTPException(status_code=400, detail="无法获取 GitHub 邮箱，请在 GitHub 设置中公开邮箱")

    redirect_url = _oauth_finish(
        provider="github",
        provider_id=str(info.get("id", "")),
        email=email,
        name=info.get("name") or info.get("login", ""),
        avatar_url=info.get("avatar_url"),
        db=db,
    )
    return RedirectResponse(redirect_url)
