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

```text
semantic_error
subject_error
silhouette_error
composition_error
style_drift
material_error
gold_ratio_error
lighting_error
background_error
geometry_error
artifact_error
text_or_logo_error
delivery_error
```

## 3. Critical defect gate

Reject or regenerate when any of the following is present:

| Defect | Diagnostic code |
| --- | --- |
| Wrong object or lost meaning | `semantic_error`, `subject_error` |
| Multiple competing objects | `composition_error` |
| Environment, interior, landscape, floor, pedestal, or horizon | `composition_error`, `background_error` |
| Background not uniform pure black | `background_error` |
| Stone, crystal, marble, lava, or rough mineral texture | `material_error` |
| Mirror, chrome, reflected environment, or HDR spectacle | `material_error`, `lighting_error` |
| Gold exceeds 25% of visible object area | `gold_ratio_error` |
| Additional design colors | `style_drift` |
| Silhouette unreadable at 64 px | `silhouette_error` |
| Object cropped or materially incomplete | `composition_error` |
| Text, pseudo-text, watermark, or unintended logo | `text_or_logo_error` |
| Image missing, unreadable, or not shown to the user | `delivery_error` |

## 4. Weighted scorecard

| Category | Weight | Review questions |
| --- | ---: | --- |
| Meaning and subject recognition | 25 | Is the intended subject immediately identifiable? Are key recognition features preserved? |
| Silhouette and geometry | 20 | Does the silhouette work at 64 px? Are planes deliberate, clean, and structurally coherent? |
| Material and gold system | 20 | Is obsidian matte and manufactured? Is gold controlled, metallic, and within range? |
| Background and composition | 15 | Is there one isolated full object on pure black with adequate negative space? |
| Lighting | 10 | Does light reveal planes without chrome, HDR, haze, or environment reflections? |
| Technical and artifact quality | 10 | Are there malformed parts, noise, accidental text, edge damage, or obvious generation defects? |

Score each category from 0 to its maximum weight.

## 5. Thresholds

```text
90-100 and no critical defects -> ACCEPT
75-89 and no critical defects  -> REPAIR if one targeted change is sufficient
60-74                         -> REGENERATE unless one localized defect dominates
below 60                      -> REGENERATE or STOP
any critical defect           -> REPAIR only when local and safe; otherwise REGENERATE
```

## 6. Category guidance

### Meaning and recognition

- Verify semantic meaning before style attractiveness.
- Compare against the Transformation Contract, not the full source scene.
- Do not penalize removal of nonessential source detail.

### Silhouette and geometry

- Review at full size and 64 px.
- Thin parts must not disappear.
- Facets should support the subject, not create random crystalline noise.

### Material and gold

- Obsidian must not read as natural rock or black chrome.
- Gold must be purposeful and restrained.
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
