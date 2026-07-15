#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
RUNNER = SOURCE / "scripts/run_evals.py"

class EvalRunnerTests(unittest.TestCase):
    def copy_suite(self, target: Path) -> None:
        shutil.copytree(SOURCE / "evals", target / "evals")

    def run_runner(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(RUNNER), "--root", str(root), "--output", str(root/"baseline.json"), "--raw-output", str(root/"raw.json")], capture_output=True, text=True)

    def test_baseline_passes(self) -> None:
        result=self.run_runner(SOURCE)
        self.assertEqual(result.returncode,0,result.stderr+result.stdout)
        self.assertEqual(json.loads(result.stdout)["status"],"pass")

    def test_trigger_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self.copy_suite(root)
            path=root/"evals/trigger-cases.yaml"; data=json.loads(path.read_text())
            data["cases"][0]["predicted"]="DO_NOT_TRIGGER"
            path.write_text(json.dumps(data)+"\n")
            result=self.run_runner(root)
            self.assertEqual(result.returncode,2)
            self.assertEqual(json.loads(result.stdout)["status"],"fail")

    def test_workflow_stage_regression_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self.copy_suite(root)
            path=root/"evals/workflow-cases.yaml"; data=json.loads(path.read_text())
            data["cases"][0]["observed_stages"].remove("visual_qa")
            path.write_text(json.dumps(data)+"\n")
            result=self.run_runner(root)
            self.assertEqual(result.returncode,2)
            self.assertTrue(any("workflow/W01" in item for item in json.loads(result.stdout)["errors"]))

    def test_visual_boundary_claim_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self.copy_suite(root)
            path=root/"evals/visual-cases.yaml"; data=json.loads(path.read_text())
            data["cases"][0]["automated_aesthetic_claim"]=True
            path.write_text(json.dumps(data)+"\n")
            result=self.run_runner(root)
            self.assertEqual(result.returncode,2)

    def test_invalid_suite_is_operational_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self.copy_suite(root)
            (root/"evals/failure-cases.yaml").write_text("not json\n")
            result=self.run_runner(root)
            self.assertEqual(result.returncode,3)
            self.assertEqual(json.loads(result.stderr)["status"],"operational_error")

if __name__=="__main__": unittest.main()
