# OGP Evaluation Suite

The suite contains 28 trigger cases, 10 workflow cases, 15 visual cases, and 6 failure-path cases.

Run locally:

```bash
python3 scripts/run_evals.py --output reports/ogp9-baseline.json --raw-output reports/ogp9-raw-results.json
```

The files use JSON-compatible YAML and require no third-party YAML package. Trigger metrics describe fixture agreement. Visual cases use the committed manual rubric. End-to-end generation and delivery are validated separately in OGP#13.
