from backend.app.services.inventory import scan_directory
from pathlib import Path


def test_inventory_scan():
    result = scan_directory("data/synthetic", True)
    assert result["metadata"]["asset_count"] >= 2
    names = {component["name"] for component in result["components"]}
    assert "ML-KEM" in names


def test_inventory_skips_symlink_escape(tmp_path: Path):
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("RSA AES", encoding="utf-8")
    link = root / "outside-link.txt"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        return
    result = scan_directory(str(root), True)
    assert result["metadata"]["asset_count"] == 0
    assert any("out-of-root symlink" in warning for warning in result["warnings"])
