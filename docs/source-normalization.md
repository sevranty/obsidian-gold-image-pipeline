# Legacy Source Normalization

Status: Foundation baseline

This document records how conflicting legacy rules were normalized into the public, generator-neutral style core. It is provenance, not runtime instruction.

## Conflict matrix

| Topic | Legacy variants | Normalized rule | Rationale |
| --- | --- | --- | --- |
| Background | pure black; black or deep graphite | Production background is pure `#000000`. Deep graphite is exploration-only and is not valid for final output. | A single measurable production invariant prevents background drift. |
| Lighting | soft frontal; contour or rim; point light | Use one broad soft frontal-key light, slightly elevated and offset, plus a restrained warm edge accent only where needed to reveal silhouette. No multi-rim spectacle. | Preserves readable facets while avoiding chrome or theatrical HDR. |
| Obsidian reflections | no reflections; controlled highlights | Obsidian is matte and non-mirror. Broad low-intensity shape highlights are allowed; discrete reflected scenes and hard specular streaks are rejected. | A fully unlit black object is unreadable, while mirror behavior breaks the material. |
| Gold reflections | reflections forbidden; polished or satin gold | Gold is satin by default and may carry small controlled specular highlights. Mirror-like, chrome, or environment reflections are rejected. | Gold must read as metal without turning the object into jewelry render. |
| Gold amount | accent only; 15-25% maximum | Target 15-25% of visible object area. Below 10% is weak unless semantically justified; above 25% is a critical defect. | Converts qualitative guidance into a reviewable range. |
| Composition | marketing hero; one isolated object | One isolated object or one fused metaphor. No environment. Marketing placement occurs outside the generated asset. | Separates asset generation from page composition. |
| Aspect ratio | mandatory Midjourney `--ar 1:1`; square default | Square is the default output ratio, expressed as structured data. Model-specific flags are adapters, not canon. | Keeps the contract portable across generators. |
| Prompt ending | exact sentence required | The prompt must unambiguously require a pure black background; exact wording is not mandatory. | Semantic validation is more robust than string matching. |
| Negative markers | reject any `reflection` token | Reject harmful reflection intent, not the word itself. Controlled gold highlights are allowed. | Avoids false rejection of valid material instructions. |
| Style naming | invoke the style name | Describe the visual invariants explicitly. The style name alone is insufficient. | Prevents magical-token prompting and improves portability. |
| Midjourney flags | `--style raw --v 6 --s 250 --q 2` | Retained only as historical examples outside the normative prompt schema. | Model versions and flags are unstable executor details. |

## Normative precedence

When source statements conflict, precedence is:

1. explicit Foundation ADR;
2. runtime style definition and token contract;
3. transformation and scene schemas;
4. legacy master specification;
5. historical examples.

Historical examples never override a current invariant.
