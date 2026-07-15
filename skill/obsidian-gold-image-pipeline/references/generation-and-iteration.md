# Generation and Iteration Contract

## 1. Generation entry gate

Call the image-generation executor only after all of the following exist and agree:

- Reference Analysis Card;
- Transformation Contract;
- complete Scene Specification;
- prompt preflight pass;
- usable input image roles;
- no unresolved stop condition.

## 2. Generate mode

Use generation when creating a new image from reference evidence.

Rules:

- attach or identify each reference by role;
- do not ask the executor to copy the full scene;
- request one final candidate unless internal comparison is necessary;
- inspect the actual result before accepting it;
- preserve declared recognition and silhouette features, not source materials or background.

## 3. Edit mode

Use edit when the target is an existing image and most compliant properties should remain unchanged.

Rules:

- identify the edit target explicitly;
- make one targeted change per iteration;
- re-state all keep-unchanged invariants;
- do not use edit when the subject, camera, silhouette, and material system all require replacement;
- inspect the entire image after edit, not only the repaired region.

## 4. Iteration budget

Default maximum:

```text
initial generation: 1
targeted repair iterations: 2
full regeneration after failed repairs: 1
```

The skill may stop earlier when the result passes or when repair would be misleading.

## 5. Repair versus regeneration

Use targeted repair when:

- the correct subject and silhouette are present;
- one or two localized style defects exist;
- the composition and camera remain valid;
- fixing the defect does not require redesigning the object.

Use full regeneration when:

- the primary subject is wrong;
- multiple objects are present;
- the silhouette is fundamentally unrecognizable;
- the scene includes an environment;
- the camera or crop is unusable;
- material drift affects most of the object;
- a targeted repair already caused new global defects.

## 6. Single-change rule

Each repair iteration addresses one diagnostic category. A repair instruction may include preservation constraints but must not redesign unrelated properties.

Example:

```text
Change: replace rough stone texture with a smooth manufactured matte obsidian-black surface.
Keep unchanged: subject identity, silhouette, camera, crop, gold placement, gold ratio, pure black background.
Must not appear: veins, cracks, pores, crystals, chrome, extra colors, text.
```

## 7. Completion

A result is complete only after:

- visual inspection;
- critical defect check;
- scorecard decision;
- 64 px silhouette check;
- final full-size review;
- user-visible image delivery.

A successful executor response without a visible final image is a delivery failure.
