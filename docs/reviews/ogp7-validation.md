# OGP#7 Deterministic Tooling Validation

Status: Owner review corrections validated; PASS

Validation date: 2026-07-15

Base: `main@446d8c9ffd07cf0893d86df4b19e0157da399606`

Initial review HEAD: `15429d09fb7c840ef32391976988757bbd4257ed`

Validated content HEAD: `7e51f0a67d3901deb2a16ae2e8c91c55b45d8160`

## Evidence model

The validated content HEAD contains the runtime integration, four public CLIs, shared helpers, fixtures, unit tests, and all owner-review corrections. This document is committed afterward as the evidence envelope.

## Owner-review findings

| ID | Severity | Finding | Disposition |
| --- | --- | --- | --- |
| OR-01 | P1 | An invalid custom required-block regex could raise an uncaught `re.error` and exit `1`, violating the stable `0/2/3` contract. | Precompile extension regexes, convert invalid patterns to `ToolError`, emit JSON on stderr, and test exit `3`. |
| OR-02 | P1 | The manifest builder accepted an incomplete QA category map and did not reconcile `score_total` with the six weighted categories. | Require all six canonical categories and limits, reject unknown or missing categories, and verify the category sum. |
| OR-03 | P2 | Initial evidence did not execute operational exits for all four CLIs or refusal to overwrite an existing package directory. | Add dedicated regression tests for missing inputs and existing package output. |
| OR-04 | P2 | Initial evidence grouped all raster decode failures as operational errors. | Clarify that supplied-content and contract mismatches are exit `2`; invocation and inaccessible primary inputs are exit `3`. |
| OR-05 | P1 | Standard `argparse` usage and type errors emitted plain text and exit `2`, bypassing the machine-readable CLI contract. | Add `ToolArgumentParser`, emit JSON operational reports on stderr, normalize parse errors to exit `3`, and test all four parsers. |

The initial review HEAD was invalidated. All checks below were repeated after the corrections.

## Validated artifacts

- `skill/obsidian-gold-image-pipeline/SKILL.md`;
- `skill/obsidian-gold-image-pipeline/requirements.txt`;
- `skill/obsidian-gold-image-pipeline/references/deterministic-validation.md`;
- `skill/obsidian-gold-image-pipeline/scripts/_common.py`;
- `skill/obsidian-gold-image-pipeline/scripts/validate_prompt.py`;
- `skill/obsidian-gold-image-pipeline/scripts/inspect_image.py`;
- `skill/obsidian-gold-image-pipeline/scripts/build_manifest.py`;
- `skill/obsidian-gold-image-pipeline/scripts/package_asset.py`;
- `tests/test_tooling.py`;
- `tests/test_tooling_review.py`;
- positive and negative prompt and manifest fixtures.

## Validation commands

```bash
python3 -m py_compile \
  skill/obsidian-gold-image-pipeline/scripts/_common.py \
  skill/obsidian-gold-image-pipeline/scripts/validate_prompt.py \
  skill/obsidian-gold-image-pipeline/scripts/inspect_image.py \
  skill/obsidian-gold-image-pipeline/scripts/build_manifest.py \
  skill/obsidian-gold-image-pipeline/scripts/package_asset.py \
  tests/test_tooling.py \
  tests/test_tooling_review.py

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

### Structural and CLI checks

```text
python=3.13.5
pillow=12.2.0
py_compile=PASS
cli_tools=4
cli_help=4
unit_tests=18
unit_tests_result=PASS
parse_argument_errors_exit=3
parse_argument_errors_machine_json=True
missing_input_exit_validate_prompt=3
missing_input_exit_inspect_image=3
missing_input_exit_build_manifest=3
missing_input_exit_package_asset=3
invalid_custom_regex_exit=3
```

All help commands exited `0`. Successful integration commands produced no stderr. The negative prompt fixture emitted machine-readable JSON on stdout and exited `2`.

### Prompt validation

```text
positive_prompt_exit=0
negative_prompt_exit=2
required_semantic_blocks=13
controlled_gold_reflections_allowed=True
mirror_or_chrome_reflections_rejected=True
case_and_inflection_normalization=True
edit_contract_fields=5
```

### Raster inspection

The deterministic technical fixture was a 256x256 RGB PNG with pure-black corners, a dark object, and a restrained gold region.

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

Two runs with the same specification and raster produced identical bytes.

```text
manifest_repeatable=True
manifest_sha256=93cfc9898df373b784fdb0c0c2111e36950365a628626e710abb93e21d1d68bf
created_at_explicit=True
created_at_timezone_required=True
scene_fields_complete=True
scene_mode_consistent=True
qa_fields_complete=True
qa_categories=6
qa_score_total_reconciled=True
output_dimensions_verified=True
output_format_verified=True
```

### Packaging

```text
package_files=5
source_preserved=True
selected_output_resolves=True
existing_output_rejected=True
successful_pipeline_stderr_bytes=0
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
validated_text_files=15
ascii_only=True
final_newlines=True
input_overwrite_protection=True
```

## Stable exit and output contract

```text
0 = deterministic checks passed
2 = supplied content or deterministic contract validation failed
3 = argument, configuration, input access, primary inspection decode, output collision, or filesystem operation failed
```

Exit `0` and `2` reports are machine-readable on stdout. Exit `3` reports are machine-readable on stderr. The manifest builder treats a reachable but invalid selected raster or declared metadata mismatch as content validation failure `2`; the raster inspector treats inability to access or decode its primary input as operational failure `3`.

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

OGP#7 meets its deterministic validation, manifest, and packaging scope. All five owner-review findings are corrected. The scripts are non-destructive, produce stable reports and exit codes, and do not claim authority over visual acceptance. Actual accepted, repairable, and rejected visual evidence remains in OGP#8.
