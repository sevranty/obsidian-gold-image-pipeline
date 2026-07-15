# Obsidian Gold Style Tokens

Style core version: 1.0.0

These tokens are a human- and machine-readable contract. They do not imply implementation in a design-token platform.

## Color tokens

| Token | Value | Rule |
| --- | --- | --- |
| `background.black` | `#000000` | Mandatory final background. |
| `obsidian.body.range` | `#050505` to `#1A1A1A` | Tonal black range for readable object planes. |
| `obsidian.deep.reference` | `#1A1A1A` | Legacy canonical deep-obsidian reference; never a final background. |
| `obsidian.highlight.limit` | up to `#242424` | Derived readability ceiling for broad low-intensity plane highlights. |
| `gold.primary` | `#FFD700` | Legacy canonical primary gold reference. |
| `gold.secondary` | `#C7A256` | Legacy canonical muted/satin gold reference. |

Rendered highlights and shadows may vary because of lighting, but they must remain categorical warm-gold variations rather than new design colors.

## Material tokens

| Token | Value |
| --- | --- |
| `material.obsidian.finish` | `matte` |
| `material.obsidian.texture` | `smooth manufactured surface; no mineral texture` |
| `material.obsidian.reflectance` | `non-mirror; broad dim shape highlights only` |
| `material.gold.finish` | `satin default` |
| `material.gold.reflectance` | `small controlled specular highlights; no environment reflection` |
| `material.gold.coverage.target` | `15-25% of visible object area` |
| `material.gold.coverage.below_target` | `<15% allowed only when semantically justified and still visibly intentional` |
| `material.gold.coverage.reject_high` | `>25%` |

The 15-25% range is a provisional Foundation target pending visual calibration in the evidence set. Values below the target are not automatically critical; values above 25% are critical.

## Geometry tokens

| Token | Value |
| --- | --- |
| `geometry.family` | `faceted / low-poly / parametric planes` |
| `geometry.edges` | `clean and deliberate` |
| `geometry.folds` | `sharp, controlled` |
| `geometry.detail` | `icon-grade; no micro-noise` |
| `geometry.silhouette_test` | `recognizable when fitted inside 64x64 px` |

## Lighting tokens

| Token | Value |
| --- | --- |
| `light.key.type` | `broad soft key` |
| `light.key.position` | `slightly above; 15-30 degrees off camera axis` |
| `light.key.intensity` | `low to moderate` |
| `light.edge` | `optional restrained warm accent` |
| `light.floor_shadow` | `none` |
| `light.environment_reflection` | `none` |
| `light.hdr` | `forbidden` |

## Composition tokens

| Token | Value |
| --- | --- |
| `composition.subject_count` | `1` |
| `composition.environment` | `none` |
| `composition.negative_space` | `generous` |
| `composition.default_alignment` | `centered or slightly offset` |
| `composition.default_ratio` | `1:1` |
| `composition.crop` | `full object visible` |

## Forbidden categories

```text
stone texture
natural obsidian rock
marble veins
crystal facets that read as mineral
chrome
mirror finish
reflective black lacquer
HDR
bloom spectacle
environment
floor or pedestal
light background
gradient background
additional colors
text
logo
watermark
```
