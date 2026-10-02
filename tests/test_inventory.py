from backend.app.services.inventory import scan_directory


def test_inventory_scan():
    result = scan_directory("data/synthetic", True)
    assert result["metadata"]["asset_count"] >= 2
    names = {c["name"] for c in result["components"]}
    assert "ML-KEM" in names
