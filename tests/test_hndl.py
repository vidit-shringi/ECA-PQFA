from backend.app.services.hndl import hndl_assessment

def test_hndl_split_and_bounds():
    r=hndl_assessment('HIGH','BOTH','2026-01-01','2026-10-01',10,'2028-01-01',10,15,20,1,0.5)
    assert r['retrospective_risk'] >= 0
    assert r['prospective_risk'] >= 0
    assert 0 <= r['exposure_probability'] <= 1
