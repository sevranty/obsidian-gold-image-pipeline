# OGP#8 Generated Fixtures

The binary reference and output fixtures are deterministic working-tree artifacts. They are intentionally not committed as a large runtime image array.

Generate the exact corpus before eval runs:

```bash
python3 scripts/generate_evidence_corpus.py
```

Then execute the existing OGP#7 `inspect_image.py` over the generated outputs and compare the reports with `reports/ogp8-inspection.json`. Expected SHA-256 values are stored in `docs/evidence/ogp8-materialized-checksums.txt`.

The committed SVG overview and three 64x64 SVG runtime anchors are documentation/structural aids, not image-generator evidence.
