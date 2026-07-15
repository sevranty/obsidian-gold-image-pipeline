# Foundation Workflow

## Required order

```text
1. Validate that a usable reference or edit target exists.
2. Classify the mode as generate or edit.
3. Assign a role to every input image.
4. Complete the Reference Analysis Card.
5. Select one primary subject or one fused metaphor.
6. Complete the Transformation Contract.
7. Complete the Obsidian Gold Scene Specification.
8. Build the prompt from semantic blocks.
9. Run the pre-generation completeness and contradiction gate.
10. Generate or edit with the available image-generation executor.
11. Inspect the actual output at full size.
12. Inspect the silhouette at 64 px.
13. Apply the critical defect gate and weighted scorecard.
14. Accept, apply one targeted repair, regenerate, or stop.
15. Repeat full QA after every change.
16. Confirm the final image is user-visible.
```

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

## Prohibited shortcuts

- Do not prompt directly from the raw reference without a Transformation Contract.
- Do not accept a result because the generation tool succeeded.
- Do not repair multiple unrelated categories in one iteration.
- Do not end without a user-visible image or an explicit failure statement.
