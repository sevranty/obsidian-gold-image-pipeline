# Contributing

This repository is a focused Agent Skill, not a general image-generation framework. Contributions must preserve the mono-style scope, deterministic evidence boundaries, and separation between repository documentation and the installed skill bundle.

## Before starting

1. Read the relevant GitHub Issue and its dependencies.
2. Resolve exact current `main` immediately before creating a branch.
3. Search open Issues, Pull Requests, and branches for an active equivalent contour.
4. Stop when an active duplicate exists.
5. Use one Issue, one focused branch, and one Pull Request per concern.
6. Do not write directly to `main`.

## Scope boundaries

### Repository-level files

Repository documentation, research, reports, evaluation fixtures, and release-candidate evidence remain outside the installed skill bundle.

Examples:

- `README.md`
- `CONTRIBUTING.md`
- `docs/`
- `evals/`
- `examples/`
- `reports/`
- `dist/ogp-skill-manifest.json`

### Installed skill files

Only this directory is intended for installation:

```text
skill/obsidian-gold-image-pipeline/
```

Do not add repository-only files such as `README.md` or a `docs/` tree inside the installed skill directory. The package builder rejects them.

## Change classes

### Public documentation

Public documentation must:

- describe only behavior verified by merged runtime, evaluation, package, and pilot evidence;
- link normative runtime files instead of copying them;
- distinguish deterministic contract validation from live image-generator aesthetic quality;
- state the current release status accurately;
- avoid unsupported marketing claims;
- preserve provenance for every visual example;
- keep OGP#12 cover and social-preview scope separate from OGP#11 README scope.

### Runtime contracts

Runtime changes must preserve the required workflow order in `SKILL.md` and the source-of-truth map in `docs/architecture.md`.

A normative rule should have one authoritative definition. Review all dependent schemas, templates, scripts, fixtures, and reports when changing an authoritative value.

### Deterministic scripts

Scripts must:

- use ASCII-only repository paths;
- fail explicitly on invalid input;
- produce stable machine-readable output where a contract already exists;
- avoid silent fallbacks that convert a failure into an apparent success;
- keep source files and generated outputs separate;
- reject destructive or path-traversal behavior;
- preserve non-destructive packaging and delivery.

### Visual evidence

Visual evidence must:

- use self-authored or explicitly permitted source material;
- record reference provenance and rights notes;
- preserve prompt, transformation, QA, export, and checksum evidence;
- avoid third-party logos, private FDS material, personal data, or unsupported claims;
- remain inspectable at full size and at 64x64;
- never treat tool success as visual acceptance.

## Development setup

Install the declared raster dependency:

```bash
python3 -m pip install -r skill/obsidian-gold-image-pipeline/requirements.txt
```

The repository currently declares `Pillow>=10.0,<13.0`.

## Validation

Run checks appropriate to the changed scope.

### Full repository tests

```bash
python3 -m unittest discover -s tests -v
```

### Prompt and script syntax

```bash
python3 -m py_compile scripts/build_skill_package.py scripts/smoke_test_install.py tests/test_distribution.py
```

### Deterministic package build

```bash
python3 scripts/build_skill_package.py \
  --archive /tmp/ogp-skill.zip \
  --manifest /tmp/ogp-skill-manifest.json
```

### Clean-install smoke

```bash
python3 scripts/smoke_test_install.py \
  --archive /tmp/ogp-skill.zip \
  --manifest /tmp/ogp-skill-manifest.json \
  --report /tmp/ogp-install-smoke.json
```

### Evaluation baseline

```bash
python3 scripts/run_evals.py \
  --output /tmp/ogp-baseline.json \
  --raw-output /tmp/ogp-raw-results.json
```

A Pull Request must not claim CI, live generator quality, or successful visual delivery unless exact evidence exists for its immutable HEAD.

## Documentation review checklist

- [ ] The first screen explains the project without reading `SKILL.md`.
- [ ] Scope and non-goals match `docs/architecture.md`.
- [ ] Generate and edit modes remain distinct.
- [ ] Commands match the current script interfaces.
- [ ] Version and release status match `VERSIONS.json` and the package manifest.
- [ ] Deterministic pilot results are not presented as live aesthetic proof.
- [ ] Normative values are linked, not redefined.
- [ ] Visual examples have provenance or are explicitly withheld.
- [ ] All paths are ASCII-only.
- [ ] No OGP#12 asset work is mixed into an OGP#11 documentation PR.

## Pull Request contract

A Pull Request should include:

- the linked Issue;
- exact base SHA;
- exact head SHA after the final commit;
- changed-file list;
- scope and protected resources;
- commands executed and their exact results;
- evidence gaps and limitations;
- confirmation that no release, tag, settings change, deployment, or publication occurred.

Keep a Pull Request in Draft while evidence is incomplete. Perform review on the immutable exact HEAD. Correct all P0-P3 findings before Ready or merge.

## Release protection

A contribution must not create or publish:

- a Git tag;
- a GitHub Release;
- a marketplace submission;
- a public binary or archive;
- a production deployment;
- DNS or repository settings changes.

Publication requires a separate direct owner instruction after all release gates pass.

## License

Contributions are accepted under the repository MIT License. The root `LICENSE` and installed bundle `skill/obsidian-gold-image-pipeline/LICENSE.txt` must remain byte-identical.
