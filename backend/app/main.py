from __future__ import annotations
import hashlib, json, os
from pathlib import Path
from typing import Any, Dict
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings, EVIDENCE_ROOT
from backend.app.core.schema import SHEETS
from backend.app.core.models import ClaimRequest, EvidenceFileRequest, HNDLRequest, InventoryRequest, RecordRequest, RelationshipRequest, UpdateRequest
from backend.app.services.claims import derived_claim_fields, validate_claim
from backend.app.services.hndl import hndl_assessment
from backend.app.services.inventory import scan_directory
from backend.app.services.cbom import build_cbom
from backend.app.services.verification import run_verification
from backend.app.services.assurance import promotion_check
from backend.app.services.provenance import append_event, audit_chain, create_tree_head, inclusion_for_event, consistency
from backend.app.services.records import create, delete, get, list_, update
from backend.app.services.repository import count_records, init_db, connect, utc_now
from backend.app.services.utilities import ID_FIELDS, generate_id, now
from backend.app.services.sheets import SheetsClient
from backend.app.services.metrics import evaluate
from backend.app.security.auth import require_api_key
from backend.app.security.paths import safe_path

ROOT=Path(__file__).resolve().parents[2]
FRONTEND=ROOT/"frontend"

app=FastAPI(title=settings.app_name,version=settings.version,description="Evidence-Carrying AI-Assisted Cryptanalysis and Post-Quantum Forensic Assurance research tool and reference implementation.")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.allowed_origins.split(',') if x.strip()], allow_credentials=False, allow_methods=["GET","POST","PATCH","DELETE"], allow_headers=["*"])

@app.on_event("startup")
def startup(): init_db(); EVIDENCE_ROOT.mkdir(parents=True,exist_ok=True)

@app.middleware("http")
async def security_headers(request, call_next):
    response=await call_next(request)
    response.headers["X-Content-Type-Options"]="nosniff"; response.headers["X-Frame-Options"]="DENY"; response.headers["Referrer-Policy"]="no-referrer"; response.headers["Cache-Control"]="no-store"
    return response

@app.get("/",include_in_schema=False)
def root(): return FileResponse(FRONTEND/"index.html")
app.mount("/static",StaticFiles(directory=FRONTEND),name="static")

@app.get("/api/health")
def health():
    return {"ok":True,"service":settings.app_name,"version":settings.version,"pqc_signing":"optional-ML-DSA","api_auth_required":settings.require_api_key,"timestamp":now()}

@app.get("/api/config")
def config(): return {"spreadsheet_id":settings.spreadsheet_id,"apps_script_url_configured":bool(settings.apps_script_url),"sheets":list(SHEETS.keys()),"evidence_root":str(EVIDENCE_ROOT),"security_mode":"API_KEY" if settings.require_api_key else "LOCAL_DEMO"}

@app.get("/api/dashboard")
def dashboard():
    claims=list_("03_CLAIMS",10000,0); assets=list_("06_ASSETS",10000,0); migrations=list_("12_MIGRATION",10000,0); audits=list_("14_AUDIT_LOG",10000,0)
    return {"Total_Cases":count_records("01_CASES"),"Total_Evidence_Objects":count_records("02_EVIDENCE"),"Total_Claims":len(claims),"L0_Claims":sum(str(r.get("L0","")).upper()=="TRUE" for r in claims),"L1_Claims":sum(str(r.get("L1","")).upper()=="TRUE" for r in claims),"L2_Claims":sum(str(r.get("L2","")).upper()=="TRUE" for r in claims),"L3_Claims":sum(str(r.get("L3","")).upper()=="TRUE" for r in claims),"Refuted_Claims":sum(str(r.get("Refuted","")).upper()=="TRUE" for r in claims),"High_Risk_Assets":sum(str(r.get("HNDL_Risk","")).upper() in {"HIGH","CRITICAL"} for r in assets),"Critical_Risk_Assets":sum(str(r.get("HNDL_Risk","")).upper()=="CRITICAL" for r in assets),"Migration_Issues":sum(str(r.get("Migration_Status","")).upper() in {"FAILED","PARTIAL"} for r in migrations),"Failed_Audits":sum(str(r.get("Result","")).upper()=="FAIL" for r in audits),"Total_Experiments":count_records("13_EXPERIMENTS"),"Provenance_Events":len(__import__('backend.app.services.provenance',fromlist=['all_events']).all_events())}

@app.get("/api/sheets")
def sheets(): return [{"name":k,"id_field":ID_FIELDS[k],"columns":v} for k,v in SHEETS.items()]

@app.get("/api/records/{sheet}")
def get_records(sheet:str,limit:int=Query(100,ge=1,le=1000),offset:int=Query(0,ge=0)):
    if sheet not in SHEETS: raise HTTPException(400,"Unsupported sheet")
    return {"sheet":sheet,"records":list_(sheet,limit,offset)}

@app.get("/api/records/{sheet}/{record_id}")
def get_one(sheet:str,record_id:str):
    try:return get(sheet,record_id)
    except KeyError:raise HTTPException(404,"Record not found")

@app.post("/api/records",dependencies=[Depends(require_api_key)])
def create_record(req:RecordRequest):
    try:
        result=create(req.sheet,req.record); append_event({"Event_ID":generate_id("05_PROVENANCE",count_records("05_PROVENANCE")+1),"Case_ID":result.get("Case_ID",""),"Object_Type":req.sheet,"Object_ID":result.get(ID_FIELDS.get(req.sheet,""),""),"Event_Type":"RECORD_CREATED","Actor":"Research Engine","Timestamp":now(),"Payload":result}); return result
    except Exception as exc: raise HTTPException(400,str(exc))

@app.patch("/api/records",dependencies=[Depends(require_api_key)])
def update_record(req:UpdateRequest):
    try:
        result=update(req.sheet,req.id_value,req.patch); append_event({"Event_ID":generate_id("05_PROVENANCE",count_records("05_PROVENANCE")+1),"Case_ID":result.get("Case_ID","") if result else "","Object_Type":req.sheet,"Object_ID":req.id_value,"Event_Type":"RECORD_UPDATED","Actor":"Research Engine","Timestamp":now(),"Payload":req.patch}); return result
    except KeyError: raise HTTPException(404,"Record not found")
    except Exception as exc: raise HTTPException(400,str(exc))

@app.delete("/api/records/{sheet}/{record_id}",dependencies=[Depends(require_api_key)])
def delete_record(sheet:str,record_id:str):
    try: delete(sheet,record_id)
    except KeyError: raise HTTPException(404,"Record not found")
    append_event({"Event_ID":generate_id("05_PROVENANCE",count_records("05_PROVENANCE")+1),"Object_Type":sheet,"Object_ID":record_id,"Event_Type":"RECORD_DELETED","Actor":"Research Engine","Timestamp":now()})
    return {"deleted":True,"sheet":sheet,"record_id":record_id}

@app.post("/api/claims/validate")
def claim_validate(req:ClaimRequest): return validate_claim(req.model_dump())

@app.post("/api/claims",dependencies=[Depends(require_api_key)])
def claim_create(req:ClaimRequest):
    payload=req.model_dump(); result=validate_claim(payload)
    if not result["valid"]: raise HTTPException(400,result)
    record={"Case_ID":payload["case_id"],"Claim_Form":payload["claim_form"],"Claim_Statement":payload["claim_statement"],"Target":payload["target"],"Algorithm":payload["algorithm"],"Parameter_Set":payload["parameter_set"],"Attack_Model":payload["attack_model"],"Claimed_Scope":payload["claimed_scope"],"Verified_Scope":payload["verified_scope"],"Origin":payload["origin"],"Novelty_Status":payload["novelty_status"],"Evidence_ID":payload["evidence_id"],"Witness_ID":payload["witness_id"],"Verification_ID":payload["verification_id"],"Created_By":"ECA-PQFA Research Engine"}
    record=derived_claim_fields(record); created=create("03_CLAIMS",record)
    append_event({"Event_ID":generate_id("05_PROVENANCE",count_records("05_PROVENANCE")+1),"Case_ID":created["Case_ID"],"Object_Type":"03_CLAIMS","Object_ID":created["Claim_ID"],"Event_Type":"CLAIM_CREATED","Actor":"Research Engine","Timestamp":now(),"Payload":created})
    return created

@app.post("/api/evidence/hash")
def hash_evidence(req:EvidenceFileRequest):
    p=safe_path(req.path)
    if not p.exists() or not p.is_file(): raise HTTPException(400,"Evidence file not found")
    data=p.read_bytes(); return {"path":str(p),"file_name":p.name,"file_size":len(data),"sha256":hashlib.sha256(data).hexdigest(),"sha3_256":hashlib.sha3_256(data).hexdigest()}

@app.post("/api/inventory/scan")
def inventory(req:InventoryRequest):
    try:return scan_directory(str(safe_path(req.path)),req.recursive)
    except FileNotFoundError as exc:raise HTTPException(400,str(exc))

@app.post("/api/inventory/cbom")
def cbom(req:InventoryRequest):
    try:return build_cbom(str(safe_path(req.path)),req.recursive)
    except FileNotFoundError as exc:raise HTTPException(400,str(exc))

@app.post("/api/hndl/calculate")
def calculate_hndl(req:HNDLRequest): return hndl_assessment(**req.model_dump())

@app.post("/api/verification/run",dependencies=[Depends(require_api_key)])
def verification_run(body:Dict[str,Any]):
    try:path=body.get("evidence_path",body.get("path","")); return run_verification(body.get("claim",body),str(safe_path(path)) if path else "",body.get("verifier_id","deterministic-v1"))
    except FileNotFoundError as exc: raise HTTPException(400,str(exc))

@app.post("/api/verification/promote",dependencies=[Depends(require_api_key)])
def verification_promote(body:Dict[str,Any]): return promotion_check(body.get("claim",{}),body.get("verifications",[]),bool(body.get("formal_proof_artifact")),bool(body.get("human_review")))

@app.get("/api/provenance/audit")
def provenance_audit(): return audit_chain()

@app.post("/api/provenance/event",dependencies=[Depends(require_api_key)])
def provenance_event(body:Dict[str,Any]):
    payload=dict(body); payload.setdefault("Event_ID",generate_id("05_PROVENANCE",count_records("05_PROVENANCE")+1)); payload.setdefault("Timestamp",now()); return append_event(payload)

@app.post("/api/provenance/tree-head",dependencies=[Depends(require_api_key)])
def provenance_tree_head(): return create_tree_head()

@app.get("/api/provenance/inclusion/{event_id}")
def provenance_inclusion(event_id:str,tree_size:int|None=None):
    try:return inclusion_for_event(event_id,tree_size)
    except Exception as exc: raise HTTPException(400,str(exc))

@app.get("/api/provenance/consistency")
def provenance_consistency(old_size:int=Query(...,ge=0),new_size:int|None=None):
    try:return consistency(old_size,new_size)
    except Exception as exc: raise HTTPException(400,str(exc))

@app.get("/api/provenance/verify-inclusion")
def verify_inclusion_endpoint(event_id:str,tree_size:int|None=None):
    from backend.app.services.provenance import inclusion_for_event,event_hashes
    from backend.app.services.merkle import verify_inclusion,root_from_leaf_hashes
    try:
        proof=inclusion_for_event(event_id,tree_size); hashes=event_hashes()[:proof["tree_size"]]; root=root_from_leaf_hashes(hashes); return {"valid":verify_inclusion(bytes.fromhex(proof["leaf_hash"]),proof,root),"proof":proof,"root":root}
    except Exception as exc: raise HTTPException(400,str(exc))

@app.get("/api/graph")
def graph_data():
    records=list_("10_DIGITAL_TWIN",10000,0); nodes={}; edges=[]
    for r in records:
        s=(r.get("Source_ID"),r.get("Source_Type")); t=(r.get("Target_ID"),r.get("Target_Type")); nodes[str(s)]={"id":s[0],"type":s[1]}; nodes[str(t)]={"id":t[0],"type":t[1]}; edges.append({"source":s[0],"target":t[0],"relationship":r.get("Relationship"),"assurance_level":r.get("Assurance_Level")})
    return {"nodes":list(nodes.values()),"edges":edges}

@app.post("/api/relationship",dependencies=[Depends(require_api_key)])
def create_relationship(req:RelationshipRequest):
    return create("10_DIGITAL_TWIN",{"Case_ID":req.case_id,"Source_ID":req.source_id,"Source_Type":req.source_type,"Relationship":req.relationship,"Target_ID":req.target_id,"Target_Type":req.target_type,"Assurance_Level":req.assurance_level,"Evidence_ID":req.evidence_id,"Claim_ID":req.claim_id,"Created_At":now(),"Status":req.status,"Notes":req.notes})

@app.post("/api/sheets/health",dependencies=[Depends(require_api_key)])
def sheets_health():
    try:return SheetsClient().health()
    except Exception as exc: raise HTTPException(502,f"Google Sheets bridge error: {exc}")

@app.post("/api/sheets/sync",dependencies=[Depends(require_api_key)])
def sheets_sync(body:Dict[str,Any]):
    sheet=body.get("sheet"); record=body.get("record",{})
    if sheet not in SHEETS: raise HTTPException(400,"Unsupported sheet")
    try:return SheetsClient().sync_record(sheet,record)
    except Exception as exc: raise HTTPException(502,f"Google Sheets bridge error: {exc}")

@app.post("/api/experiments/evaluate",dependencies=[Depends(require_api_key)])
def evaluate_experiment(body:Dict[str,Any]):
    return evaluate(body.get("records",[]),body.get("generated_count"))

@app.post("/api/cases/demo",dependencies=[Depends(require_api_key)])
def demo_case():
    record={"Case_Name":"DEMO - ECA-PQFA Synthetic Validation","Case_Type":"SYNTHETIC_TEST","Description":"Synthetic development record only.","Research_Objective":"Validate the complete end-to-end research-tool workflow.","Created_By":"DEMO","Case_Status":"ACTIVE","Environment":"SYNTHETIC_LAB","Dataset_ID":"DEMO-DATASET-001","Confidentiality_Level":"RESEARCH","Overall_Risk":"LOW","Migration_Status":"NOT_STARTED","Evidence_Count":0,"Claim_Count":0,"Notes":"DEMO/SYNTHETIC - NOT A RESEARCH RESULT"}
    return create("01_CASES",record)
