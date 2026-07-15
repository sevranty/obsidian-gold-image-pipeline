---
name: obsidian-gold-image-pipeline
description: Create a new Obsidian Gold image from one or more visual references, or repair an existing Obsidian Gold asset. Trigger for requests to transform a recognizable subject or fused metaphor into one isolated black-and-gold digital sculpture, and for targeted edits that preserve declared identity, silhouette, camera, crop, and compliant style properties. Do not trigger for image analysis without generation, multi-style selection, full narrative scenes, photorealistic product renders, exact text or logo reproduction, exact real-person likeness, or basic crop, resize, and color correction.
---

# Obsidian Gold Image Pipeline

Execute one complete reference-to-image workflow. Do not stop after analysis, prompting, or a successful generation tool call.

## Required workflow

1. Validate that a usable reference or edit target is present.
2. Classify the request as `generate` or `edit`.
3. Assign an explicit role to every input image.
4. Read `references/reference-analysis.md` and complete the Reference Analysis Card.
5. Select one primary subject or one fused metaphor.
6. Read `references/transformation-contract.md` and complete the Transformation Contract.
7. Read `references/style-definition.md`, `references/style-tokens.md`, and `references/scene-specification.md`; complete the Scene Specification.
8. Read `references/prompt-architecture.md`; build a generator-neutral instruction from semantic blocks.
9. Read `references/deterministic-validation.md`; run `scripts/validate_prompt.py`. Do not generate when it exits `2` or `3`.
10. Run the pre-generation completeness and contradiction gate.
11. Read `references/generation-and-iteration.md`; call the available image-generation executor in generate or edit mode.
12. Run `scripts/inspect_image.py` on the actual candidate and create the 64x64 preview.
13. Inspect the actual output at full size and at 64x64.
14. Read `references/visual-quality-assurance.md`; apply the critical gate and weighted scorecard.
15. Accept, perform one targeted repair, regenerate, or stop.
16. After every change, repeat deterministic inspection and the complete visual QA.
17. For an accepted raster, run `scripts/build_manifest.py` and `scripts/package_asset.py`.
18. Read `references/delivery-contract.md`; deliver the accepted final image visibly to the user.

Deterministic script success never replaces visual QA or user-visible delivery confirmation.

## Mode rules

### Generate

Use reference images as evidence. Preserve declared meaning, recognition features, and silhouette guidance. Replace source material, lighting, background, and incidental scene content with the normalized Obsidian Gold system.

### Edit

Use one explicit `edit_target`. State one requested change and repeat every `keep_unchanged` invariant. Use edit only when subject, silhouette, camera, crop, and most compliant properties can remain stable.

## Stop conditions

Stop before generation when:

- no usable image target exists;
- input roles cannot be resolved;
- no defensible primary subject or fused metaphor can be selected;
- the request requires a full environment, exact text, exact logo, or exact real-person identity;
- required fidelity conflicts with mandatory style constraints;
- the Scene Specification is incomplete or contradictory;
- deterministic prompt validation exits `2` or `3`.

Stop after generation when:

- no inspectable image is returned;
- deterministic raster inspection cannot decode the candidate;
- the output cannot be made user-visible;
- two targeted repairs and one full regeneration fail to remove critical defects;
- a repair introduces an equal or more severe critical defect;
- the available executor cannot preserve required edit invariants.

Report the limitation directly. Never claim success without an inspectable and user-visible image.

## Iteration budget

```text
initial generation: 1
targeted repairs: up to 2
full regeneration after failed repairs: 1
```

Each repair addresses one diagnostic category. Preservation constraints may be repeated, but unrelated properties must not be redesigned.

## Definition of Done

The task is complete only when:

- the intended subject or fused metaphor is recognizable;
- the final output passes the critical defect gate;
- the numerical QA verdict permits acceptance;
- the silhouette is readable at 64x64;
- the full-size image has no blocking artifacts;
- deterministic prompt and raster checks have no blocking errors;
- the accepted output has a reproducible manifest and non-destructive package;
- the actual final image is visible or directly accessible in the user response.

A tool success without visible delivery is `DELIVERY_MISSING`, not completion.
