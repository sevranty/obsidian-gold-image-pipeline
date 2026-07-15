#!/usr/bin/env python3
"""Run deterministic OGP#9 contract and regression evals."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FILES = {"trigger":"evals/trigger-cases.yaml","workflow":"evals/workflow-cases.yaml","visual":"evals/visual-cases.yaml","failure":"evals/failure-cases.yaml"}
EXPECTED_COUNTS = {"trigger":28,"workflow":10,"visual":15,"failure":6}
EXPECTED_TRIGGER_KINDS = {"positive":12,"negative":10,"boundary":6}
WORKFLOW_STAGES = ["input_validation","mode_classification","input_role_assignment","reference_analysis","primary_subject_selection","transformation_contract","scene_specification","prompt_construction","deterministic_prompt_validation","pre_generation_gate","generation_or_edit","deterministic_raster_inspection","full_and_64px_inspection","visual_qa","decision_or_targeted_repair","repeat_validation_after_change","manifest_and_packaging","user_visible_delivery"]

def load(path: Path) -> dict[str, Any]:
    try: value=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc: raise RuntimeError(f"Cannot load {path}: {exc}") from exc
    if not isinstance(value,dict) or not isinstance(value.get("cases"),list): raise RuntimeError(f"Invalid suite root: {path}")
    return value

def main(argv: list[str] | None=None) -> int:
    p=argparse.ArgumentParser(description="Validate OGP trigger, workflow, visual, and failure-path fixtures.")
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--raw-output",type=Path,required=True)
    args=p.parse_args(argv)
    try: suites={name:load(args.root/rel) for name,rel in FILES.items()}
    except RuntimeError as exc:
        sys.stderr.write(json.dumps({"status":"operational_error","error":str(exc)},sort_keys=True)+"\n"); return 3
    errors=[]; raw={"schema_version":"1.0.0","task":"OGP#9","suites":{}}; ids=set()
    for name,payload in suites.items():
        cases=payload["cases"]
        if len(cases)!=EXPECTED_COUNTS[name]: errors.append(f"{name}: expected {EXPECTED_COUNTS[name]}, got {len(cases)}")
        for case in cases:
            cid=case.get("id")
            if not isinstance(cid,str) or not cid: errors.append(f"{name}: missing id")
            elif cid in ids: errors.append(f"duplicate id: {cid}")
            else: ids.add(cid)
            if not case.get("observable_signal"): errors.append(f"{name}/{cid}: observable signal missing")
        if name == "trigger": compact=[{"id":c.get("id"),"expected":c.get("expected"),"observed":c.get("predicted"),"pass":c.get("expected")==c.get("predicted")} for c in cases]
        elif name == "workflow": compact=[{"id":c.get("id"),"expected_stage_count":len(c.get("expected_stages",[])),"observed_stage_count":len(c.get("observed_stages",[])),"delivery_state":c.get("delivery_state"),"pass":c.get("expected_stages")==c.get("observed_stages") and c.get("delivery_state")=="DELIVERED"} for c in cases]
        elif name == "visual": compact=[{"id":c.get("id"),"expected":c.get("expected_verdict"),"observed":c.get("observed_verdict"),"diagnostic_codes":c.get("diagnostic_codes"),"pass":c.get("expected_verdict")==c.get("observed_verdict") and c.get("automated_aesthetic_claim") is False} for c in cases]
        else: compact=[{"id":c.get("id"),"expected_action":c.get("expected_action"),"observed_action":c.get("observed_action"),"expected_code":c.get("expected_code"),"observed_code":c.get("observed_code"),"pass":c.get("expected_action")==c.get("observed_action") and c.get("expected_code")==c.get("observed_code")} for c in cases]
        raw["suites"][name]={"cases":compact,"count":len(cases)}
    kinds={k:sum(c.get("kind")==k for c in suites["trigger"]["cases"]) for k in EXPECTED_TRIGGER_KINDS}
    if kinds!=EXPECTED_TRIGGER_KINDS: errors.append(f"trigger kind counts: {kinds}")
    trigger_correct=sum(c.get("expected")==c.get("predicted") for c in suites["trigger"]["cases"])
    for c in suites["trigger"]["cases"]:
        if c.get("expected") != c.get("predicted"):
            errors.append(f"trigger/{c.get('id')}: routing mismatch")
    positive=[c for c in suites["trigger"]["cases"] if c.get("kind")=="positive"]
    negative=[c for c in suites["trigger"]["cases"] if c.get("kind")=="negative"]
    tp=sum(c.get("predicted","").startswith("TRIGGER_") for c in positive); fn=len(positive)-tp
    tn=sum(c.get("predicted")=="DO_NOT_TRIGGER" for c in negative); fp=len(negative)-tn
    precision=tp/(tp+fp) if tp+fp else 0.0; recall=tp/(tp+fn) if tp+fn else 0.0
    workflow_pass=0
    for c in suites["workflow"]["cases"]:
        ok=c.get("expected_stages")==WORKFLOW_STAGES and c.get("observed_stages")==WORKFLOW_STAGES and c.get("delivery_state")=="DELIVERED"
        workflow_pass+=ok
        if not ok: errors.append(f"workflow/{c.get('id')}: stage or delivery mismatch")
    visual_pass=0; critical=0; repairable=0
    for c in suites["visual"]["cases"]:
        ok=c.get("expected_verdict")==c.get("observed_verdict") and c.get("automated_aesthetic_claim") is False
        visual_pass+=ok; critical+=c.get("observed_verdict")=="rejected"; repairable+=c.get("observed_verdict")=="repairable"
        if not ok: errors.append(f"visual/{c.get('id')}: verdict or boundary mismatch")
    failure_pass=sum(c.get("expected_action")==c.get("observed_action") and c.get("expected_code")==c.get("observed_code") for c in suites["failure"]["cases"])
    metrics={
      "trigger_contract_accuracy":trigger_correct/len(suites["trigger"]["cases"]),
      "trigger_precision_static":precision,
      "trigger_recall_static":recall,
      "workflow_compliance":workflow_pass/len(suites["workflow"]["cases"]),
      "critical_defect_rate_golden_set":critical/len(suites["visual"]["cases"]),
      "repairable_rate_golden_set":repairable/len(suites["visual"]["cases"]),
      "style_regression_contract_pass_rate":visual_pass/len(suites["visual"]["cases"]),
      "failure_path_compliance":failure_pass/len(suites["failure"]["cases"]),
      "delivery_success_rate_workflow_contract":sum(c.get("delivery_state")=="DELIVERED" for c in suites["workflow"]["cases"])/len(suites["workflow"]["cases"])
    }
    result={"schema_version":"1.0.0","task":"OGP#9","status":"pass" if not errors else "fail","suite_counts":{n:len(p["cases"]) for n,p in suites.items()},"trigger_kind_counts":kinds,"metrics":metrics,"errors":errors,"limitations":["Static routing fixtures are not live platform telemetry.","Workflow cases validate observable contract records, not hidden reasoning.","Visual verdicts use a manual rubric; no automatic aesthetic score is claimed.","Actual generation, repair success, and user-visible delivery are exercised in OGP#13."]}
    for path,value in ((args.output,result),(args.raw_output,raw)):
        path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    sys.stdout.write(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return 0 if not errors else 2

if __name__=="__main__": raise SystemExit(main())
