import re
from backend.app.services.cbom import build_cbom


def test_cbom_uuid_and_no_undeclared_file_key(tmp_path):
    (tmp_path / "alg.txt").write_text("ML-KEM-768", encoding="utf-8")
    result = build_cbom(str(tmp_path))
    assert re.fullmatch(r"urn:uuid:[0-9a-fA-F-]{36}", result["serialNumber"])
    assert "eca_pqfa_files" not in result
    assert result["components"]
