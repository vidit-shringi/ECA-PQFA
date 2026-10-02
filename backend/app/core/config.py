from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel


ROOT = Path(__file__).resolve().parents[3]
DB_PATH = Path(os.getenv("ECA_PQFA_DB_PATH", str(ROOT / "data" / "eca_pqfa.sqlite3"))).resolve()
EVIDENCE_ROOT = Path(
    os.getenv("ECA_PQFA_EVIDENCE_ROOT", str(ROOT / "data" / "evidence"))
).resolve()


class Settings(BaseModel):
    app_name: str = os.getenv("ECA_PQFA_APP_NAME", "ECA-PQFA Research Engine")
    version: str = "3.2.0"
    host: str = os.getenv("ECA_PQFA_HOST", "127.0.0.1")
    port: int = int(os.getenv("ECA_PQFA_PORT", "8000"))
    spreadsheet_id: str = os.getenv("ECA_PQFA_SPREADSHEET_ID", "")
    apps_script_url: str = os.getenv("ECA_PQFA_APPS_SCRIPT_URL", "")
    api_key: str = os.getenv("ECA_PQFA_API_KEY", "")
    allowed_origins: str = os.getenv(
        "ECA_PQFA_ALLOWED_ORIGINS",
        "http://127.0.0.1:8000,http://localhost:8000",
    )
    require_api_key: bool = os.getenv("ECA_PQFA_REQUIRE_API_KEY", "false").lower() == "true"
    allowed_path_roots: str = os.getenv("ECA_PQFA_ALLOWED_PATH_ROOTS", str(ROOT))


settings = Settings()
