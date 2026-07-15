# OGP#10 Distribution Validation

Status: Owner-review corrections validated; PASS

Validation date: 2026-07-15

Base: `main@a63cf9ee548a5fef14dd8b1ba116c33f981142b8`

## Official format review

Current OpenAI documentation confirms that a skill uses `SKILL.md`, optional metadata belongs in `agents/openai.yaml`, direct skills are discovered from `.agents/skills`, and plugin wrapping is the reusable marketplace layer. OGP v0.1.0 keeps the issue-mandated direct skill bundle and does not invent an external MCP dependency.

## Owner-review findings

| ID | Severity | Finding | Correction |
| --- | --- | --- | --- |
| OR-01 | P1 | Archive or manifest outputs could be written inside the source skill tree. | Builder now rejects every output path inside the source directory. |
| OR-02 | P1 | ZIP layout validation did not explicitly reject cross-platform backslash traversal. | Smoke test validates `PurePosixPath`, absolute paths, parent segments, root prefix, and backslashes. |
| OR-03 | P2 | Metadata parser accepted unknown interface or policy keys. | Parser now enforces supported interface keys and one boolean policy key. |
| OR-04 | P2 | Bundled license was not verified against the repository license. | Builder now requires byte-for-byte equality between root `LICENSE` and bundled `LICENSE.txt`. |

## Validation commands

```bash
python3 -m py_compile \
  scripts/build_skill_package.py \
  scripts/smoke_test_install.py \
  tests/test_distribution.py

python3 -m unittest discover -s tests -p 'test_distribution.py' -v
```

## Results

```text
tests=10
metadata_validation=PASS
implicit_policy_matches_ogp9=True
external_tool_dependencies=0
python_dependencies=1
repository_only_files_rejected=True
deterministic_archive=True
invalid_archive_root_rejected=True
cross_platform_archive_layout_checked=True
outputs_inside_source_rejected=True
unknown_metadata_keys_rejected=True
bundled_license_matches_root=True
cli_help_commands=4
prompt_validation_exit=0
release_published=False
PASS
```

## Boundary

The contract harness uses a clean temporary skill tree with the required layout and metadata contract. The committed tests execute against the full repository checkout when run. OGP#13 repeats the build and smoke test against the final release candidate. No release or tag is published in this task.
