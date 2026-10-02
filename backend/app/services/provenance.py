from __future__ import annotations

import json
from typing import Any, Dict, List
from backend.app.services.repository import connect, utc_now
from backend.app.services.utilities import sha256_json, sha256_bytes, canonical_json
from backend.app.services.merkle import root_from_leaf_hashes, inclusion_proof_from_hashes, consistency_proof, verify_inclusion, verify_consistency
from backend.app.services.signing import sign_hybrid, verify_classical, verify_mldsa


def append_event(event: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(event)
    event_id = payload["Event_ID"]
    payload_hash = sha256_json(payload)
    with connect() as con:
        row = con.execute("SELECT event_hash FROM provenance_events ORDER BY created_at DESC LIMIT 1").fetchone()
        previous = row["event_hash"] if row else ""
        material = canonical_json({"event_id":event_id,"payload_hash":payload_hash,"previous_event_hash":previous})
        event_hash = sha256_bytes(material.encode())
        con.execute("INSERT INTO provenance_events(event_id,payload_json,event_hash,previous_event_hash,created_at) VALUES(?,?,?,?,?)",(event_id,json.dumps(payload,sort_keys=True),event_hash,previous,utc_now()))
        con.commit()
    return {**payload,"Payload_Hash":payload_hash,"Previous_Event_Hash":previous,"Event_Hash":event_hash}


def all_events() -> List[Dict[str, Any]]:
    with connect() as con:
        rows=con.execute("SELECT * FROM provenance_events ORDER BY created_at ASC").fetchall()
    return [dict(r) for r in rows]


def event_hashes() -> List[str]: return [e["event_hash"] for e in all_events()]


def create_tree_head() -> Dict[str, Any]:
    hashes=event_hashes(); size=len(hashes); root=root_from_leaf_hashes(hashes)
    tree_id=f"STH-{size:08d}"
    payload={"tree_head_id":tree_id,"tree_size":size,"merkle_root":root}
    signed=canonical_json(payload).encode(); sig=sign_hybrid(signed)
    classical=sig["classical"]
    pq=sig["pqc"]
    with connect() as con:
        con.execute("INSERT OR REPLACE INTO tree_heads(tree_head_id,tree_size,merkle_root,signed_payload,classical_signature,classical_public_key,pq_signature,pq_public_key,signature_status,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",(tree_id,size,root,signed.decode(),classical["signature"],classical["public_key"],pq.get("signature"),pq.get("public_key_pem"),sig["status"],utc_now())); con.commit()
    return {**payload,"signed_payload":payload,"signature_status":sig["status"],"classical_signature":classical,"pqc_signature":pq}


def latest_tree_head() -> Dict[str, Any] | None:
    with connect() as con: row=con.execute("SELECT * FROM tree_heads ORDER BY tree_size DESC LIMIT 1").fetchone()
    return dict(row) if row else None


def inclusion_for_event(event_id: str, tree_size: int | None = None) -> Dict[str, Any]:
    hashes=event_hashes(); n=len(hashes)
    size=tree_size or n
    if size>n or size<=0: raise ValueError("invalid tree size")
    idx=next((i for i,h in enumerate(hashes[:size]) if h==next(e["event_hash"] for e in all_events() if e["event_id"]==event_id)),None)
    if idx is None: raise ValueError("event not in requested tree")
    return inclusion_proof_from_hashes([bytes.fromhex(h) for h in hashes[:size]],idx)


def consistency(old_size: int, new_size: int | None = None) -> Dict[str, Any]:
    events=all_events(); n=len(events); new_size=new_size or n
    if old_size<0 or new_size>n or old_size>new_size: raise ValueError("invalid tree sizes")
    return consistency_proof([bytes.fromhex(h) for h in [e["event_hash"] for e in events[:new_size]]],old_size)


def audit_chain() -> Dict[str, Any]:
    events=all_events(); valid=True; previous=""; hashes=[]; reasons=[]
    for e in events:
        payload=json.loads(e["payload_json"])
        expected_payload=sha256_json(payload)
        expected_event=sha256_bytes(canonical_json({"event_id":e["event_id"],"payload_hash":expected_payload,"previous_event_hash":previous}).encode())
        if e.get("previous_event_hash")!=previous: valid=False; reasons.append(f"previous hash mismatch at {e['event_id']}")
        if e.get("event_hash")!=expected_event: valid=False; reasons.append(f"event hash mismatch at {e['event_id']}")
        previous=e["event_hash"]; hashes.append(e["event_hash"])
    root=root_from_leaf_hashes(hashes)
    head=latest_tree_head()
    signature_valid=None; pq_signature_valid=None
    if head:
        signature_valid=verify_classical(head["signed_payload"].encode(),head["classical_signature"],head["classical_public_key"])
        if head.get("pq_signature") and head.get("pq_public_key"):
            pq_signature_valid=verify_mldsa(head["signed_payload"].encode(),head["pq_signature"],head["pq_public_key"])
        if head["tree_size"]>len(hashes) or (root != head["merkle_root"] and head["tree_size"]==len(hashes)): valid=False; reasons.append("tree head root mismatch")
    return {"event_count":len(events),"chain_valid":valid,"merkle_root":root,"latest_tree_head":head,"tree_head_classical_signature_valid":signature_valid,"tree_head_pq_signature_valid":pq_signature_valid,"reasons":reasons}
