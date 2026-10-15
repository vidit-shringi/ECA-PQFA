from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List

from backend.app.services.repository import connect, utc_now
from backend.app.services.utilities import sha256_json, sha256_bytes, canonical_json
from backend.app.services.merkle import root_from_leaf_hashes, inclusion_proof_from_hashes, consistency_proof, verify_inclusion, verify_consistency
from backend.app.services.signing import sign_hybrid, verify_classical, verify_mldsa


def append_event(event: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(event)
    event_id = str(payload.get("Event_ID", "")).strip()
    with connect() as con:
        existing = con.execute("SELECT 1 FROM provenance_events WHERE event_id=?", (event_id,)).fetchone() if event_id else None
        if not event_id or existing:
            event_id = f"EVT-{uuid.uuid4().hex}"
            payload["Event_ID"] = event_id
        row = con.execute("SELECT event_hash FROM provenance_events ORDER BY rowid DESC LIMIT 1").fetchone()
        previous = row["event_hash"] if row else ""
        payload_hash = sha256_json(payload)
        material = canonical_json({
            "event_id": event_id,
            "payload_hash": payload_hash,
            "previous_event_hash": previous,
        })
        event_hash = sha256_bytes(material.encode("utf-8"))
        con.execute(
            "INSERT INTO provenance_events(event_id,payload_json,event_hash,previous_event_hash,created_at) VALUES(?,?,?,?,?)",
            (event_id, json.dumps(payload, sort_keys=True), event_hash, previous, utc_now()),
        )
        con.commit()
    return {**payload, "Payload_Hash": payload_hash, "Previous_Event_Hash": previous, "Event_Hash": event_hash}


def all_events() -> List[Dict[str, Any]]:
    with connect() as con:
        rows = con.execute("SELECT * FROM provenance_events ORDER BY rowid ASC").fetchall()
    return [dict(row) for row in rows]


def event_hashes() -> List[str]:
    return [event["event_hash"] for event in all_events()]


def create_tree_head() -> Dict[str, Any]:
    hashes = event_hashes()
    size = len(hashes)
    root = root_from_leaf_hashes(hashes)
    tree_id = f"STH-{size:08d}-{uuid.uuid4().hex[:8]}"
    payload = {"tree_head_id": tree_id, "tree_size": size, "merkle_root": root}
    signed = canonical_json(payload).encode("utf-8")
    sig = sign_hybrid(signed)
    classical = sig["classical"]
    pq = sig["pqc"]
    with connect() as con:
        con.execute(
            "INSERT INTO tree_heads(tree_head_id,tree_size,merkle_root,signed_payload,classical_signature,classical_public_key,pq_signature,pq_public_key,signature_status,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (tree_id, size, root, signed.decode(), classical["signature"], classical["public_key"], pq.get("signature"), pq.get("public_key_pem"), sig["status"], utc_now()),
        )
        con.commit()
    return {**payload, "signed_payload": payload, "signature_status": sig["status"], "classical_signature": classical, "pqc_signature": pq}


def latest_tree_head() -> Dict[str, Any] | None:
    with connect() as con:
        row = con.execute("SELECT * FROM tree_heads ORDER BY tree_size DESC, created_at DESC LIMIT 1").fetchone()
    return dict(row) if row else None


def inclusion_for_event(event_id: str, tree_size: int | None = None) -> Dict[str, Any]:
    events = all_events()
    hashes = [event["event_hash"] for event in events]
    n = len(hashes)
    size = n if tree_size is None else tree_size
    if size > n or size <= 0:
        raise ValueError("invalid tree size")
    index = next((i for i, event in enumerate(events[:size]) if event["event_id"] == event_id), None)
    if index is None:
        raise ValueError("event not in requested tree")
    return inclusion_proof_from_hashes([bytes.fromhex(h) for h in hashes[:size]], index)


def consistency(old_size: int, new_size: int | None = None) -> Dict[str, Any]:
    events = all_events()
    n = len(events)
    size = n if new_size is None else new_size
    if old_size < 0 or size > n or old_size > size:
        raise ValueError("invalid tree sizes")
    hashes = [event["event_hash"] for event in events[:size]]
    # Convert the already-computed event hashes to the proof helper's raw items only
    # where that helper is expected to hash values. The provenance log uses hashes
    # directly as leaves, so produce the proof with the direct leaf-hash helper below.
    from backend.app.services.merkle import _mth, _consistency_proof
    leaves = [bytes.fromhex(value) for value in hashes]
    proof = [] if old_size == 0 or old_size == size else [item.hex() for item in _consistency_proof(old_size, size, leaves, True)]
    return {
        "old_size": old_size,
        "new_size": size,
        "old_root": _mth(leaves[:old_size]).hex() if old_size else __import__("hashlib").sha256(b"").hexdigest(),
        "new_root": _mth(leaves).hex() if leaves else __import__("hashlib").sha256(b"").hexdigest(),
        "proof": proof,
        "format": "RFC6962-subtree-hashes-over-event-hashes",
    }


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
        }).encode("utf-8"))
        if event.get("previous_event_hash") != previous:
            valid = False
            reasons.append(f"previous hash mismatch at {event['event_id']}")
        if event.get("event_hash") != expected_event:
            valid = False
            reasons.append(f"event hash mismatch at {event['event_id']}")
        previous = event["event_hash"]
        hashes.append(event["event_hash"])
    head = latest_tree_head()
    signature_valid = None
    pq_signature_valid = None
    if head:
        signature_valid = verify_classical(head["signed_payload"].encode(), head["classical_signature"], head["classical_public_key"])
        if not signature_valid:
            valid = False
            reasons.append("classical tree-head signature verification failed")
        if head.get("pq_signature") and head.get("pq_public_key"):
            pq_signature_valid = verify_mldsa(head["signed_payload"].encode(), head["pq_signature"], head["pq_public_key"])
            if not pq_signature_valid:
                valid = False
                reasons.append("post-quantum tree-head signature verification failed")
        size = int(head["tree_size"])
        if size > len(hashes) or size < 0:
            valid = False
            reasons.append("tree head size is outside the current log")
        elif root_from_leaf_hashes(hashes[:size]) != head["merkle_root"]:
            valid = False
            reasons.append("tree head root mismatch for its committed prefix")
        try:
            signed = json.loads(head["signed_payload"])
            if signed.get("tree_size") != size or signed.get("merkle_root") != head["merkle_root"]:
                valid = False
                reasons.append("signed tree-head payload does not match stored fields")
        except (TypeError, json.JSONDecodeError):
            valid = False
            reasons.append("signed tree-head payload is invalid JSON")
    return {
        "event_count": len(events),
        "chain_valid": valid,
        "merkle_root": root_from_leaf_hashes(hashes),
        "latest_tree_head": head,
        "tree_head_classical_signature_valid": signature_valid,
        "tree_head_pq_signature_valid": pq_signature_valid,
        "reasons": reasons,
        "trust_note": "A signature verified against a public key stored beside the signature is not an external trust anchor; pin or externally publish trusted keys/tree heads for tamper evidence.",
    }
