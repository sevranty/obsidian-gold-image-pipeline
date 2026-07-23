# OGP#12 Repository Cover Benchmark

Status: selected concept approved for repository use.

## References reviewed

| Reference | Pattern observed | Use for OGP |
| --- | --- | --- |
| [OpenAI skills](https://github.com/openai/skills) | Documentation-first repository entry point; visual restraint; strong source-of-truth hierarchy. | Keep the cover secondary to factual README status and contracts. |
| [OpenAI imagegen skill](https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/imagegen/SKILL.md) | Explicit generation/editing boundaries and visible-delivery discipline. | Preserve the distinction between a repository cover and live-generator proof. |
| [OpenAI skill-creator](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md) | Focused skill scope, validation, and metadata consistency. | Keep asset provenance and source paths explicit. |
| [ComfyUI](https://github.com/Comfy-Org/ComfyUI) | Product screenshots and workflow UI communicate capability quickly but create dense visual scenes. | Do not copy screenshot-heavy composition; OGP needs one isolated subject and no interface chrome. |
| [InvokeAI](https://github.com/invoke-ai/InvokeAI) | Rich product imagery communicates creative breadth but competes with a mono-style identity. | Use a single controlled transformation motif instead of a gallery. |

## Cover requirements

- Show the pipeline, not only a finished black-and-gold object.
- Keep one subject represented in two states: wireframe reference and final sculpture.
- Use pure black background.
- Use no text, logo, UI chrome, environment, person, brand asset, or third-party material.
- Preserve readability in GitHub cards and the README.
- Keep gold restrained and subordinate to the obsidian body.
- Record source, rendering method, QA, export parameters, and checksums.

## Concept comparison

| Concept | File | Strength | Risk | Decision |
| --- | --- | --- | --- | --- |
| Portal transformation | `assets/concepts/concept-portal.svg` | The same silhouette is clearly visible before and after transformation; reads as a pipeline at small size. | Repeated subject states could be misread as two objects without a clear transformation bridge. | **Selected** |
| Folded prism | `assets/concepts/concept-prism.svg` | Strong angular silhouette and simple facets. | Reads more like an abstract logo than a reference-to-result pipeline. | Rejected |
| Neural core | `assets/concepts/concept-core.svg` | Communicates AI and internal transformation. | More decorative and less immediately legible as a source-to-final conversion. | Rejected |

## Selected direction

The selected portal uses one self-authored geometric subject shown as:

```text
wireframe reference
  -> restrained transformation markers
  -> faceted obsidian-and-gold final state
```

The composition deliberately contains no words. Repository identity remains in the surrounding GitHub/README context rather than inside the image.

## Versioned asset model

The repository commits canonical SVG assets. PNG/WebP renditions are review/build outputs, not published release binaries. GitHub social-preview Settings remain unchanged because Settings writes require a separate explicit owner action.

## Rights and provenance

The source geometry is self-authored for this repository and stored as:

- `assets/source/reference-portal-wireframe.svg`
- `assets/cover-source-manifest.json`

No third-party image, logo, private FDS material, personal data, or externally licensed visual asset is used.
