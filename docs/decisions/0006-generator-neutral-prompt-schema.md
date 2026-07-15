# ADR 0006: Generator-neutral prompt schema

Status: Accepted

## Context

Legacy production prompts embedded Midjourney version and quality flags. These are not portable and can become invalid without a style change.

## Decision

The canonical input to generation is a structured Scene Specification. Prompt text is assembled from semantic blocks. Aspect ratio, input roles, edit intent, and output usage are explicit fields.

Model-specific flags may exist only in executor adapters or historical examples. They are never required style invariants.

## Consequences

- The same Foundation can target different image tools.
- Prompt validation checks meaning and contradictions, not exact phrases.
- Prompt schema and style core can be versioned separately.
