# ADR 0003: Separate pipeline policy from image generation execution

Status: Accepted

## Context

Image models and execution surfaces change independently from style methodology. Embedding model APIs or flags in the style skill would create brittle coupling.

## Decision

The Obsidian Gold skill owns:

- reference interpretation;
- transformation and scene contracts;
- prompt intent;
- pre-generation validation;
- visual inspection;
- repair decisions;
- user-visible delivery.

The available image-generation capability owns raster generation or editing. The executor receives a complete generator-neutral specification translated into the tool's supported instruction format.

## Consequences

- The skill remains portable across ChatGPT, Codex, and future executors.
- Model-specific parameters are optional adapter concerns.
- A successful generation call is not a quality pass.
- The skill must inspect the actual output and may request a targeted edit or regeneration.
