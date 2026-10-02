from __future__ import annotations
import requests
from typing import Any, Dict
from backend.app.core.config import settings

class SheetsClient:
    def __init__(self, url: str | None = None, api_key: str | None = None):
        self.url=url or settings.apps_script_url
        self.api_key=api_key or settings.api_key
    def _request(self, method: str, payload: Dict[str, Any]):
        headers={"Content-Type":"application/json"}
        if self.api_key: headers["X-ECA-API-Key"]=self.api_key
        r=requests.request(method,self.url,json=payload,headers=headers,timeout=30)
        r.raise_for_status(); return r.json()
    def health(self): return self._request("POST",{"action":"health"})
    def list_records(self,sheet:str): return self._request("POST",{"action":"list","sheet":sheet})
    def upsert(self,sheet:str,record:Dict[str,Any]): return self._request("POST",{"action":"upsert","sheet":sheet,"record":record})
    def sync_record(self,sheet:str,record:Dict[str,Any]): return self.upsert(sheet,record)
