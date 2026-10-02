from __future__ import annotations
from pathlib import Path
from fastapi import HTTPException
from backend.app.core.config import settings

def safe_path(raw: str) -> Path:
    p=Path(raw).expanduser().resolve()
    roots=[Path(x).expanduser().resolve() for x in settings.allowed_path_roots.split(',') if x.strip()]
    if not any(p==r or r in p.parents for r in roots):
        raise HTTPException(403,"Path is outside configured research roots")
    return p
