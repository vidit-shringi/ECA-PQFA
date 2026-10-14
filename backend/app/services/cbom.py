from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List

from backend.app.services.inventory import scan_directory


PRIMITIVE_BY_ALGORITHM = {
    "RSA": "pke",
    "ECDSA": "signature",
    "X25519": "key-agree",
    "Ed25519": "signature",
    "ML-KEM": "kem",
    "ML-DSA": "signature",
    "SLH-DSA": "signature",
    "AES": "block-cipher",
    "ChaCha20": "stream-cipher",
    "SHA-2": "hash",
    "SHA-3": "hash",
    "MD5": "hash",
    "SHA-1": "hash",
}


def build_cbom(path: str, recursive: bool = True) -> Dict[str, Any]:
    inv = scan_directory(path, recursive)
    components: List[Dict[str, Any]] = []
    for algorithm in inv.get("algorithms", []):
        components.append({
            "type": "cryptographic-asset",
            "bom-ref": f"crypto:{algorithm}",
            "name": algorithm,
            "cryptoProperties": {
                "assetType": "algorithm",
                "algorithmProperties": {
                    # CycloneDX primitive is a category enum, not an algorithm name.
                    "primitive": PRIMITIVE_BY_ALGORITHM.get(algorithm, "unknown"),
                },
            },
        })
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "tools": [{"vendor": "ECA-PQFA", "name": "Cryptographic Inventory Engine", "version": "3.2.1"}],
            "component": {"type": "application", "name": "ECA-PQFA scanned environment"},
        },
        "components": components,
        "properties": [
            {"name": "eca-pqfa:source_directory", "value": inv["metadata"]["source_directory"]},
            {"name": "eca-pqfa:asset_count", "value": str(inv["metadata"]["asset_count"])},
            {"name": "eca-pqfa:scanned_files_json", "value": json.dumps(inv.get("files", []), sort_keys=True)},
        ],
        "externalReferences": [{"type": "documentation", "url": "https://cyclonedx.org/capabilities/cbom/"}],
    }
