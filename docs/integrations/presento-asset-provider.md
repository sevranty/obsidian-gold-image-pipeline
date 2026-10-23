# Presento asset-provider boundary

Issue: OGP#37

OGP accepts the optional Presento request/result boundary as a local integration contract.

- Request: `presento.asset-provider.request.v1` / `1.0.0`
- Result: `presento.asset-provider.result.v1` / `1.0.0`
- OGP retains runtime and visual-generation ownership.
- Successful materialized results require an exact provider revision, canonical configuration SHA-256, accepted asset path, SHA-256 checksum and dimensions.
- Failures before materialization must have a stable machine-readable error code and must **not** invent an asset path or checksum. An error is not a successful Presento result.
- Contract tests must not require paid calls or secrets.
- No runtime dependency OGP -> Presento is introduced.
- Source: https://github.com/sevranty/presento/issues/31
- Source merge: `3ce75515783cc6c956d43eaaa6dc0600a434a1e4`.

## Local adapter

`skill/obsidian-gold-image-pipeline/scripts/presento_adapter.py` is an optional offline adapter. It accepts only an explicitly supplied OGP PNG raster with a manifest whose QA verdict is `ACCEPT`, whose `selected_output` matches the raster name, and whose `selected_output_sha256` and dimensions match the actual bytes.

Two entry points are provided:

- `make_executor(manifest_path, asset_path)`: returns a callable for Presento's explicit `materialize_with_provider(..., executor=...)` boundary. It returns accepted bytes, `image/png` and dimensions, without writing to the Presento output directory itself.
- `result_from_accepted_asset(request, manifest_path=..., asset_path=..., provider_revision=...)`: returns the exact 13-field Presento v1 success result for a caller that already owns the materialized OGP raster.

The caller must provide the exact OGP `provider_revision`; the adapter never invents it. Configuration SHA-256 uses canonical UTF-8 JSON (sorted keys, compact separators). All refusals raise `AdapterError` with a stable `code` such as `missing_provider_revision`, `asset_checksum_mismatch`, `not_accepted` or `unsupported_capability`.

The adapter does not generate an image, invoke a paid provider, load credentials, access the network, mutate the source asset or add a runtime dependency on Presento. OGP visual QA and generation remain separate and required before materialization. Offline contract checks live in `tests/test_presento_adapter.py`.

This integration remains optional for Presento and does not authorize a release, external deployment or a live generation call.
