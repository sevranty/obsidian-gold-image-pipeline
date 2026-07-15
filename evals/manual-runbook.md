# OGP#9 Manual Evaluation Runbook

## Procedure

1. Confirm the checkout SHA and record skill, style, prompt, QA, and manifest schema versions.
2. Run `python3 -m py_compile scripts/run_evals.py tests/test_evals.py`.
3. Run `python3 -m unittest discover -s tests -p 'test_evals.py' -v`.
4. Run `python3 scripts/run_evals.py --output reports/ogp9-baseline.json --raw-output reports/ogp9-raw-results.json`.
5. Verify trigger counts `12/10/6` and inspect every boundary resolution rule.
6. Verify all ten workflow cases contain the 18 canonical stages in order and finish with `DELIVERED`.
7. Compare all fifteen visual cases with OGP#8 scorecards and diagnostic codes. Do not infer aesthetic acceptance from raster metadata.
8. Verify all six failure cases use the declared action and code; `DELIVERY_MISSING` is never completion.
9. Record deviations as raw evidence; do not change expected labels to hide failures.

## Interpretation

Static trigger precision and recall describe agreement inside the declared routing fixture set. They are not production traffic metrics. Actual generation, repair, installation, and user-visible delivery are validated during OGP#13.
