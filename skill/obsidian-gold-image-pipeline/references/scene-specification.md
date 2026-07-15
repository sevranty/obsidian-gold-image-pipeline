# Obsidian Gold Scene Specification

Prompt schema version: 1.0.0

## 1. Purpose

The Scene Specification is the generator-neutral description of the intended output. It is derived from the Transformation Contract and style core.

## 2. Required schema

```text
mode
asset_type
primary_subject
semantic_meaning
recognition_features
silhouette
pose_or_orientation
camera
geometry
materials
obsidian_finish
gold_placement
gold_ratio
lighting
background
composition
negative_space
subject_fidelity
silhouette_fidelity
composition_fidelity
must_preserve
must_remove
must_not_add
output_ratio
output_usage
input_image_roles
```

## 3. Field constraints

### Mode

- `generate`: new image based on reference evidence.
- `edit`: change an existing Obsidian Gold image.

### Asset type

Use one:

- `icon_grade_object`;
- `digital_sculpture`;
- `hero_object`.

All asset types remain isolated single objects. `hero_object` does not permit an environment.

### Camera

Default to a front three-quarter view at neutral eye level. Change only when another angle preserves recognition better.

Avoid:

- extreme wide-angle distortion;
- cinematic environmental framing;
- macro crop;
- top-down view that destroys silhouette;
- camera motion.

### Geometry

Specify subject-specific planar simplification while retaining recognition features. Do not use generic `low-poly` as the only geometry instruction.

### Materials

Specify which structural areas are obsidian and which areas receive gold. Gold placement must have semantic or compositional purpose.

### Fidelity

Copy the three fidelity values from the Transformation Contract without collapsing them:

- `subject_fidelity` controls semantic identity and recognition features;
- `silhouette_fidelity` controls contour, proportion, and pose;
- `composition_fidelity` controls source framing only and cannot preserve an environment or multi-object arrangement.

### Lighting

Use the canonical model from ADR 0004 and `style-tokens.md`.

### Background

Always specify pure black, uniform, textureless, without horizon or floor.

### Output ratio

Default `1:1`. Use another ratio only when user-delivery constraints require it. The object must remain fully visible with ample negative space.

## 4. Completeness gate

A Scene Specification is incomplete when it lacks:

- a single primary subject;
- at least two recognition features when available;
- silhouette guidance;
- explicit obsidian and gold placement;
- gold ratio target;
- all three fidelity values;
- canonical lighting;
- pure black background;
- remove and must-not-add constraints;
- input image roles;
- output ratio and usage.

Do not call the image-generation executor with an incomplete specification.
