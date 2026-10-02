from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app.services.utilities import now, generate_id, sha256_bytes
from backend.app.services.repository import init_db, count_records
from backend.app.services.records import create
from backend.app.services.claims import validate_claim, derived_claim_fields
from backend.app.services.verification import run_verification
from backend.app.services.provenance import append_event, create_tree_head, audit_chain
from backend.app.services.cbom import build_cbom
from backend.app.services.hndl import hndl_assessment
from backend.app.services.metrics import evaluate

DATA=ROOT/'data'/'synthetic'


def main():
    init_db()
    case=create('01_CASES',{'Case_Name':'DEMO - ECA-PQFA End-to-End','Case_Type':'SYNTHETIC_TEST','Description':'Controlled synthetic dataset only.','Research_Objective':'Exercise evidence -> claim -> verification -> provenance -> risk -> CBOM.','Created_By':'DEMO','Case_Status':'ACTIVE','Environment':'SYNTHETIC_LAB','Dataset_ID':'ECA-PQFA-SYNTH-001','Confidentiality_Level':'RESEARCH','Overall_Risk':'LOW','Migration_Status':'NOT_STARTED','Notes':'DEMO/SYNTHETIC - NOT A RESEARCH RESULT'})
    for name in ['lab_config.txt','test_vector.txt','tls_config.txt','statistics.csv']:
        p=DATA/name; data=p.read_bytes(); create('02_EVIDENCE',{'Case_ID':case['Case_ID'],'Evidence_Name':name,'Evidence_Type':'CONFIGURATION' if name.endswith('.txt') else 'DOCUMENT','Description':'Synthetic evidence artifact','Source_Type':'SYNTHETIC_DATASET','File_Name':name,'File_Type':p.suffix,'SHA256':sha256_bytes(data),'File_Size':len(data),'Evidence_Status':'VALIDATED','Integrity_Status':'VALID','Acquired_By':'DEMO','Acquisition_Method':'CONTROLLED_DATASET','Created_At':now()})
    claim={'Case_ID':case['Case_ID'],'Claim_Form':'ID','Claim_Statement':'Synthetic TLS configuration contains ML-KEM hybrid key establishment.','Target':'SYNTHETIC_TLS_CONFIG','Algorithm':'ML-KEM','Parameter_Set':'ML-KEM-768','Attack_Model':'IDENTIFICATION','Claimed_Scope':'C','Verified_Scope':'C','Origin':'HYBRID','Novelty_Status':'KNOWN'}
    assert validate_claim(claim)['valid']; claim=derived_claim_fields(claim); created=create('03_CLAIMS',claim)
    append_event({'Event_ID':generate_id('05_PROVENANCE',count_records('05_PROVENANCE')+1),'Case_ID':case['Case_ID'],'Object_Type':'03_CLAIMS','Object_ID':created['Claim_ID'],'Event_Type':'CLAIM_CREATED','Actor':'DEMO','Timestamp':now(),'Payload':created})
    v=run_verification(created,str(DATA/'tls_config.txt'),'deterministic-id-v1'); create('04_VERIFICATIONS',{'Claim_ID':created['Claim_ID'],'Case_ID':case['Case_ID'],'Verifier_ID':v['verifier_id'],'Verifier_Type':v['verifier_type'],'Verification_Method':v['method'],'Result':v['result'],'Verification_Scope':'C','Verifier_Environment':'LOCAL_SYNTHETIC','Operating_System':'demo','Software_Version':'ECA-PQFA-3.0','Analyst':'DEMO','Started_At':now(),'Completed_At':now(),'Independence_Status':'NOT_REQUIRED','Verifier_Notes':json.dumps(v)})
    head=create_tree_head(); audit=audit_chain(); cbom=build_cbom(str(DATA)); risk=hndl_assessment('HIGH','BOTH','2026-01-01','2026-10-02',10,'2028-01-01',10,15,20,1,0.8)
    metrics=evaluate([{'assurance_state':'L1','assessed':True,'refuted':False,'verified_scope':'C','scope_status':'SCOPE_MATCH','provenance_complete':True}],1)
    out={'case':case,'verification':v,'tree_head':{'tree_size':head['tree_size'],'merkle_root':head['merkle_root'],'signature_status':head['signature_status']},'audit':{'chain_valid':audit['chain_valid'],'classical_signature_valid':audit['tree_head_classical_signature_valid'],'pq_signature_valid':audit['tree_head_pq_signature_valid']},'cbom_summary':{'algorithms':[x.get('name') for x in cbom.get('components',[])]},'hndl':risk,'metrics':metrics,'status':'SYNTHETIC_DEMO_ONLY'}
    outpath=ROOT/'data'/'demo'/'demo_result.json'; outpath.parent.mkdir(exist_ok=True); outpath.write_text(json.dumps(out,indent=2))
    print(outpath)

if __name__=='__main__': main()
