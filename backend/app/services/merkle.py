from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Sequence, Tuple


def _sha(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def leaf_hash(data: bytes | str) -> bytes:
    if isinstance(data, str):
        data = data.encode()
    return _sha(b"\x00" + data)


def node_hash(left: bytes, right: bytes) -> bytes:
    return _sha(b"\x01" + left + right)


def _mth(items: Sequence[bytes]) -> bytes:
    n = len(items)
    if n == 0:
        return _sha(b"")
    if n == 1:
        return items[0]
    k = 1 << (n.bit_length() - 1)
    if k == n:
        k //= 2
    return node_hash(_mth(items[:k]), _mth(items[k:]))


def root_from_bytes(items: Sequence[bytes | str]) -> str:
    leaves = [leaf_hash(x) for x in items]
    return _mth(leaves).hex()


def root_from_leaf_hashes(hashes: Sequence[str]) -> str:
    return _mth([bytes.fromhex(h) for h in hashes]).hex() if hashes else _sha(b"").hex()


def inclusion_proof(items: Sequence[bytes | str], index: int) -> Dict[str, Any]:
    if not 0 <= index < len(items):
        raise IndexError("leaf index out of range")
    leaves = [leaf_hash(x) for x in items]
    return inclusion_proof_from_hashes(leaves, index)


def inclusion_proof_from_hashes(leaves: Sequence[bytes], index: int) -> Dict[str, Any]:
    if not 0 <= index < len(leaves):
        raise IndexError("leaf index out of range")
    path: List[Dict[str, str]] = []

    def walk(xs: Sequence[bytes], idx: int) -> bytes:
        n = len(xs)
        if n == 1:
            return xs[0]
        k = 1 << (n.bit_length() - 1)
        if k == n:
            k //= 2
        if idx < k:
            sibling = _mth(xs[k:])
            path.append({"direction": "right", "hash": sibling.hex()})
            return walk(xs[:k], idx)
        sibling = _mth(xs[:k])
        path.append({"direction": "left", "hash": sibling.hex()})
        return walk(xs[k:], idx - k)

    walk(leaves, index)
    root = _mth(leaves).hex()
    return {"leaf_index": index, "tree_size": len(leaves), "leaf_hash": leaves[index].hex(), "audit_path": list(reversed(path)), "root": root}


def verify_inclusion(leaf: bytes | str, proof: Dict[str, Any], expected_root: str) -> bool:
    # RFC 9162-style verification using the supplied tree index/size.
    h = leaf_hash(leaf)
    fn = int(proof.get("leaf_index", -1)); sn = int(proof.get("tree_size", 0)) - 1
    if fn < 0 or sn < fn:
        return False
    path = [bytes.fromhex(x["hash"]) if isinstance(x, dict) else bytes.fromhex(x) for x in proof.get("audit_path", [])]
    for p in path:
        if sn == 0:
            return False
        if (fn & 1) or fn == sn:
            h = node_hash(p, h)
            if not (fn & 1):
                while fn and not (fn & 1):
                    fn >>= 1; sn >>= 1
        else:
            h = node_hash(h, p)
        fn >>= 1; sn >>= 1
    return sn == 0 and h.hex() == expected_root.lower()


def _largest_power_less_than(n: int) -> int:
    if n <= 1:
        return 0
    return 1 << (n.bit_length() - 1) if (1 << (n.bit_length() - 1)) < n else 1 << (n.bit_length() - 2)


def _consistency_proof(m: int, n: int, leaves: Sequence[bytes], complete: bool) -> List[bytes]:
    # RFC 6962-style recursive consistency proof. The proof is represented as
    # subtree hashes, while the verifier reconstructs both roots from the prefix.
    if m == n:
        return [] if complete else [_mth(leaves[:n])]
    k = _largest_power_less_than(n)
    if m <= k:
        return _consistency_proof(m, k, leaves[:k], complete) + [_mth(leaves[k:n])]
    return _consistency_proof(m - k, n - k, leaves[k:n], False) + [_mth(leaves[:k])]


def consistency_proof(items: Sequence[bytes | str], old_size: int) -> Dict[str, Any]:
    leaves = [leaf_hash(x) for x in items]
    n = len(leaves)
    if not 0 <= old_size <= n:
        raise ValueError("old_size must be between 0 and tree size")
    if old_size == 0 or old_size == n:
        proof: List[str] = []
    else:
        proof = [h.hex() for h in _consistency_proof(old_size, n, leaves, True)]
    return {
        "old_size": old_size,
        "new_size": n,
        "old_root": _mth(leaves[:old_size]).hex() if old_size else _sha(b"").hex(),
        "new_root": _mth(leaves).hex() if n else _sha(b"").hex(),
        "proof": proof,
        "format": "RFC6962-subtree-hashes",
    }


def verify_consistency(old_size: int, new_size: int, old_root: str, new_root: str, proof_hex: Sequence[str]) -> bool:
    # RFC 9162 Section 2.1.4.2 verifier.
    if old_size <= 0 or old_size >= new_size or not proof_hex:
        return old_size == new_size and old_root.lower() == new_root.lower() and not proof_hex
    path=[bytes.fromhex(x) for x in proof_hex]
    if old_size & (old_size-1) == 0:
        path=[bytes.fromhex(old_root)]+path
    fn=old_size-1; sn=new_size-1
    while fn & 1:
        fn >>= 1; sn >>= 1
    fr=path[0]; sr=path[0]
    for c in path[1:]:
        if sn==0: return False
        if (fn & 1) or fn==sn:
            fr=node_hash(c,fr); sr=node_hash(c,sr)
            if not (fn & 1):
                while fn and not (fn & 1): fn >>= 1; sn >>= 1
        else:
            sr=node_hash(sr,c)
        fn >>= 1; sn >>= 1
    return sn==0 and fr.hex()==old_root.lower() and sr.hex()==new_root.lower()
