# ADR 0002: Reduce references to one object or fused metaphor

Status: Accepted

## Context

Obsidian Gold relies on isolation, negative space, and icon-grade silhouette. Literal preservation of complex references produces environments, secondary subjects, text, and material noise.

## Decision

Every generation selects one primary subject or one fused visual metaphor. Secondary subjects, original environments, incidental text, and nonessential details are removed unless they are structurally necessary recognition features of the primary subject.

When several subjects are equally important, the pipeline must either:

1. select one using the user goal and salience rules;
2. fuse them into one coherent emblematic object;
3. stop and report ambiguity if neither result is defensible.

## Consequences

- The output preserves meaning rather than full scene layout.
- Exact documentary reconstruction is outside scope.
- Reference analysis becomes mandatory before prompting.
- QA can reject multi-object drift consistently.
