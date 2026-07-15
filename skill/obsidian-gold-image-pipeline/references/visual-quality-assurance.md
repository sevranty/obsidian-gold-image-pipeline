# Visual Quality Assurance

QA schema version: 1.0.0

## 1. Decision model

Quality review combines:

1. critical defect gate;
2. weighted scorecard;
3. full-size visual inspection;
4. 64 px silhouette inspection;
5. user-visible delivery confirmation.

A critical defect overrides the numerical score.

## 2. Diagnostic codes

| Code | Meaning |
| --- | --- |
| `semantic_error` | The intended meaning, relationship, or fused metaphor is wrong even if a recognizable object is present. |
| `subject_error` | The object category or declared recognition features are wrong or missing. |
| `silhouette_error` | The outer contour, proportion, or pose is not recognizable at the target scale. |
| `composition_error` | The result contains competing objects, invalid crop, environment, floor, or insufficient negative space. |
| `style_drift` | Additional colors, realism cues, decorative noise, or unrelated visual language are present. |
| `material_error` | Obsidian or gold material behavior violates the style contract. |
| `gold_ratio_error` | Gold exceeds the hard cap or is below target without sufficient semantic justification. |
| `lighting_error` | Lighting is theatrical, multi-source, HDR-like, or fails to reveal form. |
| `background_error` | Background is not uniform pure black or contains scene elements. |
| `geometry_error` | Facets are random, incoherent, overly crystalline, or fail to support recognition. |
| `artifact_error` | Generated anatomy, appendages, openings, repeated parts, or edges are malformed. |
| `text_or_logo_error` | Text, pseudo-text, watermark, or unintended mark is present. |
| `delivery_error` | The final image is missing, unreadable, inaccessible, or not shown to the user. |

## 3. Critical defect gate

Reject, repair, or regenerate according to the action map when any of the following is present:

| Defect | Diagnostic code |
| --- | --- |
| Intended meaning or fused metaphor is wrong | `semantic_error` |
| Wrong object category or missing defining recognition features | `subject_error` |
| Multiple competing objects | `composition_error` |
| Environment, interior, landscape, floor, pedestal, or horizon | `composition_error`, `background_error` |
| Background not uniform pure black | `background_error` |
| Stone, crystal, marble, lava, or rough mineral texture | `material_error` |
| Mirror, chrome, reflected environment, or HDR spectacle | `material_error`, `lighting_error` |
| Gold exceeds 25% of visible object area | `gold_ratio_error` |
| Additional design colors | `style_drift` |
| Silhouette unreadable when fitted inside 64x64 px | `silhouette_error` |
| Object cropped or materially incomplete | `composition_error` |
| Text, pseudo-text, watermark, or unintended logo | `text_or_logo_error` |
| Image missing, unreadable, or not shown to the user | `delivery_error` |

Gold below the provisional 15% target is not automatically critical. Apply `gold_ratio_error` only when the accent is visually accidental, too weak to carry its declared semantic role, or undocumented in the contract.

## 4. Weighted scorecard

| Category | Weight | Review questions |
| --- | ---: | --- |
| Meaning and subject recognition | 25 | Is the intended subject immediately identifiable? Are key recognition features preserved? |
| Silhouette and geometry | 20 | Does the silhouette work at 64 px? Are planes deliberate, clean, and structurally coherent? |
| Material and gold system | 20 | Is obsidian matte and manufactured? Is gold controlled, metallic, and justified? |
| Background and composition | 15 | Is there one isolated full object on pure black with adequate negative space? |
| Lighting | 10 | Does light reveal planes without chrome, HDR, haze, or environment reflections? |
| Technical and artifact quality | 10 | Are there malformed parts, noise, accidental text, edge damage, or obvious generation defects? |

Score each category from 0 to its maximum weight.

## 5. Thresholds

```text
90-100 and no critical defects -> ACCEPT
75-89 and no critical defects  -> TARGETED REPAIR only for one localized diagnostic category; otherwise REGENERATE
60-74                          -> REGENERATE; use repair only for one clearly isolated defect with no semantic/global drift
below 60                       -> REGENERATE or STOP
any critical defect            -> follow diagnostic action map; repair only when local and safe, otherwise REGENERATE
```

A numerical band never authorizes a multi-category repair. The single-change rule remains mandatory.

## 6. Category guidance

### Meaning and recognition

- Verify semantic meaning before style attractiveness.
- Compare against the Transformation Contract, not the full source scene.
- Do not penalize removal of nonessential source detail.

### Silhouette and geometry

- Review at full size and fitted inside 64x64 px.
- Thin parts must not disappear.
- Facets should support the subject, not create random crystalline noise.

### Material and gold

- Obsidian must not read as natural rock or black chrome.
- Gold must be purposeful and restrained.
- The 15-25% target is provisional pending evidence calibration.
- Estimated gold coverage is a visual review, not a false-precision pixel metric.

### Background and composition

- Background must be visually uniform black.
- No ground plane, cast floor shadow, vignette color, or smoke.
- The full object must have breathing room.

### Lighting

- Plane separation must remain visible.
- No multi-source spectacle or white hotspot dominance.
- Gold highlights may be small and controlled.

### Technical artifacts

- Inspect edges, openings, appendages, symmetry, and repeated structures.
- Reject pseudo-text and accidental iconography.
- Confirm the image is actually accessible to the user.

## 7. QA output

Record:

```text
verdict
score_total
category_scores
critical_defects
diagnostic_codes
repairable
recommended_action
repair_scope
known_limitations
```
