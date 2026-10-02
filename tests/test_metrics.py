from backend.app.services.metrics import evaluate

def test_metrics():
    r=evaluate([{'assurance_state':'L1','assessed':True,'refuted':False,'verified_scope':'C','scope_status':'SCOPE_MATCH','provenance_complete':True},{'assurance_state':'L2','assessed':True,'refuted':True,'verified_scope':'B','scope_status':'SCOPE_INFLATION','provenance_complete':False}],2)
    assert r['VCR_1']==1.0 and r['FCCR']==0.5 and r['IRR']==0.5
