# ADR 0001: Mono-style autonomous skill

Status: Accepted

## Context

A universal image pipeline with multiple style packs would require style selection, compatibility resolution, and shared runtime dependencies. The intended operating model favors independent maintenance and transfer between projects.

## Decision

Implement Obsidian Gold as one autonomous mono-style skill. The skill contains its own pipeline rules, style rules, QA, templates, and future deterministic scripts.

No multi-style selector, style registry, or runtime import from a shared template is allowed.

## Consequences

- The skill is portable by copying one installable directory.
- Style changes cannot silently affect other skills.
- Shared improvements must be deliberately ported and revalidated.
- Some pipeline documentation may be structurally similar across repositories, but each repository remains independently versioned.
