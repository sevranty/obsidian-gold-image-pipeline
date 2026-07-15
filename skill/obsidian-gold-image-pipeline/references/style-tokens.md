# Obsidian Gold Style Tokens

Style core version: 1.0.0

These tokens are a human- and machine-readable contract. They do not imply implementation in a design-token platform.

## Color tokens

| Token | Value | Rule |
| --- | --- | --- |
| `background.black` | `#000000` | Mandatory final background. |
| `obsidian.base` | `#050505` to `#141414` | Object body may use tonal blacks for readable planes. |
| `obsidian.highlight` | up to `#242424` | Broad low-intensity plane highlight only. |
| `gold.primary` | `#D4AF37` reference | Main warm metallic gold reference. |
| `gold.light` | `#FFD66B` reference | Small highlight or restrained inner glow. |
| `gold.deep` | `#8A6718` reference | Shadowed gold plane. |

Exact rendered pixels vary with lighting. The palette contract is categorical: black/tonal black plus warm gold only.

## Material tokens

| Token | Value |
| --- | --- |
| `material.obsidian.finish` | `matte` |
| `material.obsidian.texture` | `smooth manufactured surface; no mineral texture` |
| `material.obsidian.reflectance` | `non-mirror; broad dim shape highlights only` |
| `material.gold.finish` | `satin default` |
| `material.gold.reflectance` | `small controlled specular highlights; no environment reflection` |
| `material.gold.coverage.target` | `15-25% of visible object area` |
| `material.gold.coverage.warning_low` | `<10% unless semantically justified` |
| `material.gold.coverage.reject_high` | `>25%` |

## Geometry tokens

| Token | Value |
| --- | --- |
| `geometry.family` | `faceted / low-poly / parametric planes` |
| `geometry.edges` | `clean and deliberate` |
| `geometry.folds` | `sharp, controlled` |
| `geometry.detail` | `icon-grade; no micro-noise` |
| `geometry.silhouette_test` | `recognizable at 64x64 px` |

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
