# OGP#7 Deterministic Tooling Validation

Status: PASS

Validation date: 2026-07-15

Base: `main@446d8c9ffd07cf0893d86df4b19e0157da399606`

Validated content HEAD: `2a57876182ab6a0e6064b0e38e4147403294aadd`

## Evidence model

The validated content HEAD contains the runtime integration, four public CLIs, the shared helper, fixtures, and unit tests. This evidence document is committed afterward as a separate evidence envelope.

## Scope

Validated artifacts:

- `skill/obsidian-gold-image-pipeline/SKILL.md`;
- `skill/obsidian-gold-image-pipeline/requirements.txt`;
- `skill/obsidian-gold-image-pipeline/references/deterministic-validation.md`;
- `skill/obsidian-gold-image-pipeline/scripts/_common.py`;
- `skill/obsidian-gold-image-pipeline/scripts/validate_prompt.py`;
- `skill/obsidian-gold-image-pipeline/scripts/inspect_image.py`;
- `skill/obsidian-gold-image-pipeline/scripts/build_manifest.py`;
- `skill/obsidian-gold-image-pipeline/scripts/package_asset.py`;
- `tests/test_tooling.py`;
- positive and negative prompt and manifest fixtures.

## Commands

```bash
python3 -m py_compile \
  skill/obsidian-gold-image-pipeline/scripts/_common.py \
  skill/obsidian-gold-image-pipeline/scripts/validate_prompt.py \
  skill/obsidian-gold-image-pipeline/scripts/inspect_image.py \
  skill/obsidian-gold-image-pipeline/scripts/build_manifest.py \
  skill/obsidian-gold-image-pipeline/scripts/package_asset.py

python3 -m unittest discover -s tests -p 'test_*.py' -v

python3 skill/obsidian-gold-image-pipeline/scripts/validate_prompt.py --help
python3 skill/obsidian-gold-image-pipeline/scripts/inspect_image.py --help
python3 skill/obsidian-gold-image-pipeline/scripts/build_manifest.py --help
python3 skill/obsidian-gold-image-pipeline/scripts/package_asset.py --help

python3 skill/obsidian-gold-image-pipeline/scripts/validate_prompt.py \
  --file tests/fixtures/prompts/valid-generate.txt \
  --mode generate

python3 skill/obsidian-gold-image-pipeline/scripts/validate_prompt.py \
  --file tests/fixtures/prompts/invalid-generate.txt \
  --mode generate

python3 skill/obsidian-gold-image-pipeline/scripts/inspect_image.py \
  /tmp/ogp7-validation/accepted.png \
  --preview-output /tmp/ogp7-validation/preview-64.png \
  --report /tmp/ogp7-validation/image-report.json

python3 skill/obsidian-gold-image-pipeline/scripts/build_manifest.py \
  /tmp/ogp7-validation/manifest-spec.json \
  --selected-output /tmp/ogp7-validation/accepted.png \
  --output /tmp/ogp7-validation/manifest-a.json

python3 skill/obsidian-gold-image-pipeline/scripts/build_manifest.py \
  /tmp/ogp7-validation/manifest-spec.json \
  --selected-output /tmp/ogp7-validation/accepted.png \
  --output /tmp/ogp7-validation/manifest-b.json

cmp /tmp/ogp7-validation/manifest-a.json \
  /tmp/ogp7-validation/manifest-b.json

python3 skill/obsidian-gold-image-pipeline/scripts/package_asset.py \
  /tmp/ogp7-validation/accepted.png \
  /tmp/ogp7-validation/manifest-a.json \
  --preview /tmp/ogp7-validation/preview-64.png \
  --output-dir /tmp/ogp7-validation/package \
  --include-webp
```

## Results

### Structural and unit checks

```text
python=3.13.5
pillow=12.2.0
py_compile=PASS
cli_tools=4
cli_help=4
unit_tests=12
unit_tests_result=PASS
```

All four help commands exited `0`. Routine help and passing CLI commands produced no stderr output. The negative prompt fixture returned a machine-readable validation report on stdout and exited `2`, as specified.

### Prompt validation

```text
positive_prompt_exit=0
negative_prompt_exit=2
controlled_gold_reflections_allowed=True
mirror_or_chrome_reflections_rejected=True
case_and_inflection_normalization=True
edit_contract_fields=5
```

### Raster inspection

The generated technical fixture was a 256x256 RGB PNG with a pure-black background, a dark object, and a restrained gold region.

```text
width=256
height=256
aspect_ratio=1:1
format=PNG
mode=RGB
has_alpha=False
corners_near_black=True
content_bbox=[58, 63, 199, 189]
content_edge_touch=False
source_preserved=True
inspection_exit=0
selected_output_sha256=0b6a84651a833b3af79d788ebad53a23edcb76cd0a378bf2f2bc3e12490ad025
```

### Manifest reproducibility

Both manifest runs produced identical bytes.

```text
manifest_repeatable=True
manifest_sha256=93cfc9898df373b784fdb0c0c2111e36950365a628626e710abb93e21d1d68bf
created_at_explicit=True
created_at_timezone_required=True
scene_fields_complete=True
qa_fields_complete=True
output_dimensions_verified=True
output_format_verified=True
```

### Packaging

```text
package_files=5
source_preserved=True
selected_output_resolves=True
existing_output_rejected=True
```

Package contents:

```text
accepted.png
final-image.webp
manifest.json
package-index.json
preview-64.png
```

The final image, manifest, and supplied preview retained their source hashes. Packaging used a temporary sibling directory and published only after all checks passed.

### Repository hygiene

```text
validated_text_files=14
ascii_only=True
final_newlines=True
input_overwrite_protection=True
```

## Stable exit codes

```text
0 = deterministic checks passed
2 = deterministic validation failed
3 = operational error
```

Validation failures are machine-readable on stdout. Missing files, invalid JSON, decode failures, output collisions, and filesystem errors produce operational reports on stderr.

## Automation boundary

The tooling intentionally does not automate:

- semantic correctness or subject recognition;
- aesthetic or style acceptance;
- visual material judgment;
- gold-coverage measurement;
- OCR or pseudo-text detection;
- automatic selection of the best generated candidate;
- image generation itself.

Corner sampling does not prove global background uniformity. The non-black bounding box is a crop-risk heuristic, not semantic object detection. Full visual QA and user-visible delivery remain mandatory.

## Validation conclusion

OGP#7 meets its deterministic validation, manifest, and packaging scope. The scripts are non-destructive, produce stable reports and exit codes, and do not claim authority over visual acceptance. Actual accepted, repairable, and rejected visual evidence remains in OGP#8.
