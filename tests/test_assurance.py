from backend.app.services.assurance import independence_check, promotion_check

def test_independence():
    a={"verifier_implementation":"a","hardware":"x"}; b={"verifier_implementation":"b","hardware":"y"}
    assert independence_check("EX",a,b)["independent"]

def test_promotion():
    c={"Claim_Form":"ID"}
    vs=[{"Result":"PASS","verifier_implementation":"a"},{"Result":"PASS","verifier_implementation":"b"}]
    assert promotion_check(c,vs)["L2"]
