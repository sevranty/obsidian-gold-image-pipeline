# OGP#12 Cover Validation

Status: **ACCEPT**

QA schema: `1.0.0`

Exact base before OGP#12: `c65719b559dbbefa88578f4d1b8481ae218298f0`

## Scope

This review covers repository-level visual assets only. It does not claim live third-party image-generator aesthetic success and does not alter the installed skill bundle.

## Canonical committed assets

| Check | Result |
| --- | --- |
| Repository cover | PASS — `assets/repository-cover.svg`, `1280x640` |
| Social-preview source | PASS — `assets/social-preview.svg`, `1280x640` |
| Selected concept | PASS — `assets/concepts/concept-portal.svg` |
| Alternative concepts | PASS — prism and neural-core SVGs |
| Pure black background | PASS — explicit `#000000` root rectangle |
| Text or pseudo-text inside image | PASS — none; only accessible SVG title/description metadata |
| Logo, person, private material, or third-party brand | PASS — none |
| Environment, floor, horizon, smoke, or texture | PASS — none |
| Full subject visibility | PASS |
| Source rights and provenance | PASS |
| Manifest and SHA-256 | PASS |

## Raster review evidence

The same deterministic geometry was rendered locally to:

- `1280x640` PNG;
- `1280x640` WebP;
- `64x32` inspection thumbnail.

Local inspection result:

- exact black pixels: `86.31%`;
- visible gold share of non-black pixels: `23.5%`;
- non-black bounding box: `(127, 114, 1126, 540)`;
- full wireframe and final portal state visible;
- no text, watermark, logo, person, environment, or crop.

These raster files are validation/build outputs. They are not a published release and are not committed as public binaries.

## Critical defect gate

| Diagnostic | Result |
| --- | --- |
| `semantic_error` | none |
| `subject_error` | none |
| `composition_error` | none |
| `background_error` | none |
| `material_error` | none |
| `gold_ratio_error` | none |
| `style_drift` | none |
| `silhouette_error` | none |
| `text_or_logo_error` | none |
| `delivery_error` | none |

## Weighted scorecard

| Category | Score |
| --- | ---: |
| Meaning and subject recognition | 24 / 25 |
| Silhouette and geometry | 18 / 20 |
| Material and gold system | 19 / 20 |
| Background and composition | 15 / 15 |
| Lighting | 9 / 10 |
| Technical and artifact quality | 10 / 10 |
| **Total** | **95 / 100** |

## Decision

```text
verdict: ACCEPT
score_total: 95
critical_defects: []
diagnostic_codes: []
repairable: false
recommended_action: MERGE_AFTER_EXACT_HEAD_REVIEW
repair_scope: none
known_limitations:
  - the asset is deterministic geometry, not evidence of external generator quality
  - raster exports are build outputs rather than versioned release binaries
  - GitHub social-preview Settings are not changed in this contour
```

## Files

- `assets/repository-cover.svg`
- `assets/social-preview.svg`
- `assets/concepts/concept-portal.svg`
- `assets/concepts/concept-prism.svg`
- `assets/concepts/concept-core.svg`
- `assets/source/reference-portal-wireframe.svg`
- `assets/cover-source-manifest.json`
