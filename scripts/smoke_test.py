from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
from backend.app.main import app


def main() -> int:
    with TestClient(app) as client:
        health = client.get("/api/health")
        dashboard = client.get("/api/dashboard")
        assert health.status_code == 200, health.text
        assert dashboard.status_code == 200, dashboard.text
        print("health=PASS")
        print("dashboard=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
