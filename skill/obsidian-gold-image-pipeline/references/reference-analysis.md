# Reference Analysis

## 1. Goal

Convert visual evidence into a factual analysis card without applying Obsidian Gold style decisions prematurely.

The analysis answers: what is present, what is important, what makes the subject recognizable, and what is uncertain.

## 2. Input validation

Before analysis, confirm:

- at least one usable image is available;
- the target image is identifiable when several images exist;
- image resolution is sufficient to identify the main subject;
- the request is `generate` or `edit`;
- the request does not require prohibited exact text, logo, or real-person identity preservation.

Stop when the target image is missing or unusable. Do not invent a reference.

## 3. Reference roles

Assign one or more explicit roles to every input image:

- `content_reference`: source of subject and semantic meaning;
- `silhouette_reference`: source of outer shape or pose;
- `detail_reference`: source of one declared recognition feature;
- `composition_reference`: weak guidance for orientation or framing only;
- `edit_target`: existing Obsidian Gold image to change;
- `do_not_copy`: context that must not be reproduced literally.

Record each assignment as a structured entry:

```text
image_id
roles
priority
intended_use
must_not_override
notes
```

One image may have multiple roles only when each role is explicit. An edit target must always declare which properties are protected by `keep_unchanged`.

## 4. Primary subject selection

Select one subject using this order:

1. the subject explicitly named by the user;
2. the object occupying the highest visual salience;
3. the object that carries the requested semantic meaning;
4. the object with the strongest unique silhouette;
5. a fused metaphor derived from two inseparable concepts.

Do not select incidental background objects, decorative elements, or text labels.

## 5. Complex scenes

For a complex scene:

1. list the top three candidate subjects;
2. identify the scene's dominant meaning or action;
3. choose one physical object that carries that meaning;
4. when no single object is adequate, design one fused metaphor;
5. remove people, environment, and props unless structurally required by the chosen object.

Examples of valid reduction:

- person protecting data in a server room -> shield with a protected core;
- team climbing a chart -> upward stepped monolith;
- vehicle operating at a site -> the vehicle alone;
- hand holding a card -> the card or a fused card-lock object.

## 6. People and living subjects

People are not reproduced as exact identities in MVP.

Allowed approaches:

- reduce the person to a generic sculptural figure;
- select a carried object or semantic symbol instead;
- preserve a broad pose only when it is essential and visually safe;
- translate an animal into a faceted sculptural body while preserving species-defining silhouette.

Do not promise exact face, hand, clothing, age, or likeness preservation.

## 7. Text, logos, and symbols

- Treat text as semantic evidence, not a drawable element.
- Convert a logo into a generic geometric feature only when the user explicitly permits loss of brand identity.
- Remove watermarks, UI chrome, labels, serial numbers, and incidental symbols.
- Do not reproduce protected marks or pseudo-text by default.

## 8. Multiple references and precedence

Precedence is mode-specific.

### Generate mode

```text
user-stated requirement
  > content reference
  > silhouette reference
  > declared detail reference
  > composition reference
```

### Edit mode

```text
user-stated change
  > edit target keep-unchanged invariants
  > content reference for the changed region only
  > silhouette reference for the changed region only
  > declared detail reference
  > composition reference
```

A supplemental reference must not override an edit-target invariant unless the user explicitly requests that invariant to change.

When two references conflict at the same priority:

- preserve the feature most necessary for subject recognition;
- record the conflict in `unknowns`;
- lower confidence;
- stop if the conflict changes the subject identity.

## 9. Fidelity scale

Use integer values from 0 to 4:

| Value | Meaning |
| --- | --- |
| 0 | Do not preserve. |
| 1 | Preserve only semantic category. |
| 2 | Preserve major recognition features. |
| 3 | Preserve strong shape and proportion cues. |
| 4 | Preserve the feature closely, subject to style constraints. |

Separate fidelity fields are required for subject, silhouette, and composition.

## 10. Reference Analysis Card

Record:

```text
mode
input_images
reference_roles
observed_subjects
primary_subject_candidates
selected_primary_subject
semantic_meaning
recognition_features
silhouette_features
orientation_and_pose
material_evidence
composition_evidence
text_or_logo_evidence
complex_scene_reduction
confidence
unknowns
safety_or_rights_notes
```

The card must describe evidence. Style conversion belongs in the Transformation Contract.
