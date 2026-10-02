from __future__ import annotations

from typing import Any, Dict, List
from backend.app.services.inventory import scan_directory


def build_cbom(path: str, recursive: bool = True) -> Dict[str, Any]:
    inv = scan_directory(path, recursive)
    components: List[Dict[str, Any]] = []
    for alg in inv["algorithms"] if isinstance(inv.get("algorithms"), list) else []:
        components.append({"type":"cryptographic-asset","bom-ref":f"crypto:{alg}","name":alg,"cryptoProperties":{"assetType":"algorithm","algorithmProperties":{"primitive":alg}}})
    return {
        "bomFormat":"CycloneDX","specVersion":"1.6","serialNumber":"urn:uuid:eca-pqfa-cbom","version":1,
        "metadata":{"tools":[{"vendor":"ECA-PQFA","name":"Cryptographic Inventory Engine","version":"3.0.0"}],"component": {"type":"application","name":"ECA-PQFA scanned environment"}},
        "components":components,
        "properties":[{"name":"eca-pqfa:source_directory","value":inv["metadata"]["source_directory"]},{"name":"eca-pqfa:asset_count","value":str(inv["metadata"]["asset_count"])}],
        "externalReferences":[{"type":"documentation","url":"https://cyclonedx.org/capabilities/cbom/"}],
        "eca_pqfa_files":inv.get("files",[])
    }
