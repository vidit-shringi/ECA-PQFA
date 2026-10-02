from __future__ import annotations
from typing import Any, Dict, Set

ERROR_PROPAGATION={
    "EX":{"verifier_implementation","hardware"},
    "ST":{"code_base","data_source","model_family","hardware"},
    "CX":{"verifier_implementation","analyst_organization"},
    "PD":{"verifier_implementation","analyst_organization"},
    "IM":{"hardware_device","code_base"},
    "PR":{"verifier_implementation","analyst_organization"},
    "NG":{"model_family","data_source"},
    "ID":{"verifier_implementation"},
}

def independence_check(claim_form:str, first:Dict[str,Any], second:Dict[str,Any])->Dict[str,Any]:
    dims=ERROR_PROPAGATION.get(claim_form.upper(),set())
    differences={d:first.get(d)!=second.get(d) for d in dims}
    ok=bool(dims) and all(differences.values())
    return {"claim_form":claim_form,"required_dimensions":sorted(dims),"differences":differences,"independent":ok}

def promotion_check(claim:Dict[str,Any], verifications:list[Dict[str,Any]], formal:bool=False, human_review:bool=False)->Dict[str,Any]:
    form=str(claim.get("Claim_Form","")).upper()
    passed=[v for v in verifications if str(v.get("Result",v.get("result",""))).upper()=="PASS"]
    l1=len(passed)>=1
    l2=False
    independence=None
    if len(passed)>=2:
        independence=independence_check(form,passed[0],passed[1]); l2=independence["independent"]
    l3=bool(formal and human_review)
    return {"L0":True,"L1":l1,"L2":l2,"L3":l3,"assurance_state":"L3" if l3 else "L2" if l2 else "L1" if l1 else "L0","promotion_reasons":{"L1":"accepted verifier" if l1 else "requires PASS verification","L2":"phi-independent second acceptance" if l2 else "requires phi-independent second acceptance","L3":"proof artifact + human adequacy review" if l3 else "not auto-promoted"},"independence":independence}
