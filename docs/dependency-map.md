# Foundation Dependency Map

## Issue dependency graph

```text
#1 Architecture and orchestration
 |
 +--> #2 Style core normalization
 |      |
 |      +--> #4 Reference analysis and transformation contract
 |              |
 |              +--> #5 Scene specification and imagegen contract
 |                      |
 |                      +--> #6 Visual QA and targeted repair
 |
 +--> #3 Canonical SKILL.md (after #2, #4, #5; close after #6)
 +--> #7 Deterministic validation (after #2, #5, #6)
 +--> #8 Evidence set (after #2, #6)
 +--> #9 Evals (after #3, #4, #5, #6, #8)
 +--> #10 Distribution (after #3, #7, #9)
 +--> #13 Pilot (after #3-#10)
 +--> #11 README (after working release candidate)
 +--> #12 Project cover (after style evidence and README direction)
```

## File dependency graph

```text
style-definition.md
  +--> style-tokens.md
  +--> transformation-contract.md
  +--> scene-specification.md
  +--> visual-quality-assurance.md

reference-analysis.md
  +--> transformation-contract.md
          +--> scene-specification.md
                  +--> prompt-architecture.md
                          +--> generation-and-iteration.md
                                  +--> visual-quality-assurance.md
                                          +--> repair-rules.md

workflow.md
  +--> all runtime references above
```

## Change impact rules

| Changed artifact | Mandatory downstream review |
| --- | --- |
| `style-definition.md` | tokens, scene spec, prompt, QA, evidence, visual evals |
| `style-tokens.md` | prompt, QA, technical validators, manifests |
| `reference-analysis.md` | transformation contract, workflow and workflow evals |
| `transformation-contract.md` | scene spec, prompt and workflow evals |
| `scene-specification.md` | prompt, generation contract and examples |
| `prompt-architecture.md` | prompt validation and generation fixtures |
| `visual-quality-assurance.md` | repair rules, scorecards, evidence labels and visual evals |
| `repair-rules.md` | iteration tests and pilot reports |

## Merge order

Foundation may be delivered in one PR because the repository is empty and the files form one mutually consistent baseline. Future modifications should use one issue and one focused PR per concern unless an atomic cross-file schema migration is required.

## WebFactoryOS orchestration links

- OGP#1 remains the local project status source: https://github.com/sevranty/obsidian-gold-image-pipeline/issues/1
- OGP#22 owns overall product closure independently of registry work: https://github.com/sevranty/obsidian-gold-image-pipeline/issues/22
- OGP#21 owns the local handoff contract: https://github.com/sevranty/obsidian-gold-image-pipeline/issues/21
- The OGP#21 implementation is merged through PR #24: https://github.com/sevranty/obsidian-gold-image-pipeline/pull/24
- WFO#69 owns reciprocal remote routing only: https://github.com/sevranty/web-factory-os/issues/69
- WFO#102 and PR #103 completed the remote OGP registry record and relation.
- WFO#65 remains the naming source of truth without copying its grammar into OGP: https://github.com/sevranty/web-factory-os/issues/65
- WFO#39 remains shared onboarding context, not copied implementation: https://github.com/sevranty/web-factory-os/issues/39
- OGP owns runtime dependencies, validation, package contents and release candidates.
- WebFactoryOS owns registry, routing status and cross-project relations.
- Relation `WFO-069__OGP-021` grants no write access to OGP.
- OGP#13, OGP#11 and OGP#12 remain separate product scopes and are not changed by OGP#21 closure.
- PR #20 is historical pilot implementation evidence and is not modified by OGP#21 closure.
