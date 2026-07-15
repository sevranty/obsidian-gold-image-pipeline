# Canonical Runtime Workflow

## Required order

```text
1. Validate that a usable reference or edit target exists.
2. Classify the mode as generate or edit.
3. Assign an explicit role to every input image.
4. Complete the Reference Analysis Card.
5. Select one primary subject or one fused metaphor.
6. Complete the Transformation Contract.
7. Complete the Obsidian Gold Scene Specification.
8. Build the prompt from semantic blocks.
9. Run the pre-generation completeness and contradiction gate.
10. Generate or edit with the available image-generation executor.
11. Inspect the actual output at full size.
12. Inspect the silhouette at 64x64.
13. Apply the critical defect gate and weighted scorecard.
14. Accept, apply one targeted repair, regenerate, or stop.
15. Repeat full QA after every change.
16. Apply the user-visible delivery gate.
17. End only with DELIVERY_READY or an explicit failure state.
```

No stage may be skipped because the raw reference looks simple or the executor reports success.

## Files to read by stage

| Stage | Required reference |
| --- | --- |
| Input and reference analysis | `reference-analysis.md` |
| Transformation planning | `transformation-contract.md`, `style-definition.md` |
| Scene planning | `scene-specification.md`, `style-tokens.md` |
| Prompt construction | `prompt-architecture.md` |
| Generate or edit | `generation-and-iteration.md` |
| Visual review | `visual-quality-assurance.md` |
| Repair | `repair-rules.md` |
| User-visible delivery | `delivery-contract.md` |

## Mode gates

### Generate gate

Proceed only when reference evidence, one selected subject or fused metaphor, all three fidelity fields, and a complete Scene Specification agree.

### Edit gate

Proceed only when one explicit `edit_target`, one requested change, and all `keep_unchanged` invariants are recorded. If subject, silhouette, camera, crop, and material system all require replacement, switch to generate mode rather than pretending the task is a local edit.

## Decision gates

- `ACCEPT`: no critical defect and the QA threshold permits acceptance.
- `REPAIR`: exactly one localized diagnostic category can be changed safely.
- `REGENERATE`: the subject, silhouette, composition, camera, or global style system is wrong, or several categories fail.
- `STOP`: the request is unsupported, the iteration budget is exhausted, or valid visible delivery is impossible.

## Prohibited shortcuts

- Do not prompt directly from the raw reference without a Transformation Contract.
- Do not use the style name as a substitute for explicit visual constraints.
- Do not accept a result because the generation tool succeeded.
- Do not repair multiple unrelated categories in one iteration.
- Do not skip full QA after a repair.
- Do not present an internal path, textual description, SVG, HTML, or CSS as the requested raster result.
- Do not end without `DELIVERY_READY` or an explicit `DELIVERY_MISSING`, `DELIVERY_FAILED`, or `DELIVERY_BLOCKED` statement.