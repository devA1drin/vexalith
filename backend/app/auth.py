"""
Backend authentication.

The Next.js server (Auth.js session holder) mints a short-lived HS256 JWT signed
with the shared BACKEND_JWT_SECRET and sends it as `Authorization: Bearer <jwt>`.
We verify signature, issuer, audience and expiry, then upsert the User by
(provider, provider_account_id). Client-supplied user ids are never trusted.
"""

from __future__ import annotations

from datetime import datetime, timezone

import jwt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import get_db
from app.models.models import User

JWT_ISSUER = "vexalith-web"
JWT_AUDIENCE = "vexalith-api"
MAX_TOKEN_LIFETIME_S = 15 * 60
ALLOWED_PROVIDERS = {"github", "google"}


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def decode_token(token: str) -> dict:
    secret = get_settings().backend_jwt_secret
    if not secret:
        raise HTTPException(status_code=503, detail="Authentication is not configured on the server")
    try:
        claims = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER,
            options={"require": ["exp", "iat", "sub", "iss", "aud"]},
            leeway=30,
        )
    except jwt.PyJWTError as exc:
        raise _unauthorized(f"Invalid token: {exc.__class__.__name__}") from exc
    if claims["exp"] - claims["iat"] > MAX_TOKEN_LIFETIME_S:
        raise _unauthorized("Token lifetime too long")
    provider = claims.get("provider")
    pid = claims.get("provider_account_id")
    if provider not in ALLOWED_PROVIDERS or not pid or claims["sub"] != f"{provider}:{pid}":
        raise _unauthorized("Invalid identity claims")
    return claims


def _clip(v: object, n: int) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s[:n] or None


def upsert_user(db: Session, claims: dict) -> User:
    provider = claims["provider"]
    pid = str(claims["provider_account_id"])
    name = _clip(claims.get("name"), 128)
    email = _clip(claims.get("email"), 320)
    picture = _clip(claims.get("picture"), 1024)
    if picture and not picture.startswith("https://"):
        picture = None

    user = db.query(User).filter_by(auth_provider=provider, provider_account_id=pid).one_or_none()
    now = datetime.now(timezone.utc)
    if user is None:
        user = User(
            auth_provider=provider,
            provider_account_id=pid,
            email=email,
            display_name=name or (email.split("@")[0] if email else f"{provider} user"),
            avatar_url=picture,
            created_at=now,
            last_login_at=now,
        )
        db.add(user)
        try:
            db.commit()
        except IntegrityError:  # concurrent first request
            db.rollback()
            user = db.query(User).filter_by(auth_provider=provider, provider_account_id=pid).one()
    else:
        changed = False
        for attr, val in (("display_name", name), ("email", email), ("avatar_url", picture)):
            if val and getattr(user, attr) != val:
                setattr(user, attr, val)
                changed = True
        if changed:
            db.commit()
    return user


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise _unauthorized("Missing bearer token")
    claims = decode_token(authorization.split(" ", 1)[1].strip())
    return upsert_user(db, claims)
