# Foundation Manual Validation

Status: Prepared for PR review

Validation date: 2026-07-15

Validated implementation commit: `fabd7cdeb364b4a15fb38e02301ca9eb48a2737a`

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

## Reproducible local checks

The Foundation tree was checked for:

- all required Foundation files;
- UTF-8 readability and final newlines;
- ASCII-only repository content for the current Foundation files;
- absence of organization-specific runtime terms and internal tool names;
- absence of legacy Midjourney version and quality flags in runtime references;
- exact equality between QA diagnostic codes and repair-rule mappings;
- scorecard weights totaling 100;
- presence of core style invariants and Scene Specification fields.

Observed result:

```text
FOUNDATION_VALIDATION
files=24
diagnostic_codes=13
repair_mappings=13
score_weights=100
ascii_only=True
PASS
```

## Git comparison

```text
base: main@9d78ea440717eae80e282fb750a888fb86fe3804
implementation: fabd7cdeb364b4a15fb38e02301ca9eb48a2737a
ahead_by: 1
behind_by: 0
changed_files: 25
additions: 1618
deletions: 1
```

The single deletion is the initial `README.md` line without a trailing newline; its content is unchanged.

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
