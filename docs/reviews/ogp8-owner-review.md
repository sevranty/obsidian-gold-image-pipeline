# OGP#8 Owner Review

Status: PASS after corrections

Validation date: 2026-07-15

Base: `main@7288a99f68bd59b34bdd45edbcf7e083c9681911`

Initial review HEAD: `bdc953c2ff0d7dc0028239b31d4c3aff9372a412`

Validated content HEAD: `0a0dd3f19b5a58c58a5cb229e30c45df3ba7246f`

The earlier `docs/reviews/ogp8-validation.md` snapshot is superseded by this review because the branch changed during corrections.

## Findings corrected

| ID | Severity | Finding | Correction |
| --- | --- | --- | --- |
| OR-01 | P1 | Clean generation changed tracked inventory fields. | Committed inventory now matches generator output and verdict indexes use canonical serialization. |
| OR-02 | P1 | Checksum generation scanned unrelated repository PNG files. | Checksum scope is limited to the exact 55 OGP#8 raster paths. |
| OR-03 | P1 | Weighted totals lacked six-category score breakdowns. | All 15 cases now include category scores; a validator reconciles maxima, sums, verdicts, actions, and diagnostics. |
| OR-04 | P2 | Runtime anchors and the overview lacked individual provenance records. | Every visual path now has source type, rights status, path, and SHA-256 metadata; a dedicated validator checks them. |

## Validation commands

```bash
python3 -m py_compile \
  scripts/generate_evidence_corpus.py \
  scripts/validate_evidence_corpus.py \
  scripts/validate_manual_review.py \
  scripts/validate_visual_provenance.py

python3 scripts/generate_evidence_corpus.py
python3 scripts/validate_evidence_corpus.py
python3 scripts/validate_manual_review.py
python3 scripts/validate_visual_provenance.py
```

The existing OGP#7 `inspect_image.py` was applied to all fifteen outputs and the results are recorded in `reports/ogp8-inspection.json`.

## Results

```text
coverage_cases=10
accepted=5
repairable=5
rejected=5
materialized_raster_assets=55
ogp7_inspection_reports=15
accepted_technical_pass=5
runtime_svg_anchors=3
documentation_visuals=1
verdict_index_checksums=True
materialized_checksum_entries=55
checksum_scope_isolated=True
clean_generator_inventory_stable=True
inspection_sha_bound=True
manual_scorecard_cases=15
manual_scorecard_categories=6
manual_scorecard_total_reconciled=True
visual_provenance_records=29
visual_paths=59
ascii_paths=True
private_source_tokens_absent=True
py_compile=PASS
validation=PASS
```

## Boundary

The corpus consists of deterministic programmatic structural fixtures. It does not claim to measure image-generator quality, aesthetic quality, material realism, semantic recognition, or gold coverage. Actual generator behavior is tested later in OGP#13.

Public distribution terms are defined later in OGP#10. This task records provenance and ownership classification only.
