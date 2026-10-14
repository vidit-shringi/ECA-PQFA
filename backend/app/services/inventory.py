from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

from backend.app.services.utilities import sha256_bytes, sha3_256_bytes

PATTERNS = {
    "RSA": [rb"\bRSA\b", rb"rsaEncryption", rb"1\.2\.840\.113549\.1\.1"],
    "ECDSA": [rb"\bECDSA\b", rb"ecdsa-with-SHA"],
    "X25519": [rb"\bX25519\b", rb"1\.3\.101\.110"],
    "Ed25519": [rb"\bEd25519\b", rb"1\.3\.101\.112"],
    "ML-KEM": [rb"\bML[- ]KEM\b", rb"MLKEM(?:512|768|1024)", rb"\bKyber\b"],
    "ML-DSA": [rb"\bML[- ]DSA\b", rb"MLDSA(?:44|65|87)", rb"\bDilithium\b"],
    "SLH-DSA": [rb"\bSLH[- ]DSA\b", rb"SPHINCS"],
    "AES": [rb"\bAES(?:-128|-192|-256)?\b"],
    "ChaCha20": [rb"\bChaCha20\b", rb"CHACHA20-POLY1305"],
    "SHA-2": [rb"\bSHA[- ]?256\b", rb"\bSHA[- ]?384\b", rb"\bSHA[- ]?512\b"],
    "SHA-3": [rb"\bSHA3[- ]?256\b", rb"\bSHA3[- ]?384\b", rb"\bSHA3[- ]?512\b"],
    "MD5": [rb"\bMD5\b"],
    "SHA-1": [rb"\bSHA[- ]?1\b"],
}


def detect_algorithms(data: bytes) -> List[str]:
    hits = []
    for name, patterns in PATTERNS.items():
        if any(re.search(pattern, data, re.IGNORECASE) for pattern in patterns):
            hits.append(name)
    return hits


def scan_directory(path: str, recursive: bool = True) -> Dict[str, object]:
    base = Path(path).expanduser().resolve()
    if not base.exists() or not base.is_dir():
        raise FileNotFoundError(base)
    iterator = base.rglob("*") if recursive else base.glob("*")
    assets = []
    algorithms = set()
    skipped_symlinks = 0
    for candidate in iterator:
        try:
            resolved = candidate.resolve(strict=True)
            # Do not let an in-root symlink cause reads outside the approved scan root.
            if resolved != base and base not in resolved.parents:
                skipped_symlinks += 1
                continue
            if not resolved.is_file():
                continue
            data = resolved.read_bytes()
        except (OSError, RuntimeError):
            skipped_symlinks += 1
            continue
        detected = detect_algorithms(data)
        algorithms.update(detected)
        assets.append({
            "file_name": candidate.name,
            "relative_path": str(candidate.relative_to(base)),
            "size": len(data),
            "sha256": sha256_bytes(data),
            "sha3_256": sha3_256_bytes(data),
            "algorithms_detected": detected,
        })
    warnings = ["String/OID scanning is an identification aid, not proof of implementation correctness or security."]
    if skipped_symlinks:
        warnings.append(f"Skipped {skipped_symlinks} unreadable, dangling, or out-of-root symlink path(s).")
    return {
        "metadata": {"source_directory": str(base), "asset_count": len(assets)},
        "algorithms": sorted(algorithms),
        "components": [
            {"type": "cryptographic-algorithm", "name": algorithm,
             "properties": [{"name": "detection", "value": "string/OID pattern"}]}
            for algorithm in sorted(algorithms)
        ],
        "files": assets,
        "warnings": warnings,
    }
