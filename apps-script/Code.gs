const CONFIG = {
  SPREADSHEET_ID: PropertiesService.getScriptProperties().getProperty('ECA_PQFA_SPREADSHEET_ID') || '',
  TZ: Session.getScriptTimeZone() || 'Asia/Kolkata',
  VERSION: '3.1.0'
};
const API_KEY_PROP = 'ECA_PQFA_API_KEY';
const SHEETS = {
  "01_CASES": [
    "Case_ID",
    "Case_Name",
    "Case_Type",
    "Description",
    "Research_Objective",
    "Created_At",
    "Created_By",
    "Case_Status",
    "Environment",
    "Dataset_ID",
    "Confidentiality_Level",
    "Overall_Risk",
    "Migration_Status",
    "Evidence_Count",
    "Claim_Count",
    "Last_Updated",
    "Notes"
  ],
  "02_EVIDENCE": [
    "Evidence_ID",
    "Case_ID",
    "Evidence_Name",
    "Evidence_Type",
    "Description",
    "Source_Type",
    "File_Name",
    "File_Type",
    "Drive_File_ID",
    "Drive_URL",
    "SHA256",
    "SHA3_256",
    "File_Size",
    "Acquired_At",
    "Acquired_By",
    "Acquisition_Method",
    "Evidence_Status",
    "Integrity_Status",
    "Chain_of_Custody_ID",
    "Parent_Evidence_ID",
    "Created_At",
    "Notes"
  ],
  "03_CLAIMS": [
    "Claim_ID",
    "Case_ID",
    "Claim_Form",
    "Claim_Statement",
    "Target",
    "Algorithm",
    "Parameter_Set",
    "Attack_Model",
    "Claimed_Scope",
    "Verified_Scope",
    "Scope_Status",
    "Origin",
    "Novelty_Status",
    "Evidence_ID",
    "Witness_ID",
    "Verification_ID",
    "L0",
    "L1",
    "L2",
    "L3",
    "Assurance_State",
    "Claim_Status",
    "Refuted",
    "Created_At",
    "Created_By",
    "Last_Updated",
    "Notes"
  ],
  "04_VERIFICATIONS": [
    "Verification_ID",
    "Claim_ID",
    "Case_ID",
    "Verifier_ID",
    "Verifier_Type",
    "Verifier_Version",
    "Verification_Method",
    "Input_Evidence_ID",
    "Input_Hash",
    "Reference_Implementation",
    "Test_Vector_ID",
    "Result",
    "Verification_Scope",
    "Verifier_Environment",
    "Hardware",
    "Operating_System",
    "Software_Version",
    "Analyst",
    "Started_At",
    "Completed_At",
    "Execution_Time",
    "Independence_Status",
    "Independence_Notes",
    "Output_Evidence_ID",
    "Output_Hash",
    "Verifier_Notes"
  ],
  "05_PROVENANCE": [
    "Event_ID",
    "Case_ID",
    "Object_Type",
    "Object_ID",
    "Event_Type",
    "Actor",
    "Timestamp",
    "Payload_JSON",
    "Payload_Hash",
    "Previous_Event_Hash",
    "Event_Hash",
    "Merkle_Index",
    "Merkle_Level",
    "Merkle_Root",
    "Tree_Head_ID",
    "Signature_Status",
    "Signature_Type",
    "Audit_Status",
    "Notes"
  ],
  "06_ASSETS": [
    "Asset_ID",
    "Case_ID",
    "Asset_Name",
    "Asset_Type",
    "Hostname",
    "IP_or_Identifier",
    "Environment",
    "Operating_System",
    "Application",
    "Version",
    "Location",
    "Criticality",
    "Data_Sensitivity",
    "Data_Lifetime",
    "Algorithm_Count",
    "Migration_Status",
    "HNDL_Risk",
    "Created_At",
    "Last_Updated",
    "Notes"
  ],
  "07_ALGORITHMS": [
    "Algorithm_ID",
    "Algorithm_Name",
    "Family",
    "Category",
    "Parameter_Set",
    "Classical_or_PQC",
    "Key_Size",
    "Security_Level",
    "Standard",
    "OID",
    "Status",
    "Source",
    "Notes"
  ],
  "08_IMPLEMENTATIONS": [
    "Implementation_ID",
    "Implementation_Name",
    "Algorithm_ID",
    "Library_Name",
    "Library_Version",
    "Language",
    "Platform",
    "Repository",
    "Build_ID",
    "Configuration",
    "Implementation_Status",
    "Evidence_ID",
    "Discovered_At",
    "Notes"
  ],
  "09_PROTOCOLS": [
    "Protocol_ID",
    "Protocol_Name",
    "Version",
    "Endpoint",
    "Algorithm_ID",
    "Implementation_ID",
    "Negotiation_Method",
    "PQC_Status",
    "Hybrid_Status",
    "Fallback_Status",
    "Certificate_Status",
    "Migration_Status",
    "Evidence_ID",
    "Checked_At",
    "Notes"
  ],
  "10_DIGITAL_TWIN": [
    "Relationship_ID",
    "Case_ID",
    "Source_ID",
    "Source_Type",
    "Relationship",
    "Target_ID",
    "Target_Type",
    "Assurance_Level",
    "Evidence_ID",
    "Claim_ID",
    "Created_At",
    "Status",
    "Notes"
  ],
  "11_HNDL_RISK": [
    "Risk_ID",
    "Case_ID",
    "Asset_ID",
    "Evidence_ID",
    "Sensitivity",
    "Exposure_Type",
    "Capture_Date",
    "Current_Date",
    "Confidentiality_Lifetime",
    "Migration_Date",
    "Data_Generation_Rate",
    "Optimistic_CRQC_Years",
    "Median_CRQC_Years",
    "Pessimistic_CRQC_Years",
    "Retrospective_Risk",
    "Prospective_Risk",
    "Combined_Risk",
    "Risk_Priority",
    "Baseline_Rank",
    "Proposed_Rank",
    "Notes"
  ],
  "12_MIGRATION": [
    "Migration_ID",
    "Case_ID",
    "Asset_ID",
    "Protocol_ID",
    "Current_Algorithm",
    "Target_PQC_Algorithm",
    "Hybrid_Enabled",
    "PQC_Detected",
    "Legacy_Algorithm_Detected",
    "Fallback_Detected",
    "Certificate_Checked",
    "Handshake_Checked",
    "Migration_Status",
    "Verification_ID",
    "Evidence_ID",
    "Checked_At",
    "Notes"
  ],
  "13_EXPERIMENTS": [
    "Experiment_ID",
    "Case_ID",
    "Experiment_ID_From_Paper",
    "Experiment_Name",
    "Research_Question",
    "Hypothesis",
    "Dataset",
    "Sample_Size",
    "Baseline",
    "Method",
    "Metric",
    "Expected_Result",
    "Observed_Result",
    "Result_Value",
    "Unit",
    "Run_ID",
    "Software_Version",
    "Environment",
    "Started_At",
    "Completed_At",
    "Reproducibility_Status",
    "Result_Status",
    "Notes"
  ],
  "14_AUDIT_LOG": [
    "Audit_ID",
    "Case_ID",
    "Audit_Type",
    "Object_ID",
    "Audit_Timestamp",
    "Auditor",
    "Expected_Hash",
    "Computed_Hash",
    "Merkle_Root_Expected",
    "Merkle_Root_Computed",
    "Signature_Check",
    "Consistency_Check",
    "Inclusion_Check",
    "Result",
    "Failure_Reason",
    "Notes"
  ]
};

function ss_(){if(!CONFIG.SPREADSHEET_ID)throw new Error('Set Script Property ECA_PQFA_SPREADSHEET_ID before using the Sheets bridge.');return SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID);}
function now_(){return Utilities.formatDate(new Date(),CONFIG.TZ,'yyyy-MM-dd HH:mm:ss');}
function norm_(v){return v===null||v===undefined?'':String(v).trim();}
function json_(x){return ContentService.createTextOutput(JSON.stringify(x)).setMimeType(ContentService.MimeType.JSON);}
function auth_(p){const configured=PropertiesService.getScriptProperties().getProperty(API_KEY_PROP); if(!configured) return {ok:false,error:'API key not configured in Script Properties'}; if(!p || !p.api_key || p.api_key!==configured) return {ok:false,error:'Unauthorized'}; return {ok:true};}
function sheet_(name){const s=ss_().getSheetByName(name); if(!s) throw new Error('Missing sheet: '+name); return s;}
function headers_(name){return sheet_(name).getRange(1,1,1,sheet_(name).getLastColumn()).getValues()[0].map(norm_);}
function rows_(name){const sh=sheet_(name),hs=headers_(name),values=sh.getDataRange().getValues();return values.slice(1).map((r,i)=>{const o={};hs.forEach((h,j)=>{if(h)o[h]=r[j];});o.__row=i+2;return o;});}
function idField_(name){const h=headers_(name);return h.find(x=>/_ID$/.test(x)) || ''; }
function nextId_(name){const p={'01_CASES':'CASE','02_EVIDENCE':'EVD','03_CLAIMS':'CLM','04_VERIFICATIONS':'VER','05_PROVENANCE':'EVT','06_ASSETS':'AST','07_ALGORITHMS':'ALG','08_IMPLEMENTATIONS':'IMP','09_PROTOCOLS':'PRT','10_DIGITAL_TWIN':'REL','11_HNDL_RISK':'RSK','12_MIGRATION':'MIG','13_EXPERIMENTS':'EXP','14_AUDIT_LOG':'AUD'}[name]; if(!p) return ''; const width=name==='05_PROVENANCE'?5:4; return p+'-'+Utilities.formatDate(new Date(),CONFIG.TZ,'yyyy')+'-'+String(rows_(name).length+1).padStart(width,'0');}
function sha256_(s){const b=Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256,String(s),Utilities.Charset.UTF_8);return b.map(x=>{const n=x<0?x+256:x;return ('0'+n.toString(16)).slice(-2);}).join('');}
function setup_(){Object.keys(SHEETS).forEach(n=>{const sh=sheet_(n),hs=SHEETS[n];if(sh.getLastRow()===0)sh.getRange(1,1,1,hs.length).setValues([hs]);sh.setFrozenRows(1);sh.getRange(1,1,1,hs.length).setFontWeight('bold').setWrap(true);try{sh.getDataRange().createFilter();}catch(e){}sh.autoResizeColumns(1,Math.min(hs.length,12));});buildEnums_();buildReadme_();return {ok:true,version:CONFIG.VERSION,sheets:Object.keys(SHEETS).concat(['15_ENUMS','16_README'])};}
function create_(name,record){const sh=sheet_(name),hs=headers_(name),r=Object.assign({},record||{}),idf=idField_(name);if(idf&&!norm_(r[idf]))r[idf]=nextId_(name);if(hs.includes('Created_At')&&!norm_(r.Created_At))r.Created_At=now_();if(hs.includes('Last_Updated')&&!norm_(r.Last_Updated))r.Last_Updated=now_();sh.appendRow(hs.map(h=>Object.prototype.hasOwnProperty.call(r,h)?r[h]:''));return r;}
function upsert_(name,record){const sh=sheet_(name),hs=headers_(name),idf=idField_(name),r=Object.assign({},record||{});if(!idf)throw new Error('No ID field');if(!norm_(r[idf]))r[idf]=nextId_(name);const values=sh.getDataRange().getValues();let row=-1;for(let i=1;i<values.length;i++){if(norm_(values[i][hs.indexOf(idf)])===norm_(r[idf])){row=i+1;break;}}if(row<0)return create_(name,r);hs.forEach((h,j)=>{if(Object.prototype.hasOwnProperty.call(r,h))sh.getRange(row,j+1).setValue(r[h]);});if(hs.includes('Last_Updated'))sh.getRange(row,hs.indexOf('Last_Updated')+1).setValue(now_());return r;}
function list_(name){return rows_(name).map(o=>{delete o.__row;return o;});}
function doGet(e){try{const a=(e&&e.parameter&&e.parameter.action)||'health';if(a==='health')return json_({ok:true,version:CONFIG.VERSION,timestamp:now_(),spreadsheet_id:CONFIG.SPREADSHEET_ID});if(a==='list'){const ar=auth_(e.parameter);if(!ar.ok)return json_(ar);return json_({ok:true,data:list_(e.parameter.sheet)});}return json_({ok:false,error:'Unknown action'});}catch(err){return json_({ok:false,error:String(err)});}}
function doPost(e){try{const p=JSON.parse((e&&e.postData&&e.postData.contents)||'{}');if(p.action==='health')return json_({ok:true,version:CONFIG.VERSION,timestamp:now_(),spreadsheet_id:CONFIG.SPREADSHEET_ID});const ar=auth_(p);if(!ar.ok)return json_(ar);if(p.action==='setup')return json_(setup_());if(p.action==='list')return json_({ok:true,data:list_(p.sheet)});if(p.action==='create')return json_({ok:true,data:create_(p.sheet,p.record||{})});if(p.action==='upsert')return json_({ok:true,data:upsert_(p.sheet,p.record||{})});if(p.action==='ping')return json_({ok:true,data:'ECA-PQFA Sheets bridge online'});return json_({ok:false,error:'Unknown action'});}catch(err){return json_({ok:false,error:String(err)});}}

function buildEnums_(){
  const sh=ss_().getSheetByName('15_ENUMS'); if(!sh)return;
  sh.clear();
  const groups={
    Claim_Forms:['EX','ST','CX','PD','IM','PR','NG','ID'],
    Scopes:['A','B','C','D','NOT_VERIFIED'],
    Assurance:['L0','L1','L2','L3'],
    Origins:['AI','HUMAN','HYBRID','SYSTEM'],
    Verification_Result:['PASS','FAIL','INCONCLUSIVE','NOT_RUN'],
    Independence:['NOT_REQUIRED','PENDING','INDEPENDENT','NOT_INDEPENDENT','FAILED'],
    Risk:['LOW','MEDIUM','HIGH','CRITICAL'],
    Migration:['NOT_STARTED','IN_PROGRESS','PARTIAL','VERIFIED','FAILED','NOT_APPLICABLE']
  };
  const names=Object.keys(groups); sh.getRange(1,1,1,names.length).setValues([names]).setFontWeight('bold');
  const max=Math.max.apply(null,names.map(k=>groups[k].length));
  const rows=[]; for(let i=0;i<max;i++) rows.push(names.map(k=>groups[k][i]||''));
  if(rows.length)sh.getRange(2,1,rows.length,names.length).setValues(rows);
  sh.setFrozenRows(1);
}

function buildReadme_(){
  const sh=ss_().getSheetByName('16_README'); if(!sh)return;
  sh.clear();
  const rows=[
    ['ECA-PQFA','Evidence-Carrying AI-Assisted Cryptanalysis and Post-Quantum Forensic Assurance'],
    ['Purpose','University research-tool persistence layer and audit console.'],
    ['H/W/E/V/P','Hypothesis / Witness / Experimental evidence / Verification / Provenance'],
    ['Scopes','A design; B reduced-parameter; C implementation; D protocol.'],
    ['Assurance','L0 hypothesis; L1 executable support; L2 independent reproduction; L3 formal verification.'],
    ['Sheets role','Google Sheets stores structured metadata. It is not itself an immutable forensic ledger.'],
    ['Evidence role','Store large artifacts externally; record Drive/file identifiers and SHA-256/SHA3-256 hashes here.'],
    ['Integrity','Python backend computes hash-chain and Merkle commitments and verifies signed tree heads.'],
    ['AI rule','AI-generated output is provenance/origin metadata and cannot independently promote assurance.'],
    ['Research integrity','No fabricated experimental results; synthetic demo records must remain labelled SYNTHETIC/DEMO.'],
    ['Security','For confidential work configure an API key and use authenticated access. Do not publish secrets in Apps Script source.']
  ];
  sh.getRange(1,1,rows.length,2).setValues(rows); sh.setFrozenRows(1); sh.autoResizeColumns(1,2);
}
