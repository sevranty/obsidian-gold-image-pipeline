# Transformation Contract

## 1. Purpose

The Transformation Contract is the stable bridge between reference analysis and generation planning. It prevents the prompt from silently reinterpreting the source.

## 2. Required schema

```text
mode
primary_subject
semantic_meaning
recognition_features
silhouette_features
preserve
simplify
replace
remove
must_not_add
subject_fidelity
silhouette_fidelity
composition_fidelity
composition_guidance
preferred_orientation
confidence
unknowns
```

## 3. Field rules

### `preserve`

Use for features required to recognize the subject or retain the intended meaning:

- outer silhouette;
- distinctive proportions;
- unique openings, appendages, or structural parts;
- pose or orientation;
- one semantically important internal feature.

### `simplify`

Use for features that should remain but be reduced:

- repeated small components;
- mechanical detail;
- organic surface detail;
- seams and controls;
- clothing folds;
- secondary appendages.

### `replace`

Use for source properties that conflict with the style:

- source material -> matte obsidian-black and controlled gold;
- rounded surface treatment -> faceted planes;
- scene lighting -> canonical Obsidian Gold lighting;
- source background -> pure black;
- held or surrounding semantic context -> one fused structural metaphor.

### `remove`

Always consider removing:

- environment;
- floor and pedestal;
- secondary subjects;
- text and logos;
- decorative particles;
- shadows cast onto a ground plane;
- source color palette;
- incidental props;
- realistic surface texture.

### `must_not_add`

Include style-specific risks relevant to the subject, such as:

- extra gold ornaments;
- gemstone details;
- cracks or stone veins;
- UI panels;
- symbols on coins;
- human face detail;
- environment or narrative props;
- additional colors;
- text.

### Fidelity fields

Use the 0-4 scale from `reference-analysis.md` separately:

- `subject_fidelity`: semantic identity and recognition features;
- `silhouette_fidelity`: outer contour, proportions, and pose;
- `composition_fidelity`: source framing and spatial arrangement.

For the canonical single-object conversion, composition fidelity is usually `0` or `1`. It must not preserve an environment or multi-object layout.

## 4. Complex scene reduction

A complex scene is valid only when the contract resolves it to:

- one existing object;
- one generic figure;
- one animal;
- one architectural emblem;
- one fused metaphor.

A fused metaphor must have one continuous silhouette and one dominant semantic reading. A cluster of separate objects is not a fused metaphor.

## 5. Generate mode

In `generate` mode:

- the reference is evidence, not an edit target;
- source pixels, background, lighting, and material are not preserved;
- recognition features and silhouette guidance define fidelity;
- source composition is weak guidance and cannot override the single-object style contract;
- the output may vary in details while remaining semantically recognizable.

## 6. Edit mode

In `edit` mode, add:

```text
change
keep_unchanged
may_vary
remove
must_not_appear
```

The edit target is the source of truth for all `keep_unchanged` fields. Re-state these invariants in every repair instruction. Supplemental references apply only to the declared changed region or property.

## 7. Stop conditions

Do not advance to Scene Specification when:

- the primary subject remains ambiguous;
- recognition features are unknown;
- requested fidelity conflicts with style geometry;
- a multi-object scene cannot be reduced to one continuous object;
- exact text, logo, or likeness is a mandatory success condition;
- confidence is below the level needed to produce an honest contract.
