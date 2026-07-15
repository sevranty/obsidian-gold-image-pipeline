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
