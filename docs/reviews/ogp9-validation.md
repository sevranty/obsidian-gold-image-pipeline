# OGP#9 Evaluation Baseline Validation

Status: PASS

Validation date: 2026-07-15

Base: `main@d764b4a442215b1848f3756b7b9a5be2d4758b6f`

## Scope

- 28 trigger cases: 12 positive, 10 negative, 6 boundary;
- 10 workflow cases over all 18 mandatory stages;
- 15 visual regression cases linked to OGP#8;
- 6 controlled failure-path cases;
- standard-library runner and five mutation/regression tests;
- raw and summarized baseline reports;
- manual runbook independent of GitHub Actions.

## Commands

```bash
python3 -m py_compile scripts/run_evals.py tests/test_evals.py
python3 -m unittest discover -s tests -p 'test_evals.py' -v
python3 scripts/run_evals.py \
  --output reports/ogp9-baseline.json \
  --raw-output reports/ogp9-raw-results.json
```

## Results

```text
trigger_positive=12
trigger_negative=10
trigger_boundary=6
workflow_cases=10
workflow_stages=18
visual_cases=15
failure_cases=6
mutation_tests=5
trigger_contract_accuracy=1.0
trigger_precision_static=1.0
trigger_recall_static=1.0
workflow_compliance=1.0
style_regression_contract_pass_rate=1.0
failure_path_compliance=1.0
delivery_success_rate_workflow_contract=1.0
PASS
```

## Finding corrected before PR

The first mutation test showed that a trigger label mismatch reduced a metric but did not fail the suite. The runner was changed to fail closed and the complete test suite was repeated successfully.

## Boundaries

- Static trigger metrics are fixture agreement, not live platform telemetry.
- Workflow cases validate explicit records, not hidden reasoning.
- Visual cases depend on the manual OGP#8 rubric and do not automate aesthetic judgment.
- Actual generation, repair success, installation, and visible delivery remain in OGP#13.
