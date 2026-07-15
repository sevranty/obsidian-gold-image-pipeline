# OGP Release Checklist

## Distribution

- [x] `agents/openai.yaml` matches `SKILL.md` scope.
- [x] Explicit invocation is supported.
- [x] Implicit invocation follows the passing OGP#9 routing baseline.
- [x] Boundary prompts require confirmation.
- [x] No external MCP dependency is declared.
- [x] Pillow is the only Python package dependency.
- [x] Direct bundle contains only the skill directory.
- [x] Repository-only files are rejected.
- [x] Package paths are ASCII-only.
- [x] Hidden caches and compiled artifacts are excluded.
- [x] License travels inside the bundle.
- [x] Archive generation is deterministic.
- [x] Archive layout outside the fixed skill root is rejected.
- [x] Installation smoke test runs all four CLI help commands and one valid prompt check.

## Pending before publication

- [ ] OGP#13 end-to-end pilot PASS.
- [ ] Public README matches the release candidate.
- [ ] Repository cover and social preview PASS.
- [ ] Final closure audit PASS.
- [ ] Separate owner instruction authorizes publication.
