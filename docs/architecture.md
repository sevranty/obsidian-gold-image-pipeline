# Obsidian Gold Image Pipeline Architecture

Status: Foundation baseline

## 1. Purpose

`obsidian-gold-image-pipeline` is a self-contained mono-style Agent Skill. It transforms one or more visual references into one new raster image representing a single isolated Obsidian Gold digital sculpture.

The skill owns analysis, transformation planning, style enforcement, quality assessment, repair decisions, and user-visible delivery. The image generation tool owns raster generation or editing.

## 2. Scope

The Foundation supports two modes:

1. `generate`: create a new Obsidian Gold object from a visual reference.
2. `edit`: repair or change an existing Obsidian Gold asset while preserving declared invariants.

The canonical output is:

- one dominant object or one unified visual metaphor;
- isolated on a pure black background;
- faceted, low-poly, or parametrically planar;
- primarily matte obsidian-black;
- accented with controlled gold targeting 15-25% of visible object area, with any below-target exception documented;
- legible as a silhouette when fitted inside 64x64 px;
- square by default unless the downstream use explicitly requires another ratio.

## 3. Non-goals

The Foundation does not provide:

- multi-style selection or routing;
- full-scene preservation;
- environmental backgrounds, interiors, landscapes, or narrative staging;
- photorealistic product rendering;
- exact identity preservation for a real person;
- reliable text, logo, or trademark reproduction inside the generated object;
- a custom image-generation API client;
- automatic aesthetic scoring by computer vision;
- automatic best-of-N selection without visual review;
- SVG, HTML, or CSS substitutes for a requested raster image.

## 4. Runtime boundaries

```text
reference image(s)
  -> input validation
  -> reference role assignment
  -> reference analysis
  -> primary subject or metaphor selection
  -> transformation contract
  -> scene specification
  -> prompt construction
  -> pre-generation gate
  -> image generation or edit
  -> visual inspection
  -> diagnostic classification
  -> targeted repair or regeneration
  -> final visual and technical gate
  -> user-visible delivery
```

### Pipeline core

The pipeline core contains:

- input and mode classification;
- reference analysis;
- transformation contract;
- scene specification;
- generation and repair control;
- final delivery requirements.

### Style core

The style core contains:

- semantic tone;
- geometry;
- materials;
- gold placement and ratio;
- lighting;
- background and composition;
- mandatory invariants and rejection rules.

### Executor boundary

The installed image-generation capability performs `generate` or `edit`. It does not decide the subject, style policy, quality threshold, or repair strategy.

## 5. Repository layout

```text
README.md
LICENSE
CONTRIBUTING.md

docs/
  architecture.md
  dependency-map.md
  source-normalization.md
  decisions/
  reviews/

skill/
  obsidian-gold-image-pipeline/
    SKILL.md
    agents/
      openai.yaml
    references/
      workflow.md
      style-definition.md
      style-tokens.md
      reference-analysis.md
      transformation-contract.md
      scene-specification.md
      prompt-architecture.md
      generation-and-iteration.md
      visual-quality-assurance.md
      repair-rules.md
      delivery-contract.md
    assets/
      anchors/
      templates/
    scripts/

evals/
examples/
reports/
```

Only `skill/obsidian-gold-image-pipeline/` is intended for installation. Repository-level documentation, research, reports, and large evaluation corpora remain outside the runtime package.

## 6. Source-of-truth map

| Concern | Authoritative location |
| --- | --- |
| Scope, boundaries, component responsibilities | `docs/architecture.md` |
| Architectural rationale | `docs/decisions/` |
| Normalized visual invariants | `skill/obsidian-gold-image-pipeline/references/style-definition.md` |
| Concrete color, material, light, and ratio values | `skill/obsidian-gold-image-pipeline/references/style-tokens.md` |
| How to inspect references | `skill/obsidian-gold-image-pipeline/references/reference-analysis.md` |
| What is preserved, simplified, removed, or replaced | `skill/obsidian-gold-image-pipeline/references/transformation-contract.md` |
| Generator-neutral desired output | `skill/obsidian-gold-image-pipeline/references/scene-specification.md` |
| Prompt block construction | `skill/obsidian-gold-image-pipeline/references/prompt-architecture.md` |
| Generate, edit, iteration, and stop rules | `skill/obsidian-gold-image-pipeline/references/generation-and-iteration.md` |
| Acceptance and rejection | `skill/obsidian-gold-image-pipeline/references/visual-quality-assurance.md` |
| Error-specific corrective actions | `skill/obsidian-gold-image-pipeline/references/repair-rules.md` |
| Runtime ordering | `skill/obsidian-gold-image-pipeline/references/workflow.md` |

A normative rule has one authoritative definition. Downstream schemas and templates may repeat a value for execution, but they must not redefine it and must be reviewed whenever the authoritative source changes.

## 7. Failure and stop model

The pipeline stops before generation when:

- no usable image target is available;
- the reference role cannot be resolved;
- no primary subject or coherent metaphor can be selected with sufficient confidence;
- the request requires a prohibited full scene, exact text, exact logo, or exact real-person identity;
- the requested output contradicts mandatory style invariants.

The pipeline stops after generation when:

- the generation tool returns no usable image;
- the output cannot be inspected;
- two targeted repairs and one full regeneration fail to remove critical defects;
- a repair introduces an equal or more severe critical defect;
- the result cannot be made user-visible.

The final response reports the limitation rather than claiming success.

## 8. Version boundaries

The following versions evolve independently:

- `skill_version`;
- `style_core_version`;
- `prompt_schema_version`;
- `qa_schema_version`;
- `manifest_schema_version`.

Foundation baseline values:

```text
style_core_version: 1.0.0
prompt_schema_version: 1.0.0
qa_schema_version: 1.0.0
```

## 9. Definition of Done for Foundation

Foundation is complete when:

- architecture and dependencies are explicit;
- style conflicts are resolved into one normative core;
- reference analysis produces a complete transformation contract;
- subject, silhouette, and composition fidelity remain explicit across schemas;
- scene specification is generator-neutral;
- generate and edit contracts are distinct;
- visual QA has critical defects, score thresholds, and unambiguous diagnostic codes;
- every diagnostic code maps to a repair action;
- runtime files contain no brand-specific organizational dependencies;
- no required stage can be skipped by a future `SKILL.md`.

## 10. WebFactoryOS orchestration boundary

- OGP owns skill code, style contracts, validators, evals, assets, packages and releases in this repository.
- WebFactoryOS owns project registry, routing, orchestration status and cross-project relations outside this repository.
- Remote routing is tracked by WFO#69: https://github.com/sevranty/web-factory-os/issues/69
- Naming is sourced from WFO#65: https://github.com/sevranty/web-factory-os/issues/65
- OGP does not copy the WebFactoryOS registry or naming grammar.
- A WebFactoryOS relation never grants write access to OGP.
- OGP build, validation and release candidate work remain local and autonomous.
- WebFactoryOS availability never blocks OGP runtime or local validation.
