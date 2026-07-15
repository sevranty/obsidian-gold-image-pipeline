# OGP Release Process

## Version model

The canonical version matrix is `skill/obsidian-gold-image-pipeline/VERSIONS.json`.

- skill: runtime behavior version;
- style core: Obsidian Gold visual contract;
- prompt schema: semantic prompt blocks;
- QA schema: critical gate and weighted scorecard;
- manifest schema: packaged asset manifest;
- tool contract: deterministic CLI behavior;
- distribution contract: install bundle structure;
- release candidate: current pre-release identifier.

## Build

```bash
python3 scripts/build_skill_package.py \
  --skill-dir skill/obsidian-gold-image-pipeline \
  --output-zip /tmp/ogp-dist/obsidian-gold-image-pipeline.zip \
  --manifest /tmp/ogp-dist/package-manifest.json
```

The archive contains one root directory named `obsidian-gold-image-pipeline`. It can be extracted to `.agents/skills/`.

## Smoke test

```bash
python3 scripts/smoke_test_install.py \
  --archive /tmp/ogp-dist/obsidian-gold-image-pipeline.zip \
  --manifest /tmp/ogp-dist/package-manifest.json \
  --report /tmp/ogp-dist/install-smoke.json
```

## Release gates

1. OGP#8 corpus PASS.
2. OGP#9 eval baseline PASS.
3. OGP#10 deterministic bundle and installation smoke PASS.
4. OGP#13 five-case pilot PASS, with at least four accepted final cases.
5. OGP#11 public documentation matches the candidate.
6. OGP#12 public cover uses only approved source material.
7. Final closure audit confirms no open blocking issue or PR.
8. Publication requires a separate direct owner instruction.

No Git tag, GitHub Release, marketplace submission, or public binary is created by OGP#10.
