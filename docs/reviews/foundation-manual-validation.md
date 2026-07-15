# Foundation Owner Review and Manual Validation

Status: Owner review corrections validated; PR remains Draft

Validation date: 2026-07-15

Review baseline HEAD: `c96bbe244c1cbe5a2eba3098b59a1e3d05630ce5`

Validated content HEAD: `1e10019a4ddb28e9788f00a1756b824b63c1518c`

## Evidence model

The validated content HEAD is the repository state after all functional review fixes and before this evidence file is updated. The evidence update necessarily creates a later envelope commit, so the final PR HEAD is recorded in the PR conversation and PR body after this file is committed. This avoids claiming that a commit contains its own SHA.

## Owner-review findings and dispositions

| ID | Severity | Finding | Disposition |
| --- | --- | --- | --- |
| OR-01 | P1 | Generate-mode precedence was reused for edit mode, allowing a content reference to override edit-target invariants. | Added mode-specific precedence; edit-target `keep_unchanged` invariants now outrank supplemental references. |
| OR-02 | P1 | Reference analysis required composition fidelity, but the Transformation Contract, Scene Specification, and templates omitted it. | Added explicit `composition_fidelity` end to end and completeness checks for all three fidelity values. |
| OR-03 | P1 | Public color tokens replaced canonical source references without a documented normalization decision. | Restored `#FFD700`, `#C7A256`, and `#1A1A1A` provenance; documented derived tonal ranges separately. |
| OR-04 | P1 | `semantic_error` and `subject_error` were conflated, producing ambiguous repair decisions. | Added distinct definitions, split critical-defect rows, and revised semantic repair to reconcile the contract before regeneration. |
| OR-05 | P2 | QA score bands did not specify when multi-category defects require regeneration instead of repair. | Restricted targeted repair to one localized diagnostic category and made the single-change rule explicit in threshold decisions. |
| OR-06 | P2 | Gold below 15% had inconsistent handling and the 15-25% range was treated as fully calibrated. | Marked 15-25% as a provisional target; below-target use requires justification, while above 25% remains critical. |
| OR-07 | P2 | Source-of-truth wording prohibited the execution-oriented restatements already used by schemas and templates. | Defined one authoritative source per rule and allowed non-overriding downstream restatement with mandatory review. |
| OR-08 | P2 | Validation evidence referenced an obsolete implementation snapshot without explaining evidence-envelope semantics. | Replaced it with explicit baseline, validated content HEAD, and envelope-commit model. |

## Structural checks

- [x] Architecture, ADR, runtime references, and templates are separated.
- [x] No multi-style selector or style registry exists.
- [x] Runtime style files contain no organization-specific roles, product matrices, logos, or internal asset paths.
- [x] Legacy Midjourney flags are excluded from normative runtime rules.
- [x] Lighting, background, reflection, color-token, and gold-ratio conflicts are resolved or explicitly deferred for visual calibration.
- [x] Reference analysis is separated from style transformation.
- [x] Complex scenes reduce to one object or fused metaphor.
- [x] Generate and edit precedence rules are distinct.
- [x] Subject, silhouette, and composition fidelity are present across contract, scene schema, and templates.
- [x] Scene Specification is generator-neutral.
- [x] Visual QA includes critical defects, unambiguous diagnostic definitions, score thresholds, and 64x64 review.
- [x] Every diagnostic code has one action-map entry.
- [x] Iteration budget and stop conditions are explicit.
- [x] The image-generation executor remains an execution boundary and does not own style or QA policy.

## Reproducible manual checks

The Foundation tree was checked for:

- all required Foundation files;
- mode-specific reference precedence;
- explicit `subject_fidelity`, `silhouette_fidelity`, and `composition_fidelity` in downstream schemas;
- canonical color references and normalization rationale;
- exact equality between QA diagnostic codes and repair-rule mappings;
- scorecard weights totaling 100;
- critical-defect precedence over numerical score;
- single-category targeted-repair rule;
- absence of legacy generator flags from normative runtime references;
- absence of multi-style routing and organization-specific runtime dependencies.

Observed result:

```text
FOUNDATION_OWNER_REVIEW_VALIDATION
diagnostic_codes=13
repair_mappings=13
score_weights=100
fidelity_fields=3
mode_specific_precedence=True
canonical_color_provenance=True
single_change_thresholds=True
PASS
```

## Git comparison for validated content HEAD

```text
base: main@9d78ea440717eae80e282fb750a888fb86fe3804
validated_content: 1e10019a4ddb28e9788f00a1756b824b63c1518c
ahead_by: 13
behind_by: 0
changed_files: 25
additions: 1728
deletions: 1
```

The single deletion is the initial `README.md` line without a trailing newline; its content is unchanged.

## Residual calibration items

These are not blocking Foundation defects and require visual evidence in #8 and evals in #9:

1. calibrate the provisional 15-25% gold target across object classes;
2. test plane separation produced by the canonical light on pure black;
3. test fused-metaphor rules against cluster drift;
4. calibrate numerical QA thresholds with accepted, repairable, and rejected outputs;
5. keep exact-person preservation outside MVP until separately specified and evaluated.

## Deferred work

The following belongs to later issues:

- `SKILL.md` and trigger description;
- `agents/openai.yaml`;
- deterministic scripts;
- visual anchors and accepted/rejected evidence;
- trigger, workflow, and visual eval suites;
- release packaging and public README.
