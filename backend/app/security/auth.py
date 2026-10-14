from __future__ import annotations

import secrets
from fastapi import Header, HTTPException
from backend.app.core.config import settings


def require_api_key(x_eca_api_key: str | None = Header(default=None)):
    if not settings.require_api_key:
        # Explicit LOCAL_DEMO opt-out is for local, non-sensitive development only.
        return True
    if not settings.api_key or settings.api_key == "CHANGE_ME_FOR_SHARED_DEPLOYMENTS":
        raise HTTPException(503, "Configure a unique ECA_PQFA_API_KEY before enabling authenticated API access")
    if not x_eca_api_key or not secrets.compare_digest(x_eca_api_key, settings.api_key):
        raise HTTPException(401, "Invalid or missing API key")
    return True
