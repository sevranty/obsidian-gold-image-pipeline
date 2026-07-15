# Foundation Manual Validation

Status: Prepared for PR review

## Structural checks

- [x] Architecture, ADR, runtime references, and templates are separated.
- [x] No multi-style selector or style registry exists.
- [x] Runtime style files contain no organization-specific roles, product matrices, logos, or internal asset paths.
- [x] Legacy Midjourney flags are excluded from normative runtime rules.
- [x] Lighting, background, reflection, and gold-ratio conflicts are resolved.
- [x] Reference analysis is separated from style transformation.
- [x] Complex scenes reduce to one object or fused metaphor.
- [x] Generate and edit contracts are distinct.
- [x] Scene Specification is generator-neutral.
- [x] Visual QA includes critical defects, diagnostic codes, score thresholds, and 64 px review.
- [x] Every diagnostic code has a repair action.
- [x] Iteration budget and stop conditions are explicit.

## Manual review focus

Owner review should challenge:

1. whether 15-25% gold is appropriate for every subject class;
2. whether the canonical light creates enough separation on pure black;
3. whether fused metaphors are constrained enough to avoid object clusters;
4. whether score thresholds need calibration after the first visual evidence set;
5. whether exact-person handling should remain outside MVP.

## Deferred work

The following belongs to later issues:

- `SKILL.md` and trigger description;
- `agents/openai.yaml`;
- deterministic scripts;
- visual anchors and accepted/rejected evidence;
- trigger, workflow, and visual eval suites;
- release packaging and public README.
