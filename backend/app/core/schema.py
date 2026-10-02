from __future__ import annotations

SHEETS = {
    "01_CASES": [
        "Case_ID","Case_Name","Case_Type","Description","Research_Objective",
        "Created_At","Created_By","Case_Status","Environment","Dataset_ID",
        "Confidentiality_Level","Overall_Risk","Migration_Status",
        "Evidence_Count","Claim_Count","Last_Updated","Notes"
    ],
    "02_EVIDENCE": [
        "Evidence_ID","Case_ID","Evidence_Name","Evidence_Type","Description",
        "Source_Type","File_Name","File_Type","Drive_File_ID","Drive_URL",
        "SHA256","SHA3_256","File_Size","Acquired_At","Acquired_By",
        "Acquisition_Method","Evidence_Status","Integrity_Status",
        "Chain_of_Custody_ID","Parent_Evidence_ID","Created_At","Notes"
    ],
    "03_CLAIMS": [
        "Claim_ID","Case_ID","Claim_Form","Claim_Statement","Target","Algorithm",
        "Parameter_Set","Attack_Model","Claimed_Scope","Verified_Scope",
        "Scope_Status","Origin","Novelty_Status","Evidence_ID","Witness_ID",
        "Verification_ID","L0","L1","L2","L3","Assurance_State","Claim_Status",
        "Refuted","Created_At","Created_By","Last_Updated","Notes"
    ],
    "04_VERIFICATIONS": [
        "Verification_ID","Claim_ID","Case_ID","Verifier_ID","Verifier_Type",
        "Verifier_Version","Verification_Method","Input_Evidence_ID","Input_Hash",
        "Reference_Implementation","Test_Vector_ID","Result","Verification_Scope",
        "Verifier_Environment","Hardware","Operating_System","Software_Version",
        "Analyst","Started_At","Completed_At","Execution_Time","Independence_Status",
        "Independence_Notes","Output_Evidence_ID","Output_Hash","Verifier_Notes"
    ],
    "05_PROVENANCE": [
        "Event_ID","Case_ID","Object_Type","Object_ID","Event_Type","Actor",
        "Timestamp","Payload_JSON","Payload_Hash","Previous_Event_Hash",
        "Event_Hash","Merkle_Index","Merkle_Level","Merkle_Root","Tree_Head_ID",
        "Signature_Status","Signature_Type","Audit_Status","Notes"
    ],
    "06_ASSETS": [
        "Asset_ID","Case_ID","Asset_Name","Asset_Type","Hostname",
        "IP_or_Identifier","Environment","Operating_System","Application",
        "Version","Location","Criticality","Data_Sensitivity","Data_Lifetime",
        "Algorithm_Count","Migration_Status","HNDL_Risk","Created_At",
        "Last_Updated","Notes"
    ],
    "07_ALGORITHMS": [
        "Algorithm_ID","Algorithm_Name","Family","Category","Parameter_Set",
        "Classical_or_PQC","Key_Size","Security_Level","Standard","OID",
        "Status","Source","Notes"
    ],
    "08_IMPLEMENTATIONS": [
        "Implementation_ID","Implementation_Name","Algorithm_ID","Library_Name",
        "Library_Version","Language","Platform","Repository","Build_ID",
        "Configuration","Implementation_Status","Evidence_ID","Discovered_At",
        "Notes"
    ],
    "09_PROTOCOLS": [
        "Protocol_ID","Protocol_Name","Version","Endpoint","Algorithm_ID",
        "Implementation_ID","Negotiation_Method","PQC_Status","Hybrid_Status",
        "Fallback_Status","Certificate_Status","Migration_Status","Evidence_ID",
        "Checked_At","Notes"
    ],
    "10_DIGITAL_TWIN": [
        "Relationship_ID","Case_ID","Source_ID","Source_Type","Relationship",
        "Target_ID","Target_Type","Assurance_Level","Evidence_ID","Claim_ID",
        "Created_At","Status","Notes"
    ],
    "11_HNDL_RISK": [
        "Risk_ID","Case_ID","Asset_ID","Evidence_ID","Sensitivity","Exposure_Type",
        "Capture_Date","Current_Date","Confidentiality_Lifetime","Migration_Date",
        "Data_Generation_Rate","Optimistic_CRQC_Years","Median_CRQC_Years",
        "Pessimistic_CRQC_Years","Retrospective_Risk","Prospective_Risk",
        "Combined_Risk","Risk_Priority","Baseline_Rank","Proposed_Rank","Notes"
    ],
    "12_MIGRATION": [
        "Migration_ID","Case_ID","Asset_ID","Protocol_ID","Current_Algorithm",
        "Target_PQC_Algorithm","Hybrid_Enabled","PQC_Detected",
        "Legacy_Algorithm_Detected","Fallback_Detected","Certificate_Checked",
        "Handshake_Checked","Migration_Status","Verification_ID","Evidence_ID",
        "Checked_At","Notes"
    ],
    "13_EXPERIMENTS": [
        "Experiment_ID","Case_ID","Experiment_ID_From_Paper","Experiment_Name",
        "Research_Question","Hypothesis","Dataset","Sample_Size","Baseline",
        "Method","Metric","Expected_Result","Observed_Result","Result_Value",
        "Unit","Run_ID","Software_Version","Environment","Started_At",
        "Completed_At","Reproducibility_Status","Result_Status","Notes"
    ],
    "14_AUDIT_LOG": [
        "Audit_ID","Case_ID","Audit_Type","Object_ID","Audit_Timestamp",
        "Auditor","Expected_Hash","Computed_Hash","Merkle_Root_Expected",
        "Merkle_Root_Computed","Signature_Check","Consistency_Check",
        "Inclusion_Check","Result","Failure_Reason","Notes"
    ],
}

ENUMS = {
    "Claim_Forms": ["EX","ST","CX","PD","IM","PR","NG","ID"],
    "Scopes": ["A","B","C","D","NOT_VERIFIED"],
    "Assurance_Levels": ["L0","L1","L2","L3"],
    "Case_Status": ["ACTIVE","COMPLETED","ARCHIVED","SUSPENDED"],
    "Case_Type": ["RESEARCH","VALIDATION","HNDL_ASSESSMENT","PQC_MIGRATION","PROVENANCE_TEST","SYNTHETIC_TEST"],
    "Evidence_Types": ["BINARY","SOURCE_CODE","CERTIFICATE","CONFIGURATION","PACKET_CAPTURE","LOG","TEST_VECTOR","DOCUMENT","METADATA","OTHER"],
    "Evidence_Status": ["REGISTERED","VALIDATED","REJECTED","ARCHIVED"],
    "Integrity_Status": ["NOT_CHECKED","VALID","FAILED"],
    "Claim_Status": ["DRAFT","VALIDATED","REJECTED","L0","L1","L2","L3","REFUTED","ARCHIVED"],
    "Verification_Types": ["DETERMINISTIC","REFERENCE_IMPLEMENTATION","STATISTICAL","INDEPENDENT_REPRODUCTION","FORMAL","PROTOCOL","IDENTIFICATION","NEGATIVE_RESULT"],
    "Verification_Results": ["PASS","FAIL","INCONCLUSIVE","NOT_RUN"],
    "Independence_Status": ["NOT_REQUIRED","PENDING","INDEPENDENT","NOT_INDEPENDENT","FAILED"],
    "Risk_Levels": ["LOW","MEDIUM","HIGH","CRITICAL"],
    "Origin_Types": ["AI","HUMAN","HYBRID","SYSTEM"],
    "Novelty_Status": ["NEW","KNOWN","UNCERTAIN","NOT_ASSESSED"],
    "Classical_or_PQC": ["CLASSICAL","PQC","HYBRID","UNKNOWN"],
}
