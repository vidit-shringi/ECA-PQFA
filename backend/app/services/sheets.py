from __future__ import annotations

from typing import Any, Dict

import requests

from backend.app.core.config import settings


class SheetsClient:
    def __init__(self, url: str | None = None, api_key: str | None = None):
        self.url = url or settings.apps_script_url
        self.api_key = api_key or settings.api_key

    def _request(self, method: str, payload: Dict[str, Any]):
        if not self.url:
            raise RuntimeError("ECA_PQFA_APPS_SCRIPT_URL is not configured")
        body = dict(payload)
        # Apps Script Web Apps do not expose arbitrary request headers consistently;
        # the bridge's doPost authentication contract expects api_key in JSON.
        if self.api_key:
            body["api_key"] = self.api_key
        response = requests.request(
            method, self.url, json=body, headers={"Content-Type": "application/json"}, timeout=30
        )
        response.raise_for_status()
        result = response.json()
        if isinstance(result, dict) and result.get("ok") is False:
            raise RuntimeError(str(result.get("error", "Google Apps Script request failed")))
        return result

    def health(self):
        return self._request("POST", {"action": "health"})

    def list_records(self, sheet: str):
        return self._request("POST", {"action": "list", "sheet": sheet})

    def upsert(self, sheet: str, record: Dict[str, Any]):
        return self._request("POST", {"action": "upsert", "sheet": sheet, "record": record})

    def sync_record(self, sheet: str, record: Dict[str, Any]):
        return self.upsert(sheet, record)
