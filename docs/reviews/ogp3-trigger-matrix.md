# OGP#3 Trigger Matrix

Status: Manual routing baseline

## Decision labels

- `TRIGGER_GENERATE`: run the complete generate workflow.
- `TRIGGER_EDIT`: run the complete edit workflow.
- `DO_NOT_TRIGGER`: route to another capability or answer without image generation.
- `BOUNDARY_CONFIRM`: trigger only when a usable image target and generation or edit intent are both clear; otherwise stop for missing input or route elsewhere.

## Positive cases

| ID | User intent | Expected | Rationale |
| --- | --- | --- | --- |
| P01 | Create an Obsidian Gold sculpture from this attached machine photo. | `TRIGGER_GENERATE` | Explicit reference-to-style transformation. |
| P02 | Turn the main object in this image into one isolated black-and-gold digital sculpture. | `TRIGGER_GENERATE` | Single-subject style conversion. |
| P03 | Use this sketch as the content reference and generate an Obsidian Gold asset. | `TRIGGER_GENERATE` | Sketch is valid reference evidence. |
| P04 | Convert this animal into a faceted obsidian sculpture with restrained gold accents. | `TRIGGER_GENERATE` | Living subject translated into the canonical object style. |
| P05 | Reduce this complex scene to one fused metaphor and render it in Obsidian Gold. | `TRIGGER_GENERATE` | Explicit complex-scene reduction. |
| P06 | Preserve the silhouette of this vehicle but rebuild materials, geometry, light, and background in Obsidian Gold. | `TRIGGER_GENERATE` | Recognition and silhouette locks with full style replacement. |
| P07 | Use image one for subject and image two for silhouette; create one Obsidian Gold object. | `TRIGGER_GENERATE` | Multiple references have explicit roles. |
| P08 | Make a square hero object from this reference, isolated on pure black, in Obsidian Gold. | `TRIGGER_GENERATE` | Output ratio and hero-object request remain in scope. |
| P09 | Repair this existing Obsidian Gold image: remove the stone texture and keep everything else unchanged. | `TRIGGER_EDIT` | One localized style repair. |
| P10 | Edit this Obsidian Gold asset so the gold coverage is restrained while preserving subject, camera, crop, and background. | `TRIGGER_EDIT` | One explicit change with invariants. |
| P11 | Fix the black background in this existing Obsidian Gold image without changing the object. | `TRIGGER_EDIT` | Local background repair. |
| P12 | Remove accidental pseudo-text from this Obsidian Gold asset and preserve all compliant properties. | `TRIGGER_EDIT` | Local text artifact removal. |

## Negative cases

| ID | User intent | Expected | Rationale |
| --- | --- | --- | --- |
| N01 | Analyze what is shown in this image. | `DO_NOT_TRIGGER` | Analysis only; no generation or edit intent. |
| N02 | Compare three visual styles for this product. | `DO_NOT_TRIGGER` | Multi-style selection is outside scope. |
| N03 | Create a photorealistic studio product render. | `DO_NOT_TRIGGER` | Photorealistic product rendering is excluded. |
| N04 | Reproduce this entire cinematic scene with all characters and environment. | `DO_NOT_TRIGGER` | Full narrative scene preservation is excluded. |
| N05 | Design an exact company logo in gold. | `DO_NOT_TRIGGER` | Exact logo generation is excluded. |
| N06 | Put this exact sentence inside the generated object. | `DO_NOT_TRIGGER` | Exact text reproduction is excluded. |
| N07 | Preserve this real person's face exactly. | `DO_NOT_TRIGGER` | Exact real-person identity is outside MVP. |
| N08 | Crop this image to square. | `DO_NOT_TRIGGER` | Basic crop belongs to an image utility. |
| N09 | Resize this image to 1024 by 1024. | `DO_NOT_TRIGGER` | Basic resize belongs to an image utility. |
| N10 | Correct white balance and saturation only. | `DO_NOT_TRIGGER` | Basic color correction is outside scope. |

## Boundary cases

| ID | User intent | Expected | Resolution rule |
| --- | --- | --- | --- |
| B01 | Make it Obsidian Gold. | `BOUNDARY_CONFIRM` | Trigger only when a usable image target is present in the current conversation. |
| B02 | Create a black-and-gold image from my idea, with no reference. | `DO_NOT_TRIGGER` | This skill requires visual reference evidence; route to general image generation. |
| B03 | Use this screenshot to create an Obsidian Gold object. | `BOUNDARY_CONFIRM` | Trigger when one primary subject or defensible fused metaphor can be extracted; otherwise stop. |
| B04 | Make this existing asset more premium in Obsidian Gold. | `BOUNDARY_CONFIRM` | Classify as edit only when the target is already substantially compliant; otherwise use generate. |
| B05 | Keep the person recognizable but stylize them. | `BOUNDARY_CONFIRM` | Trigger only when broad pose or generic figure is acceptable; exact likeness remains excluded. |
| B06 | Use this logo only as inspiration for a generic geometric object. | `BOUNDARY_CONFIRM` | Trigger only with explicit permission to lose brand identity and remove drawable logo details. |

## Matrix totals

```text
positive_cases=12
negative_cases=10
boundary_cases=6
total_cases=28
PASS
```

