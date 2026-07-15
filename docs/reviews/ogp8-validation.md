# OGP#8 Visual Evidence Corpus Validation

Status: PASS

Validation date: 2026-07-15

Base: `main@7288a99f68bd59b34bdd45edbcf7e083c9681911`

Validated content HEAD: `b072fc105178a5863cc007bcaac8098a2fe0bf77`

## Evidence model

The validated content HEAD contains the deterministic corpus generator, corpus validator, ten coverage records, fifteen verdict records, materialized checksums, OGP#7 inspection summaries, manual visual-rubric results, provenance notes, a lightweight overview, and three minimal runtime anchors. This document is committed afterward as the evidence envelope.

All raster references, outputs, and previews are deterministic working-tree artifacts generated from geometric primitives. They are not image-generator outputs and are not evidence of generative-model quality. The repository stores their complete metadata and SHA-256 values rather than a large runtime image array.

## Commands

```bash
python3 -m py_compile \
  scripts/generate_evidence_corpus.py \
  scripts/validate_evidence_corpus.py

python3 scripts/generate_evidence_corpus.py

python3 skill/obsidian-gold-image-pipeline/scripts/inspect_image.py \
  examples/accepted/accepted-01-symmetric-orb.png

# Repeat inspect_image.py for all fifteen indexed outputs and aggregate the reports.

python3 scripts/validate_evidence_corpus.py \
  --output reports/generated/ogp8-validation.json
```

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
verdict_index_checksums=True
materialized_checksum_entries=55
inspection_sha_bound=True
runtime_anchor_checksums=True
rights_approved=True
ascii_paths=True
forbidden_private_tokens_absent=True
py_compile=PASS
validation=PASS
```

The three verdict-index SHA-256 values are:

```text
accepted=7ab881cd9d24ee8ebf66228969f32329754d60513cbc068548ac51a0e47809cd
repairable=a4287d5ce266ce1d33af6f1c004ee1b28a6c6bcbd67a13931b7c72d8c2e18572
rejected=5ad0843ca93ebc01e5910d8966654e64be04ad30a49715ba529ee50873d74ad3
```

## Coverage

The corpus covers:

1. simple symmetric object;
2. asymmetric object;
3. hollow object;
4. thin elements;
5. transport or machinery;
6. animal sculpture;
7. architectural symbol;
8. financial metaphor;
9. technology symbol;
10. complex source reduced to one object.

## Rights and privacy

- all fixtures are self-authored programmatic geometry;
- no uploaded user image is included;
- no third-party logo or brand asset is included;
- no personal data or private design-system source is included;
- each case records `source_type`, `rights_status`, provenance, role, subject, invariants, risks, verdict, diagnostics, notes, and checksums.

## Automation boundary

`inspect_image.py` verifies technical raster properties only. It does not prove semantic recognition, material realism, aesthetic quality, gold coverage, or style acceptance. Eight non-accepted fixtures intentionally pass deterministic raster checks; their verdicts are manual visual-rubric decisions. Visual acceptance remains human-reviewed.

## Conclusion

OGP#8 satisfies the structural evidence-corpus scope and provides a reproducible golden set for OGP#9. Actual image-generator behavior remains reserved for the OGP#13 end-to-end pilot.
