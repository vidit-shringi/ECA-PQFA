from __future__ import annotations

import requests
from typing import Any, Dict
from backend.app.core.config import settings


class SheetsClient:
    def __init__(self, url: str | None = None, api_key: str | None = None):
        self.url = url or settings.apps_script_url
        self.api_key = api_key or settings.api_key

    def _request(self, method: str, payload: Dict[str, Any]):
        if not self.url:
            raise ValueError("ECA_PQFA_APPS_SCRIPT_URL is not configured")
        body = dict(payload)
        if self.api_key and body.get("action") != "health":
            # Apps Script validates the JSON body field; a custom HTTP header is ignored.
            body["api_key"] = self.api_key
        response = requests.request(
            method, self.url, json=body,
            headers={"Content-Type": "application/json"}, timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and data.get("ok") is False:
            raise RuntimeError(str(data.get("error", "Apps Script request failed")))
        return data

    def health(self):
        return self._request("POST", {"action": "health"})

    def list_records(self, sheet: str):
        return self._request("POST", {"action": "list", "sheet": sheet})

    def upsert(self, sheet: str, record: Dict[str, Any]):
        return self._request("POST", {"action": "upsert", "sheet": sheet, "record": record})

    def sync_record(self, sheet: str, record: Dict[str, Any]):
        return self.upsert(sheet, record)
