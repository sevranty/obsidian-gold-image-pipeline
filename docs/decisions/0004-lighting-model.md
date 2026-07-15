# ADR 0004: Canonical lighting model

Status: Accepted

## Context

Legacy descriptions alternated between frontal light, rim light, point light, and ultra-minimal lighting. Uncontrolled combinations create chrome, HDR, or unreadable black forms.

## Decision

Use one canonical lighting system:

- one broad, soft key light;
- positioned slightly above and 15-30 degrees off camera axis;
- low-to-moderate intensity;
- enough tonal separation to reveal faceted planes;
- optional restrained warm edge accent on gold-facing contours;
- no visible environment, light source, floor shadow, multi-rim setup, bloom haze, or HDR contrast.

The light reveals geometry, not surface texture.

## Consequences

- Obsidian remains matte but legible.
- Gold can read as metal without mirror behavior.
- Dramatic stage lighting and deep silhouette loss are rejected.
