"""Test configuration: isolated SQLite DB, test JWT secret, offline grader."""

import os
import tempfile
import time

_tmpdir = tempfile.mkdtemp(prefix="vexalith-test-")
os.environ["DATABASE_URL"] = f"sqlite:///{_tmpdir}/test.db"
os.environ["BACKEND_JWT_SECRET"] = "test-secret-not-used-in-production-0123456789"
os.environ["XAI_API_KEY"] = ""
os.environ["LLM_API_KEY"] = ""
os.environ.pop("VERCEL", None)

import jwt  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.auth import JWT_AUDIENCE, JWT_ISSUER  # noqa: E402


def mint(provider="github", pid="1001", name="Ada Lovelace", email="ada@example.com",
         picture="https://avatars.example.com/ada.png", lifetime=300, secret=None, **overrides):
    now = int(time.time())
    claims = {
        "iss": JWT_ISSUER, "aud": JWT_AUDIENCE, "sub": f"{provider}:{pid}",
        "provider": provider, "provider_account_id": pid,
        "name": name, "email": email, "picture": picture,
        "iat": now, "exp": now + lifetime,
    }
    claims.update(overrides)
    return jwt.encode(claims, secret or os.environ["BACKEND_JWT_SECRET"], algorithm="HS256")


def auth(**kw):
    return {"Authorization": f"Bearer {mint(**kw)}"}


@pytest.fixture(scope="session")
def client():
    from app.main import app

    with TestClient(app) as c:
        yield c
