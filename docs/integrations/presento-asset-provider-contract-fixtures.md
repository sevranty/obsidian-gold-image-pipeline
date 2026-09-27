# Presento asset-provider contract fixtures

Issue: OGP#37

These fixtures define repository-only contract cases for the optional Presento boundary. They do not invoke a paid provider, require secrets, or transfer generation ownership out of OGP.

## Valid result

A successful local adapter result must preserve all provenance fields:

- provider revision: exact non-empty revision identifier;
- canonical configuration SHA-256: 64 lowercase hexadecimal characters;
- asset path: non-empty OGP-owned materialized path;
- asset checksum: `sha256:` followed by 64 lowercase hexadecimal characters.

Expected outcome: `accepted`.

## Missing provider revision

All other result fields are present, but provider revision is absent.

Expected outcome: `rejected` with machine-readable reason `missing_provider_revision`.

## Invalid configuration digest

Configuration digest is not a 64-character lowercase SHA-256 value.

Expected outcome: `rejected` with machine-readable reason `invalid_config_sha256`.

## Missing asset provenance

Asset path or asset checksum is absent.

Expected outcome: `rejected` with machine-readable reason `missing_asset_provenance`.

## Provider failure

The provider reports failure before a materialized asset exists.

Expected outcome: machine-readable failure containing a stable error code and no invented asset path or checksum.

## Ownership invariant

In every case, OGP remains the generation/runtime owner. The Presento boundary is optional and must not become a runtime dependency from OGP to Presento.

Source contract: https://github.com/sevranty/presento/issues/31
Source merge: `3ce75515783cc6c956d43eaaa6dc0600a434a1e4`.
