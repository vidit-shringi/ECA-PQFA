from __future__ import annotations

import uuid
from typing import Any, Dict, List
from backend.app.services.inventory import scan_directory


def build_cbom(path: str, recursive: bool = True) -> Dict[str, Any]:
    inv = scan_directory(path, recursive)
    components: List[Dict[str, Any]] = []
    for alg in inv.get("algorithms", []):
        components.append({
            "type": "cryptographic-asset",
            "bom-ref": f"crypto:{alg}",
            "name": alg,
            "cryptoProperties": {
                "assetType": "algorithm",
                "algorithmProperties": {"primitive": alg},
            },
        })
    # Keep non-CycloneDX file metadata inside declared properties rather than
    # introducing an unrecognized top-level extension key.
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "tools": [{"vendor": "ECA-PQFA", "name": "Cryptographic Inventory Engine", "version": "3.2.0"}],
            "component": {"type": "application", "name": "ECA-PQFA scanned environment"},
        },
        "components": components,
        "properties": [
            {"name": "eca-pqfa:source_directory", "value": inv["metadata"]["source_directory"]},
            {"name": "eca-pqfa:asset_count", "value": str(inv["metadata"]["asset_count"])},
            {"name": "eca-pqfa:scanned_files_json", "value": __import__("json").dumps(inv.get("files", []), sort_keys=True)},
        ],
        "externalReferences": [{"type": "documentation", "url": "https://cyclonedx.org/capabilities/cbom/"}],
    }
