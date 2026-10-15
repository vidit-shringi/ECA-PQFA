from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List

from backend.app.services.inventory import scan_directory


def build_cbom(path: str, recursive: bool = True) -> Dict[str, Any]:
    inv = scan_directory(path, recursive)
    components: List[Dict[str, Any]] = []
    for alg in inv.get("algorithms", []) if isinstance(inv.get("algorithms"), list) else []:
        components.append({
            "type": "cryptographic-asset",
            "bom-ref": f"crypto:{alg}",
            "name": alg,
            "cryptoProperties": {
                "assetType": "algorithm",
                "algorithmProperties": {"primitive": alg},
            },
        })
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "tools": [{"vendor": "ECA-PQFA", "name": "Cryptographic Inventory Engine", "version": "3.2.0"}],
            "component": {"type": "application", "name": "ECA-PQFA scanned environment"},
            "properties": [
                {"name": "eca-pqfa:source_directory", "value": str(inv.get("metadata", {}).get("source_directory", ""))},
                {"name": "eca-pqfa:asset_count", "value": str(inv.get("metadata", {}).get("asset_count", 0))},
                {"name": "eca-pqfa:files-json", "value": json.dumps(inv.get("files", []), sort_keys=True)},
            ],
        },
        "components": components,
        "externalReferences": [{"type": "documentation", "url": "https://cyclonedx.org/capabilities/cbom/"}],
    }
