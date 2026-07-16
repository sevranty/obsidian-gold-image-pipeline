# OGP Agent Entry Point

- Canonical architecture: `docs/architecture.md`.
- Canonical dependency order: `docs/dependency-map.md`.
- Canonical release gates: `docs/release-process.md`.
- OGP owns skill code, style contracts, validators, evals, assets, packages and releases in this repository.
- WebFactoryOS owns registry, routing, orchestration status and cross-project relations outside this repository.
- Do not copy WebFactoryOS registry data into OGP.
- Do not add runtime dependencies on WebFactoryOS.
- WebFactoryOS availability must not block OGP runtime, local validation or release candidate work.
