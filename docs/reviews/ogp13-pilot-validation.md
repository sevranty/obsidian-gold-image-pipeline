# OGP#13 End-to-End Pilot Validation

Status: PASS for deterministic pilot evidence; no CI pass is claimed.

Validation date: 2026-07-16

Base main: `25348669684b5bcf6b0aa8c3c79f466e94e63a42`

Child PR: #20

## Scope boundary

This pilot exercises the release-candidate skill bundle with deterministic repository tooling. It validates packaging, clean install, prompt validation, visible delivery records, failure-path coverage, and checksum evidence. It does not claim live image-generator aesthetic success, and it does not publish a tag, GitHub Release, marketplace submission, or public binary.

## Acceptance evidence

| Criterion | Result | Evidence |
| --- | --- | --- |
| At least 4/5 accepted final cases | PASS: 5/5 accepted structural final cases remain accepted in the committed OGP#9 baseline. | `reports/ogp9-baseline.json` |
| Visible delivery | PASS: 10/10 workflow cases retain `DELIVERED` state. | `reports/ogp9-baseline.json` |
| Failure recovery | PASS: 6/6 failure-path fixtures match expected recovery or stop behavior. | `reports/ogp9-baseline.json` |
| Clean install smoke | PASS. | `reports/ogp13-install-smoke.json` |
| Raw SHA/checksum evidence | PASS. | `dist/ogp-skill-manifest.json` and `reports/ogp13-pilot.json`; archive checksum retained, generated archive not committed. |

## Release-candidate artifact

- Archive: `/tmp/ogp-skill.zip` during validation; generated archive is not committed.
- Manifest: `dist/ogp-skill-manifest.json`
- Archive SHA-256: `10bf8e0ff242f538b62d18a8e39a0c25b20f1a38c91a7aacf5c15646dce54abd`
- Release candidate: `0.1.0-rc.1`
- Release published: `false`

## Validation commands

```bash
python3 -m py_compile scripts/build_skill_package.py scripts/smoke_test_install.py tests/test_distribution.py
python3 -m unittest discover -s tests -p 'test_distribution.py' -v
python3 scripts/build_skill_package.py --archive /tmp/ogp-skill.zip --manifest dist/ogp-skill-manifest.json
python3 scripts/smoke_test_install.py --archive /tmp/ogp-skill.zip --manifest dist/ogp-skill-manifest.json --report reports/ogp13-install-smoke.json
python3 scripts/run_evals.py --output reports/ogp9-baseline.json --raw-output reports/ogp9-raw-results.json
python3 -m unittest discover -s tests -v
```

## Result summary

```text
archive_sha256=10bf8e0ff242f538b62d18a8e39a0c25b20f1a38c91a7aacf5c15646dce54abd
cli_help_commands=4
prompt_validation_exit=0
accepted_final_cases=5
workflow_delivered_cases=10
failure_path_cases=6
release_published=false
committed_release_archive=false
PASS
```
