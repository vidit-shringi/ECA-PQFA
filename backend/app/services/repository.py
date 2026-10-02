from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.app.core.config import DB_PATH
from backend.app.core.schema import SHEETS


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("PRAGMA journal_mode=WAL")
    return con


def init_db() -> None:
    with connect() as con:
        con.execute("CREATE TABLE IF NOT EXISTS records (sheet TEXT NOT NULL, record_id TEXT NOT NULL, case_id TEXT, payload_json TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, PRIMARY KEY(sheet,record_id))")
        con.execute("CREATE TABLE IF NOT EXISTS provenance_events (event_id TEXT PRIMARY KEY, payload_json TEXT NOT NULL, event_hash TEXT NOT NULL, previous_event_hash TEXT, created_at TEXT NOT NULL)")
        con.execute("CREATE TABLE IF NOT EXISTS tree_heads (tree_head_id TEXT PRIMARY KEY, tree_size INTEGER NOT NULL, merkle_root TEXT NOT NULL, signed_payload TEXT NOT NULL, classical_signature TEXT NOT NULL, classical_public_key TEXT NOT NULL, pq_signature TEXT, pq_public_key TEXT, signature_status TEXT NOT NULL, created_at TEXT NOT NULL)")
        con.execute("CREATE TRIGGER IF NOT EXISTS provenance_no_update BEFORE UPDATE ON provenance_events BEGIN SELECT RAISE(ABORT,'provenance_events is append-only'); END")
        con.execute("CREATE TRIGGER IF NOT EXISTS provenance_no_delete BEFORE DELETE ON provenance_events BEGIN SELECT RAISE(ABORT,'provenance_events is append-only'); END")
        con.commit()


def list_records(sheet: str, limit: int=100, offset: int=0) -> List[Dict[str,Any]]:
    with connect() as con:
        rows=con.execute("SELECT payload_json FROM records WHERE sheet=? ORDER BY created_at DESC LIMIT ? OFFSET ?",(sheet,limit,offset)).fetchall()
    return [json.loads(r["payload_json"]) for r in rows]


def get_record(sheet: str, record_id: str) -> Optional[Dict[str,Any]]:
    with connect() as con:
        row=con.execute("SELECT payload_json FROM records WHERE sheet=? AND record_id=?",(sheet,record_id)).fetchone()
    return json.loads(row["payload_json"]) if row else None


def insert_record(sheet: str, record_id: str, record: Dict[str,Any], case_id: str="") -> Dict[str,Any]:
    t=utc_now()
    with connect() as con:
        con.execute("INSERT INTO records(sheet,record_id,case_id,payload_json,created_at,updated_at) VALUES(?,?,?,?,?,?)",(sheet,record_id,case_id,json.dumps(record,sort_keys=True,ensure_ascii=False),t,t)); con.commit()
    return record


def update_record(sheet: str, record_id: str, patch: Dict[str,Any]) -> Optional[Dict[str,Any]]:
    current=get_record(sheet,record_id)
    if current is None:return None
    current.update(patch)
    with connect() as con:
        con.execute("UPDATE records SET payload_json=?,updated_at=? WHERE sheet=? AND record_id=?",(json.dumps(current,sort_keys=True,ensure_ascii=False),utc_now(),sheet,record_id)); con.commit()
    return current


def delete_record(sheet: str, record_id: str) -> bool:
    with connect() as con:
        cur=con.execute("DELETE FROM records WHERE sheet=? AND record_id=?",(sheet,record_id)); con.commit(); return cur.rowcount>0


def count_records(sheet: str) -> int:
    with connect() as con:
        return int(con.execute("SELECT COUNT(*) c FROM records WHERE sheet=?",(sheet,)).fetchone()["c"])


def upsert_from_sheets(sheet: str, records: List[Dict[str,Any]]) -> int:
    id_field=next((k for k in SHEETS.get(sheet,[]) if k.endswith("_ID")),None)
    if not id_field: raise ValueError(f"No ID field defined for {sheet}")
    count=0
    for record in records:
        rid=str(record.get(id_field,"")).strip()
        if not rid: continue
        if get_record(sheet,rid): update_record(sheet,rid,record)
        else: insert_record(sheet,rid,record,record.get("Case_ID",""))
        count+=1
    return count
