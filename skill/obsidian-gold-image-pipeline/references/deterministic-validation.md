# Deterministic Validation and Packaging

Tool contract version: 1.0.0

## 1. Boundary

These scripts automate only reproducible technical checks and file operations. They do not replace reference analysis, visual QA, semantic review, style judgment, or delivery confirmation.

Required runtime dependency:

```text
Pillow>=10.0,<13.0
```

## 2. Exit codes

All four CLIs use the same stable exit contract:

```text
0 = deterministic checks passed
2 = deterministic validation failed
3 = operational error
```

Machine-readable JSON is written to stdout for pass/fail results. Operational errors are written to stderr.

## 3. Prompt validation

Run after the generator-neutral prompt is assembled and before generation:

```bash
python skill/obsidian-gold-image-pipeline/scripts/validate_prompt.py \
  --file tests/fixtures/prompts/valid-generate.txt \
  --mode generate
```

The validator checks semantic-block presence and contextual conflicts. It normalizes Unicode, case, whitespace, and common English inflections. It does not reject the word `reflection` by itself. Phrases such as `minimal controlled reflections on gold accents` remain valid, while positive requirements for mirror or chrome reflections fail.

Optional rule extension is JSON with:

```text
required_blocks
deny_concepts
allow_patterns
```

Rules extend the defaults; they do not silently remove canonical checks.

## 4. Raster inspection

Run on every generated or repaired candidate:

```bash
python skill/obsidian-gold-image-pipeline/scripts/inspect_image.py \
  /tmp/ogp7-validation/accepted.png \
  --preview-output /tmp/ogp7-validation/preview-64.png \
  --report /tmp/ogp7-validation/image-report.json
```

The inspector records:

- width, height, reduced aspect ratio, format, mode, bands, and alpha presence;
- file size and SHA-256;
- RGBA values and black-distance metrics for four corner pixels;
- a 64x64 preview;
- empty/all-black risk;
- content-edge-touch risk;
- source-preservation hashes.

The corner check is not proof of global background uniformity. The bounding-box heuristic is not semantic object detection and does not judge aesthetics.

## 5. Deterministic manifest

The manifest specification must explicitly supply `created_at`. The script never inserts the current time.

```bash
python skill/obsidian-gold-image-pipeline/scripts/build_manifest.py \
  /tmp/ogp7-validation/manifest-spec.json \
  --selected-output /tmp/ogp7-validation/accepted.png \
  --output /tmp/ogp7-validation/manifest.json
```

The builder:

- validates all required manifest fields;
- validates the complete Scene Specification field set;
- validates the required QA result field set;
- verifies declared output dimensions and format against the raster;
- adds selected-output SHA-256 and byte size;
- serializes canonical sorted JSON with a final newline.

Identical specification bytes and selected-output bytes produce identical manifest bytes.

## 6. Production package

Package only an accepted raster with a matching manifest:

```bash
python skill/obsidian-gold-image-pipeline/scripts/package_asset.py \
  /tmp/ogp7-validation/accepted.png \
  /tmp/ogp7-validation/manifest.json \
  --preview /tmp/ogp7-validation/preview-64.png \
  --output-dir /tmp/ogp7-validation/package \
  --include-webp
```

The package contains:

```text
the selected output filename recorded in the manifest
preview-64.png
manifest.json
package-index.json
optional final-image.webp
```

The command fails when the output directory already exists. It builds in a temporary sibling directory and renames only after success. Source image, manifest, and supplied preview hashes must remain unchanged.

## 7. Mandatory use order

```text
assemble prompt
-> validate_prompt.py
-> generate or edit
-> inspect_image.py
-> visual QA
-> targeted repair or regeneration
-> inspect_image.py again after every change
-> final visual QA
-> build_manifest.py
-> package_asset.py
-> user-visible delivery
```

A script pass never authorizes visual acceptance. A visual pass without visible delivery is still `DELIVERY_MISSING`.
