# Analogous Skills Analysis

Status: OGP#11 public documentation research

Reviewed: 2026-07-23

Exact OGP baseline: `517d40932a413b80d2a825629b7c21b12723c344`

## Purpose

Compare current official Agent Skills guidance and a small set of public implementations before writing the OGP public README.

The analysis is limited to documentation structure, skill packaging, trigger boundaries, progressive disclosure, validation, and evidence language. It does not evaluate or copy visual style, prompt wording, brand identity, or generated images from another project.

## Selection criteria

A source was included when it met at least one condition:

- official OpenAI product or repository guidance;
- official implementation of the Agent Skills open standard;
- mono-purpose skill with a clear trigger and narrow output contract;
- explicit separation of instructions, scripts, references, assets, and public documentation;
- explicit testing, validation, or limitation language.

Community listicles, generated rankings, marketing pages without implementation detail, and unverified image-quality claims were excluded.

## Sources

| Source | Type | Relevant pattern | URL |
| --- | --- | --- | --- |
| OpenAI Skills in ChatGPT | Official product guidance | Skills are reusable workflows with instructions, examples, and code; OpenAI Skills follow the Agent Skills open standard | https://help.openai.com/en/articles/20001066 |
| `openai/skills` catalog | Official OpenAI repository | Skills are distributed as focused folders; system, curated, and experimental scopes are separated | https://github.com/openai/skills |
| OpenAI `skill-creator` | Official OpenAI skill | Required `SKILL.md`, optional `agents`, `scripts`, `references`, and `assets`; progressive disclosure; concise runtime instructions | https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md |
| OpenAI `imagegen` sample | Official OpenAI Codex sample | Explicit generate/edit trigger, bitmap output boundary, and non-trigger cases for vector or code-native work | https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/imagegen/SKILL.md |
| OpenAI `doc` skill | Official mono-purpose skill | Short task-focused workflow, deterministic helper preference, and format-specific validation | https://github.com/openai/skills/blob/main/skills/.curated/doc/SKILL.md |
| OpenAI `cli-creator` skill | Official mono-purpose skill | Durable tool versus one-off script distinction; companion skill stays focused on safe execution order | https://github.com/openai/skills/blob/main/skills/.curated/cli-creator/SKILL.md |
| Anthropic skills repository | Official public implementation | Self-contained skill folders, examples across task classes, and explicit warning to test before critical use | https://github.com/anthropics/skills |
| Anthropic `skill-creator` | Official public skill | Trigger description is primary; iterative evaluation and benchmark evidence are first-class work | https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md |
| GitHub Agent Skills documentation | Official platform documentation | Agent Skills are an open standard; project and personal skill locations can differ by agent surface | https://docs.github.com/en/copilot/concepts/agents/about-agent-skills |
| MicrosoftDocs Agent Skills | Official public repository | Progressive disclosure, official-source grounding, and scenario-based acceptance tests | https://github.com/MicrosoftDocs/Agent-Skills |

## Comparison matrix

| Concern | Observed pattern | OGP decision |
| --- | --- | --- |
| Public entry point | Repository README explains purpose, installation, evidence, and contribution | Adopt at repository root |
| Installed bundle | Runtime skill remains a focused self-contained folder | Adopt; only `skill/obsidian-gold-image-pipeline/` is installed |
| Triggering | Name and description state what the skill does and when not to use it | Adopt in `SKILL.md` and summarize in README |
| Progressive disclosure | Core ordering stays in `SKILL.md`; details move to one-level references | Adopt; do not duplicate reference contracts in README |
| Modes | Narrow skills separate materially different execution paths | Adopt explicit `generate` and `edit` modes |
| Output type | Image skill distinguishes bitmap generation from SVG or code-native output | Adopt raster-only output boundary |
| Scripts | Deterministic repeated operations belong in scripts | Adopt prompt validation, raster inspection, manifest, packaging, build, smoke, and eval scripts |
| Assets | Runtime templates and anchors stay inside the skill; public evidence stays outside | Adopt |
| Validation | Test exact behavior and keep evidence machine-readable | Adopt reports, manifests, checksums, eval fixtures, and clean-install smoke |
| Limitations | Public examples warn that repository behavior can differ from product behavior and must be tested | Adopt direct evidence boundaries |
| Installation paths | Agent products may use different supported skill directories | Do not claim one universal path; document the repository smoke layout and defer to the target agent |
| Visual quality | No reviewed source provides a universal automatic aesthetic guarantee | Reject automatic quality claims; require manual visual QA |
| Product documentation inside skill | OpenAI `skill-creator` discourages auxiliary README files inside the installed skill | Adopt repository-level README only; package builder rejects installed `README.md` and `docs/` |
| Broad catalog behavior | Catalog repositories contain many independent skills | Reject for OGP runtime; OGP remains one mono-style skill |
| Custom generator client | Image examples rely on an available executor rather than making every skill a platform client | Adopt executor boundary; reject bundled image API client |

## Decisions adopted for OGP

### 1. Keep the installed skill small

The installed directory contains the runtime entry point, product metadata, references, runtime assets, scripts, versions, requirements, and bundled license.

Repository research, public documentation, reviews, reports, large eval fixtures, and release-candidate evidence remain outside the bundle.

Reason:

- runtime context stays focused;
- package contents remain deterministic;
- public documentation can evolve without changing installed behavior;
- repository provenance and review records do not consume skill context.

### 2. Use progressive disclosure

`SKILL.md` defines required order, mode gates, stop conditions, iteration budget, and Definition of Done.

Detailed contracts remain in directly linked files under `references/`:

- reference analysis;
- transformation contract;
- style definition and tokens;
- scene specification;
- prompt architecture;
- generation and iteration;
- visual QA and repair;
- delivery.

The README describes the map and links the source files. It does not copy their normative values into a second source of truth.

### 3. State trigger and non-trigger boundaries early

The first README screen explains:

- one isolated Obsidian Gold object;
- generate or edit mode;
- raster output;
- required reference or edit target;
- no full scene, exact identity, exact text, logo reproduction, or generic image editing.

Reason:

A narrow public contract prevents the skill from being interpreted as a general image generator or multi-style framework.

### 4. Separate deterministic evidence from aesthetic evidence

OGP has committed deterministic evidence for:

- package structure;
- checksums;
- clean installation;
- CLI availability;
- prompt validation;
- trigger and workflow fixtures;
- failure-path behavior;
- visible-delivery records;
- manual visual-rubric contracts.

The committed pilot explicitly does not claim live third-party generator aesthetic success.

The README therefore reports:

```text
Deterministic pilot evidence: PASS
Live image-generator aesthetic claim: not established
GitHub Actions claim: none
Release published: false
```

### 5. Keep visual publication separate

OGP#11 creates public text documentation.

OGP#12 owns:

- repository cover benchmark;
- concept exploration;
- selected self-authored or permitted source;
- source manifest;
- visual QA;
- exports and checksums;
- README hero and social preview integration.

The OGP#11 README must not fabricate a before-and-after gallery from deterministic fixtures. It states that no public visual comparison is claimed yet.

### 6. Document one tested package shape without claiming universal installation

The repository smoke test extracts:

```text
.agents/skills/obsidian-gold-image-pipeline
```

Official product and platform documentation shows that supported project and personal skill locations can vary. The README documents the smoke-tested shape and tells the user to use the supported directory for the target agent.

### 7. Keep the executor boundary explicit

OGP owns:

- reference analysis;
- transformation planning;
- style constraints;
- prompt structure;
- deterministic checks;
- visual QA decisions;
- repair policy;
- manifest and delivery contract.

The available image-generation capability owns raster generation or editing.

OGP does not bundle a custom image-generation API client and does not infer generator quality from tool success.

## Decisions consciously not adopted

### Generic multi-skill catalog navigation

Not adopted because OGP is one skill and one style. Catalog-level categories, installation menus, and cross-skill routing would blur scope.

### README inside the installed skill

Not adopted because repository-level documentation is not runtime instruction. The package builder rejects an installed `README.md` and `docs/` tree.

### Automatic aesthetic scoring

Not adopted because current evidence uses a manual rubric and deterministic structural checks. No reliable automatic aesthetic acceptance is claimed.

### Best-of-N generation as default behavior

Not adopted because the runtime has a bounded initial generation, targeted repair, and regeneration budget. Unbounded sampling would weaken evidence and cost control.

### Exact face, logo, or text preservation

Not adopted because the current contracts explicitly stop or reduce such requests. Public documentation must not imply capabilities that the eval and pilot do not establish.

### Published release language

Not adopted because `0.1.0-rc.1` is a release candidate with `release_published: false`. A tag, GitHub Release, marketplace submission, or public binary requires a separate owner instruction.

## OGP evidence used by the README

| Evidence | Purpose |
| --- | --- |
| `skill/obsidian-gold-image-pipeline/SKILL.md` | Runtime workflow and completion contract |
| `skill/obsidian-gold-image-pipeline/agents/openai.yaml` | Public display name, short description, and default prompt |
| `skill/obsidian-gold-image-pipeline/VERSIONS.json` | Skill and release-candidate versions |
| `docs/architecture.md` | Scope, non-goals, repository layout, and executor boundary |
| `reports/ogp9-baseline.json` | Static trigger, workflow, failure, and visual-rubric metrics |
| `reports/ogp13-pilot.json` | Deterministic pilot status and limitations |
| `docs/reviews/ogp13-pilot-validation.md` | Human-readable pilot evidence |
| `reports/ogp13-install-smoke.json` | Clean-install smoke result |
| `dist/ogp-skill-manifest.json` | Package contents, checksums, release-candidate status |
| `scripts/build_skill_package.py` | Current build argument contract and package exclusions |
| `scripts/smoke_test_install.py` | Current install shape and smoke checks |

## Documentation gaps retained intentionally

The following items are not represented as completed:

- a public before-and-after image;
- approved repository cover and social preview;
- live third-party generator aesthetic benchmark;
- exact-HEAD GitHub Actions evidence for the current documentation branch;
- published release or marketplace installation.

These gaps must remain visible until their owning tasks provide exact evidence.

## Result

The selected pattern for OGP is:

```text
repository README
  -> narrow public contract
  -> evidence and limitations
  -> links to normative runtime sources

installed skill
  -> concise SKILL.md
  -> one-level references
  -> deterministic scripts
  -> runtime templates and anchors

release candidate
  -> reproducible package
  -> manifest and checksums
  -> clean-install smoke
  -> no publication without owner instruction
```

This structure matches the current Agent Skills ecosystem while preserving OGP's stricter evidence, visual QA, provenance, and publication boundaries.
