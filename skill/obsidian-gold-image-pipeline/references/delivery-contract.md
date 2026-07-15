# User-visible Delivery Contract

## 1. Principle

Generation is not complete until the final raster image is visible or directly accessible to the user in the final response.

A successful executor call, internal preview, temporary tool result, hidden attachment, or assistant-side file path does not satisfy delivery.

## 2. Delivery states

Use exactly one final state:

- `DELIVERY_READY`: the accepted final image is attached, embedded, or linked through the supported user-visible surface.
- `DELIVERY_MISSING`: an image may have been generated, but the user cannot see or access it.
- `DELIVERY_FAILED`: no usable image exists, the output is lost, or the delivery surface failed irrecoverably.
- `DELIVERY_BLOCKED`: policy, rights, missing input, unsupported capability, or another stop condition prevents valid delivery.

Only `DELIVERY_READY` permits a successful completion claim.

## 3. Pre-delivery gate

Before the final response, confirm:

- the delivered asset is the candidate that passed final QA;
- the asset is a raster image rather than an SVG, HTML, CSS, or textual substitute;
- the image opens or renders on the intended user-visible surface;
- the image is not an earlier rejected or pre-repair candidate;
- no internal path, temporary identifier, or unsupported local reference is presented as delivery;
- known non-blocking limitations are stated accurately.

## 4. Final response behavior

When `DELIVERY_READY`:

- show or attach the final image;
- keep the accompanying text brief;
- identify any material limitation that remains within the accepted result;
- do not expose internal prompts, hidden reasoning, or temporary executor metadata unless requested and safe.

When `DELIVERY_MISSING`:

1. attempt retrieval, re-attachment, or re-export of the accepted asset;
2. do not regenerate solely because the delivery surface failed unless the accepted asset is unavailable;
3. re-run the delivery gate;
4. if visibility still cannot be confirmed, report the delivery failure explicitly.

When `DELIVERY_FAILED` or `DELIVERY_BLOCKED`:

- state the exact blocking condition;
- do not imply that a completed image was delivered;
- do not replace the requested raster output with descriptive prose presented as success.

## 5. Repair boundary

Delivery repair changes only packaging or presentation of the accepted image. It must not alter subject, style, geometry, material, lighting, background, crop, or QA status.

If the image itself is missing or corrupted, return to the generation-and-iteration contract and apply the remaining iteration budget.

## 6. Completion record

Record:

```text
delivery_state
accepted_candidate_id
delivery_surface
visibility_confirmed
retrieval_attempted
known_limitations
```

The workflow ends successfully only with:

```text
delivery_state: DELIVERY_READY
visibility_confirmed: true
```

