"""Public metadata: domains and languages."""

from fastapi import APIRouter

from app.content.domains import DOMAINS, LANGUAGES

router = APIRouter(tags=["meta"])


@router.get("/languages")
def languages() -> list[dict]:
    return LANGUAGES


@router.get("/domains")
def domains() -> list[dict]:
    return DOMAINS
