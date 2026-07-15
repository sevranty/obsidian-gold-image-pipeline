# OGP#8 Manual Visual Rubric

This rubric classifies programmatic structural QA fixtures. It does not claim image-generator quality or automated aesthetic judgment.

## Critical gate

Reject when any of the following is present:

- the subject is not recognizable or becomes multiple unrelated objects;
- a floor, horizon, environment, or light background replaces the isolated black field;
- stone, chrome, mirror, or multicolor material drift replaces matte manufactured obsidian and restrained satin gold;
- crop or pseudo-text artifacts make the asset unusable.

## Weighted review

| Category | Maximum |
| --- | ---: |
| Meaning and subject | 25 |
| Silhouette and geometry | 20 |
| Material and gold | 20 |
| Background and composition | 15 |
| Lighting | 10 |
| Technical and artifact | 10 |

Verdict policy:

- `accepted`: no critical defect and score 85–100;
- `repairable`: no critical defect, one localized diagnostic category, and score 70–84;
- `rejected`: any critical defect or score below 70.

Every repairable fixture must map to exactly one diagnostic category. Deterministic inspection results remain supporting evidence only.
