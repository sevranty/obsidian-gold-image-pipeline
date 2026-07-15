# OGP#8 Provenance and Rights Notes

- Every raster represented by this change is generated from geometric primitives by `scripts/generate_evidence_corpus.py`.
- No uploaded user image, third-party logo, brand asset, personal data, private design-system document, or external photograph is embedded.
- `rights_status` is recorded per asset in `docs/evidence/ogp8-inventory.json`.
- Generated PNGs are working-tree artifacts and are intentionally not committed as a large image array. Their hashes and validation reports are committed.
- The corpus is a structural QA and regression fixture set. It must not be described as image-generator quality evidence.
- Runtime contains only three 64x64 SVG anchors. Repository-level evidence contains indexes, an overview, manifests, checksums, and reproducible generation scripts.
