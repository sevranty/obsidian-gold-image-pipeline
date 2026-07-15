# ADR 0005: Gold highlight and reflection policy

Status: Accepted

## Context

Legacy deny lists rejected the word `reflection`, while material rules also described gold as polished or satin. Literal enforcement created a contradiction.

## Decision

Gold is satin by default. Small, controlled specular highlights are allowed when they describe the object's form. The following are rejected:

- mirror-like reflection;
- chrome finish;
- reflected environment or visible studio setup;
- large white hotspots;
- multiple sharp streaks;
- jewelry-render sparkle;
- HDR bloom.

Polished gold is allowed only for a very small semantic insert and must still pass the same rejection rules.

## Consequences

- Prompt validation must be contextual rather than keyword-only.
- Visual QA distinguishes controlled highlights from reflected scenes.
- Obsidian and gold use different reflectance policies.
