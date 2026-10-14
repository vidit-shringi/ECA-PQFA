from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Sequence


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
    return _mth([leaf_hash(x) for x in items]).hex()


def root_from_leaf_hashes(hashes: Sequence[str]) -> str:
    try:
        raw = [bytes.fromhex(h) for h in hashes]
    except (TypeError, ValueError) as exc:
        raise ValueError("leaf hashes must be hexadecimal SHA-256 digests") from exc
    if any(len(x) != 32 for x in raw):
        raise ValueError("leaf hashes must be 32-byte SHA-256 digests")
    return _mth(raw).hex() if raw else _sha(b"").hex()


def inclusion_proof(items: Sequence[bytes | str], index: int) -> Dict[str, Any]:
    if not 0 <= index < len(items):
        raise IndexError("leaf index out of range")
    return inclusion_proof_from_hashes([leaf_hash(x) for x in items], index)


def inclusion_proof_from_hashes(leaves: Sequence[bytes], index: int) -> Dict[str, Any]:
    if not 0 <= index < len(leaves):
        raise IndexError("leaf index out of range")
    if any(len(x) != 32 for x in leaves):
        raise ValueError("leaves must contain 32-byte hashes")
    path: List[Dict[str, str]] = []

    def walk(xs: Sequence[bytes], idx: int) -> bytes:
        n = len(xs)
        if n == 1:
            return xs[0]
        k = 1 << (n.bit_length() - 1)
        if k == n:
            k //= 2
        if idx < k:
            path.append({"direction": "right", "hash": _mth(xs[k:]).hex()})
            return walk(xs[:k], idx)
        path.append({"direction": "left", "hash": _mth(xs[:k]).hex()})
        return walk(xs[k:], idx - k)

    walk(leaves, index)
    return {
        "leaf_index": index,
        "tree_size": len(leaves),
        "leaf_hash": leaves[index].hex(),
        "audit_path": list(reversed(path)),
        "root": _mth(leaves).hex(),
    }


def verify_inclusion(leaf: bytes | str, proof: Dict[str, Any], expected_root: str) -> bool:
    """Verify a proof for an original leaf value (the function hashes it once)."""
    try:
        if not isinstance(proof, dict):
            return False
        index = int(proof.get("leaf_index", -1))
        size = int(proof.get("tree_size", 0))
        if size <= 0 or index < 0 or index >= size or len(expected_root) != 64:
            return False
        path = proof.get("audit_path", [])
        if not isinstance(path, list):
            return False
        siblings = []
        for item in path:
            hex_digest = item.get("hash") if isinstance(item, dict) else item
            digest = bytes.fromhex(hex_digest)
            if len(digest) != 32:
                return False
            siblings.append((item.get("direction") if isinstance(item, dict) else None, digest))
        h = leaf_hash(leaf)
        fn, sn = index, size - 1
        for direction, sibling in siblings:
            if sn == 0:
                return False
            if direction == "left":
                h = node_hash(sibling, h)
            elif direction == "right":
                h = node_hash(h, sibling)
            elif direction is None:
                if (fn & 1) or fn == sn:
                    h = node_hash(sibling, h)
                    if not (fn & 1):
                        while fn and not (fn & 1):
                            fn >>= 1
                            sn >>= 1
                else:
                    h = node_hash(h, sibling)
            else:
                return False
            fn >>= 1
            sn >>= 1
        return sn == 0 and h.hex() == expected_root.lower()
    except (TypeError, ValueError, KeyError, OverflowError):
        return False


def _largest_power_less_than(n: int) -> int:
    if n <= 1:
        return 0
    p = 1 << (n.bit_length() - 1)
    return p if p < n else p >> 1


def _consistency_proof(m: int, n: int, leaves: Sequence[bytes], complete: bool) -> List[bytes]:
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
    proof = [] if old_size in (0, n) else [h.hex() for h in _consistency_proof(old_size, n, leaves, True)]
    return {
        "old_size": old_size,
        "new_size": n,
        "old_root": _mth(leaves[:old_size]).hex() if old_size else _sha(b"").hex(),
        "new_root": _mth(leaves).hex() if n else _sha(b"").hex(),
        "proof": proof,
        "format": "RFC6962-subtree-hashes",
    }


def verify_consistency(old_size: int, new_size: int, old_root: str, new_root: str, proof_hex: Sequence[str]) -> bool:
    try:
        if old_size < 0 or new_size < old_size or len(old_root) != 64 or len(new_root) != 64:
            return False
        if old_size == 0:
            return not proof_hex and old_root.lower() == _sha(b"").hex() and (new_size == 0 or new_root.lower() != "")
        if old_size == new_size:
            return not proof_hex and old_root.lower() == new_root.lower()
        if old_size > new_size or not proof_hex:
            return False
        path = [bytes.fromhex(x) for x in proof_hex]
        if any(len(x) != 32 for x in path):
            return False
        if old_size & (old_size - 1) == 0:
            path = [bytes.fromhex(old_root)] + path
        fn, sn = old_size - 1, new_size - 1
        while fn & 1:
            fn >>= 1
            sn >>= 1
        fr = sr = path[0]
        for c in path[1:]:
            if sn == 0:
                return False
            if (fn & 1) or fn == sn:
                fr = node_hash(c, fr)
                sr = node_hash(c, sr)
                if not (fn & 1):
                    while fn and not (fn & 1):
                        fn >>= 1
                        sn >>= 1
            else:
                sr = node_hash(sr, c)
            fn >>= 1
            sn >>= 1
        return sn == 0 and fr.hex() == old_root.lower() and sr.hex() == new_root.lower()
    except (TypeError, ValueError, IndexError):
        return False
