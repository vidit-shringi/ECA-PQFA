from __future__ import annotations

import json
from typing import Any, Dict, List

from backend.app.services.merkle import root_from_leaf_hashes, inclusion_proof_from_hashes, consistency_proof
from backend.app.services.repository import connect, utc_now
from backend.app.services.signing import sign_hybrid, verify_classical, verify_mldsa
from backend.app.services.utilities import canonical_json, generate_id, sha256_bytes, sha256_json


def _next_event_id() -> str:
    # Keep the identifier namespace independent of the generic records table.
    with connect() as con:
        row = con.execute("SELECT event_id FROM provenance_events ORDER BY rowid DESC LIMIT 1").fetchone()
    if row:
        try:
            sequence = int(str(row["event_id"]).rsplit("-", 1)[-1]) + 1
        except (TypeError, ValueError):
            sequence = 1
    else:
        sequence = 1
    return generate_id("05_PROVENANCE", sequence)


def append_event(event: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(event)
    payload.setdefault("Event_ID", _next_event_id())
    event_id = str(payload["Event_ID"])
    payload_hash = sha256_json(payload)
    with connect() as con:
        # BEGIN IMMEDIATE serializes sequence assignment and the append transaction.
        con.execute("BEGIN IMMEDIATE")
        row = con.execute("SELECT event_hash FROM provenance_events ORDER BY rowid DESC LIMIT 1").fetchone()
        previous = row["event_hash"] if row else ""
        material = canonical_json({
            "event_id": event_id,
            "payload_hash": payload_hash,
            "previous_event_hash": previous,
        })
        event_hash = sha256_bytes(material.encode())
        con.execute(
            "INSERT INTO provenance_events(event_id,payload_json,event_hash,previous_event_hash,created_at) VALUES(?,?,?,?,?)",
            (event_id, json.dumps(payload, sort_keys=True), event_hash, previous, utc_now()),
        )
        con.commit()
    return {**payload, "Payload_Hash": payload_hash, "Previous_Event_Hash": previous, "Event_Hash": event_hash}


def all_events() -> List[Dict[str, Any]]:
    with connect() as con:
        rows = con.execute("SELECT rowid AS sequence_no,* FROM provenance_events ORDER BY rowid ASC").fetchall()
    return [dict(r) for r in rows]


def event_hashes() -> List[str]:
    return [e["event_hash"] for e in all_events()]


def create_tree_head() -> Dict[str, Any]:
    hashes = event_hashes()
    size = len(hashes)
    root = root_from_leaf_hashes(hashes)
    # Include size and root in the signed payload. A size-based ID can be reused on
    # repeated snapshots; replace is intentional only for the same tree size/root.
    tree_id = f"STH-{size:08d}-{root[:12]}"
    payload = {"tree_head_id": tree_id, "tree_size": size, "merkle_root": root}
    signed = canonical_json(payload).encode()
    sig = sign_hybrid(signed)
    classical, pq = sig["classical"], sig["pqc"]
    with connect() as con:
        con.execute(
            "INSERT OR REPLACE INTO tree_heads(tree_head_id,tree_size,merkle_root,signed_payload,classical_signature,classical_public_key,pq_signature,pq_public_key,signature_status,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (tree_id, size, root, signed.decode(), classical["signature"], classical["public_key"],
             pq.get("signature"), pq.get("public_key_pem"), sig["status"], utc_now()),
        )
        con.commit()
    return {**payload, "signed_payload": payload, "signature_status": sig["status"], "classical_signature": classical, "pqc_signature": pq}


def latest_tree_head() -> Dict[str, Any] | None:
    with connect() as con:
        row = con.execute("SELECT * FROM tree_heads ORDER BY tree_size DESC, created_at DESC LIMIT 1").fetchone()
    return dict(row) if row else None


def inclusion_for_event(event_id: str, tree_size: int | None = None) -> Dict[str, Any]:
    events = all_events()
    n = len(events)
    size = n if tree_size is None else tree_size
    if size <= 0 or size > n:
        raise ValueError("invalid tree size")
    for idx, event in enumerate(events[:size]):
        if event["event_id"] == event_id:
            return inclusion_proof_from_hashes(
                [bytes.fromhex(e["event_hash"]) for e in events[:size]], idx
            )
    raise ValueError("event not in requested tree")


def consistency(old_size: int, new_size: int | None = None) -> Dict[str, Any]:
    events = all_events()
    n = len(events)
    size = n if new_size is None else new_size
    if old_size < 0 or size < 0 or size > n or old_size > size:
        raise ValueError("invalid tree sizes")
    return consistency_proof([bytes.fromhex(e["event_hash"]) for e in events[:size]], old_size)


def audit_chain() -> Dict[str, Any]:
    events = all_events()
    valid = True
    previous = ""
    hashes = []
    reasons = []
    for event in events:
        payload = json.loads(event["payload_json"])
        expected_payload = sha256_json(payload)
        expected_event = sha256_bytes(canonical_json({
            "event_id": event["event_id"],
            "payload_hash": expected_payload,
            "previous_event_hash": previous,
        }).encode())
        if event.get("previous_event_hash") != previous:
            valid = False
            reasons.append(f"previous hash mismatch at {event['event_id']}")
        if event.get("event_hash") != expected_event:
            valid = False
            reasons.append(f"event hash mismatch at {event['event_id']}")
        previous = event["event_hash"]
        hashes.append(previous)

    root = root_from_leaf_hashes(hashes)
    head = latest_tree_head()
    signature_valid = None
    pq_signature_valid = None
    head_consistent = None
    if head:
        try:
            signed_payload = head["signed_payload"].encode()
            signed = json.loads(head["signed_payload"])
            signature_valid = verify_classical(signed_payload, head["classical_signature"], head["classical_public_key"])
            if head.get("pq_signature") and head.get("pq_public_key"):
                pq_signature_valid = verify_mldsa(signed_payload, head["pq_signature"], head["pq_public_key"])
            size = int(head["tree_size"])
            expected_root = root_from_leaf_hashes(hashes[:size]) if 0 <= size <= len(hashes) else None
            head_consistent = (
                signed.get("tree_size") == size
                and signed.get("merkle_root") == head["merkle_root"]
                and expected_root == head["merkle_root"]
                and signature_valid is True
                and (head.get("pq_signature") is None or pq_signature_valid is True)
            )
            if not head_consistent:
                valid = False
                reasons.append("tree head, signature, size, or root mismatch")
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            valid = False
            head_consistent = False
            reasons.append(f"invalid tree head: {exc}")
    return {
        "event_count": len(events),
        "chain_valid": valid,
        "merkle_root": root,
        "latest_tree_head": head,
        "tree_head_classical_signature_valid": signature_valid,
        "tree_head_pq_signature_valid": pq_signature_valid,
        "tree_head_consistent": head_consistent,
        "reasons": reasons,
    }
