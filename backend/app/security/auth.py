from __future__ import annotations
import secrets
from fastapi import Header, HTTPException
from backend.app.core.config import settings


def require_api_key(x_eca_api_key: str | None = Header(default=None)):
    if not settings.require_api_key:
        return True
    if not settings.api_key:
        raise HTTPException(503, "API key authentication is enabled but ECA_PQFA_API_KEY is not configured")
    if not x_eca_api_key or not secrets.compare_digest(x_eca_api_key, settings.api_key):
        raise HTTPException(401, "Invalid or missing API key")
    return True
