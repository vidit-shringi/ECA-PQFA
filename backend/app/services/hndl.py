from __future__ import annotations
from datetime import date
from typing import Dict

SENSITIVITY={"LOW":0.25,"MEDIUM":0.5,"HIGH":0.75,"CRITICAL":1.0}

def years_between(a:date,b:date)->float:return max(0.0,(b-a).days/365.25)

def break_cdf(t_years:float, optimistic:float, median:float, pessimistic:float)->float:
    """Transparent three-quantile CDF approximation for the current research-tool implementation.
    optimistic/median/pessimistic are treated as the 0.1/0.5/0.9 quantiles.
    """
    qs=sorted([(max(0.0,optimistic),0.1),(max(0.0,median),0.5),(max(0.0,pessimistic),0.9)])
    if t_years<=qs[0][0]: return 0.0
    for (x1,p1),(x2,p2) in zip(qs,qs[1:]):
        if t_years<=x2:
            if x2==x1:return p2
            return p1+(p2-p1)*(t_years-x1)/(x2-x1)
    return 1.0

def hndl_assessment(sensitivity:str,exposure_type:str,capture_date:str,current_date:str,confidentiality_lifetime_years:float,migration_date:str,optimistic_crqc_years:float,median_crqc_years:float,pessimistic_crqc_years:float,data_generation_rate:float=1.0,exposure_probability:float=1.0)->Dict[str,object]:
    """Current implementation of the paper's retrospective/prospective split.

    R_ret = S * e * Pr[Z <= t_c + L]
    R_pro = S * integral(current..migration) lambda_f(t) Pr[Z <= t + L] dt

    For the API's date-only implementation, time is measured in years relative to the
    capture/current date. The prospective integral uses a constant lambda_f.
    Outputs are expected sensitivity-weighted exposure quantities, not probabilities.
    """
    s=SENSITIVITY.get(sensitivity.upper(),0.5)
    cap=date.fromisoformat(capture_date); cur=date.fromisoformat(current_date); mig=date.fromisoformat(migration_date)
    age=years_between(cap,cur); horizon=age+max(0.0,confidentiality_lifetime_years)
    scenarios={"optimistic":optimistic_crqc_years,"median":median_crqc_years,"pessimistic":pessimistic_crqc_years}
    exposure_probability=max(0.0,min(1.0,float(exposure_probability)))
    ret={}
    for label,break_years in scenarios.items():
        ret[label]=round(s*exposure_probability*(1.0 if horizon >= break_years else 0.0),6)
    distributional_ret=round(s*exposure_probability*break_cdf(horizon,optimistic_crqc_years,median_crqc_years,pessimistic_crqc_years),6)
    migration_years=years_between(cur,mig)
    steps=120
    if exposure_type.upper() not in {"PROSPECTIVE","BOTH"}: prospective={k:0.0 for k in scenarios}
    else:
        prospective={}
        for label in scenarios:
            if migration_years<=0: integral=0.0
            else:
                dt=migration_years/steps; integral=0.0
                for j in range(steps):
                    t=(j+0.5)*dt
                    # t is years from current time; L is future confidentiality from capture.
                    cdf=1.0 if (age+t+confidentiality_lifetime_years) >= scenarios[label] else 0.0
                    integral += data_generation_rate*cdf*dt
            prospective[label]=round(s*integral,6)
    # For retrospective-only artifacts, prospective exposure is zero; for ongoing flows,
    # migration time controls only prospective exposure as required by the model.
    if exposure_type.upper() in {"RETROSPECTIVE","BOTH"}: ret_component=ret["median"]
    else: ret_component=0.0
    if exposure_type.upper() in {"PROSPECTIVE","BOTH"}: pro_component=prospective["median"]
    else: pro_component=0.0
    combined=round(ret_component+pro_component,6)
    band="CRITICAL" if combined>=1.5 else "HIGH" if combined>=0.75 else "MEDIUM" if combined>=0.25 else "LOW"
    return {"method":"ECA-PQFA HNDL two-component implementation v3.1","interpretation":"Expected sensitivity-weighted exposure quantity; not a probability and not a security guarantee.","retrospective_risk":round(ret_component,6),"prospective_risk":round(pro_component,6),"combined_score":combined,"risk_band":band,"sensitivity_weight":s,"exposure_probability":exposure_probability,"capture_age_years":round(age,4),"confidentiality_horizon_years":round(horizon,4),"migration_window_years":round(migration_years,4),"retrospective_scenarios":ret,"prospective_scenarios":prospective,"distributional_retrospective_median_curve":distributional_ret,"cdf_quantile_convention":{"optimistic":0.1,"median":0.5,"pessimistic":0.9},"warning":"The paper requires calibrated Pr[Z<=t] distributions, elicited sensitivity S and measured/estimated exposure e/lambda. The tool exposes deterministic optimistic/median/pessimistic scenario horizons plus a piecewise distributional curve; validate/calibrate before reporting scientific results."}
