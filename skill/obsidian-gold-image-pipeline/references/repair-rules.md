# Targeted Repair Rules

## 1. Repair contract

Every repair must contain:

```text
diagnostic_code
observed_defect
single_change
keep_unchanged
must_not_appear
success_signal
```

After the repair, repeat the full critical defect gate and scorecard. Do not assume unaffected invariants remained intact.

## 2. Diagnostic action map

### `semantic_error`

Action: full regeneration from the Transformation Contract. Do not attempt local edit when the semantic subject is wrong.

Success signal: intended meaning and primary subject are immediately recognizable.

### `subject_error`

Action: regenerate when the subject category is wrong; edit only when one recognition feature is missing.

Success signal: subject identity matches declared recognition features.

### `silhouette_error`

Action: simplify or restore the outer contour while preserving camera, material system, and background.

Success signal: silhouette is recognizable at 64 px.

### `composition_error`

Action: remove secondary objects, environment, floor, or crop; recenter or scale the single object.

Success signal: one full isolated object with generous negative space.

### `style_drift`

Action: remove extra colors, realism cues, decorative noise, or unrelated visual language.

Success signal: palette and visual character match the style definition.

### `material_error`

Action: replace mineral, glossy, chrome, or mirror behavior with smooth manufactured matte obsidian. Preserve small controlled satin gold highlights.

Success signal: obsidian is matte and non-mineral; gold is metallic but not mirror-like.

### `gold_ratio_error`

Action: reduce or increase gold only through purposeful rims, trims, insets, seams, tips, or internal core elements.

Success signal: gold visually occupies 15-25% and remains subordinate to obsidian.

### `lighting_error`

Action: replace theatrical or multi-source lighting with one broad soft key and optional restrained warm edge accent.

Success signal: planes read clearly without HDR, bloom, haze, or reflected environment.

### `background_error`

Action: replace the entire background with uniform pure black; remove horizon, floor, vignette color, particles, texture, and cast floor shadow.

Success signal: background reads as uninterrupted `#000000` around the object.

### `geometry_error`

Action: regularize random crystalline noise into deliberate faceted planes; restore clean edges and subject-specific structure.

Success signal: geometry is coherent, minimal, and supports recognition.

### `artifact_error`

Action: repair malformed local geometry only when subject and silhouette are stable; otherwise regenerate.

Success signal: no broken appendages, duplicated parts, holes, noise, or edge damage.

### `text_or_logo_error`

Action: remove text, pseudo-text, symbols, watermarks, and unintended logos without adding replacement marks.

Success signal: no readable or pseudo-readable markings remain.

### `delivery_error`

Action: retrieve, attach, or re-export the actual final image. Do not regenerate solely because delivery failed unless the image is lost.

Success signal: the user can see or access the final image in the response.

## 3. Repair safety

Escalate to full regeneration when:

- repair requires changing more than one global category;
- a repair changes subject identity or camera unintentionally;
- the second targeted repair fails;
- the edit tool cannot preserve declared invariants;
- the source output is too malformed for localized correction.

## 4. Maximum attempts

```text
repair attempt 1 -> full QA
repair attempt 2 -> full QA
if critical defects remain -> one full regeneration
if critical defects still remain -> stop and report limitation
```
