# Prompt Architecture

Prompt schema version: 1.0.0

## 1. Principle

Build prompts from stable semantic blocks. Do not rely on one fixed sentence, the style name, or model-specific flags.

## 2. Generate prompt blocks

Assemble in this order:

1. **Asset and mode**
   - New raster digital sculpture generated from the declared content reference.
2. **Subject and meaning**
   - Primary subject, semantic purpose, and recognition features.
3. **Silhouette and simplification**
   - Outer shape, orientation, key proportions, and removed detail.
4. **Geometry**
   - Subject-specific faceted or parametric plane construction.
5. **Obsidian material**
   - Matte manufactured obsidian-black body with no mineral texture.
6. **Gold system**
   - Declared placement, satin finish, and 15-25% target coverage.
7. **Lighting**
   - Canonical broad soft key and restrained optional gold edge accent.
8. **Composition**
   - One isolated full object with generous negative space.
9. **Background**
   - Uniform pure black with no floor, horizon, gradient, or texture.
10. **Fidelity**
    - Preserve declared recognition and silhouette features.
11. **Remove and forbid**
    - Contract-specific removals plus critical style prohibitions.
12. **Output**
    - Ratio, intended use, and no text or watermark.

## 3. Edit prompt contract

Every edit instruction must contain:

```text
Change:
Keep unchanged:
May vary:
Remove:
Must not appear:
```

`Keep unchanged` must repeat subject identity, silhouette, camera, crop, existing compliant gold placement, and background when these are not the repair target.

## 4. Negative constraints

Express negative constraints as visual outcomes, not unsupported model syntax.

Preferred:

```text
no environment or floor
no stone veins, cracks, or mineral texture
no chrome or mirror reflections
no additional colors
no photorealistic product photography
no text, logo, watermark, or pseudo-text
no cropped object
```

Avoid ambiguous keyword-only lists that could reject valid phrases such as controlled highlights on satin gold.

## 5. Model-specific adapters

Executor-specific flags may be appended only by an adapter and must not change semantic intent. They are not stored as style invariants.

Examples of adapter concerns:

- supported aspect ratio syntax;
- reference-image attachment method;
- edit mask mechanics;
- quality or speed mode;
- output format.

## 6. Prompt preflight

Before generation, verify:

- all required blocks exist;
- no block contradicts another;
- one subject is named consistently;
- gold amount is explicit;
- obsidian is matte and non-mineral;
- background is pure black and environment-free;
- input roles are declared;
- edit invariants are repeated in edit mode;
- no legacy flag is treated as mandatory canon.
