"""Admin maintenance: purge specific users (and everything they own).

Disabled (404) unless ADMIN_TOKEN (>= 32 chars) is configured. Callers must send it in
the X-Admin-Token header; comparison is constant-time. Users are addressed by their
stable provider identity ("provider:account_id"), never by name.
"""

from __future__ import annotations

import hmac

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import get_db
from app.models.models import User
from app.services import purge

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    expected = get_settings().admin_token
    if not expected or len(expected) < 32:
        raise HTTPException(status_code=404, detail="Not Found")
    if not x_admin_token or not hmac.compare_digest(x_admin_token.encode(), expected.encode()):
        raise HTTPException(status_code=403, detail="Forbidden")


class PurgeRequest(BaseModel):
    identities: list[str] = Field(min_length=1, max_length=20)
    dry_run: bool = True


@router.post("/purge-users", dependencies=[Depends(require_admin)])
def purge_users(body: PurgeRequest, db: Session = Depends(get_db)) -> dict:
    report: list[dict] = []
    for ident in body.identities:
        provider, _, pid = ident.partition(":")
        user = db.scalar(select(User).where(User.auth_provider == provider, User.provider_account_id == pid))
        if not user:
            report.append({"identity": ident, "found": False})
            continue
        name = user.display_name
        counts = purge.purge(db, user, commit=False) if not body.dry_run else purge.counts(db, user)
        report.append({"identity": ident, "found": True, "name": name, **counts})
    if not body.dry_run:
        db.commit()
    return {"dry_run": body.dry_run, "users": report}
