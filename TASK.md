# Current Handoff

## State delta

- Task: OGP#21 WebFactoryOS migration contract.
- Base SHA: `25348669684b5bcf6b0aa8c3c79f466e94e63a42`.
- Branch: `orchestration/ogp-21-webfactoryos-migration`.
- OGP files now record local orchestration decision and responsibility boundaries.
- OGP remains the only implementation source for skill runtime, style contracts, validators, evals, assets, packages and releases.
- WebFactoryOS owns registry, routing, orchestration status and cross-project relations.
- WFO relation never grants write access to OGP.
- WFO availability never blocks OGP runtime, local validation or release candidate work.
- No WFO code, registry copy, naming grammar, workflow or pinned dependency is introduced.

## Evidence

- Local status source: https://github.com/sevranty/obsidian-gold-image-pipeline/issues/1
- Closure debt: https://github.com/sevranty/obsidian-gold-image-pipeline/issues/22
- Active pilot: https://github.com/sevranty/obsidian-gold-image-pipeline/issues/13
- Public docs: https://github.com/sevranty/obsidian-gold-image-pipeline/issues/11
- Cover: https://github.com/sevranty/obsidian-gold-image-pipeline/issues/12
- Remote routing: https://github.com/sevranty/web-factory-os/issues/69
- Naming source of truth: https://github.com/sevranty/web-factory-os/issues/65
- General onboarding: https://github.com/sevranty/web-factory-os/issues/39
- Execution order remains `OGP#13 -> OGP#11 -> OGP#12`.
- PR #20 remains protected current execution.

## Blocker

- None for OGP local docs and handoff.
- WebFactoryOS registry updates remain outside this repository.
