# Frontend Runtime Config

## Purpose

This capability defines the runtime environment-configuration contract for the Aurelia 2 frontend SPA. Per-environment values (API base URL, OIDC issuer / client / org IDs, VAPID public key, ZK circuit base URL, log level, preview artist data, and the environment identifier) are fetched from a same-origin `/config.json` at bootstrap rather than baked into the SPA bundle at build time.

This decoupling makes the container image env-agnostic — the same digest runs in dev, staging, and prod with per-environment divergence served from a Kubernetes ConfigMap mounted by `cloud-provisioning`. It also eliminates the entire class of build-mode-dependent bundle-correctness bugs (notably the v1.0.0 blank-screen Sev-1 that motivated this capability — see archive `2026-05-16-adopt-runtime-config-for-frontend`).

## Requirements

### Requirement: `/config.json` SHALL conform to the AppConfig schema

The runtime configuration document SHALL be a JSON object whose top-level shape exactly matches the TypeScript `AppConfig` interface declared in `frontend/src/config/app-config.ts`. The interface SHALL be the single source of truth for the contract between the SPA bundle and any environment that serves `/config.json`. The schema fields SHALL include: `environment` (one of `dev | staging | prod`), `apiBaseUrl` (absolute https URL), `zitadelIssuer` (absolute https URL), `zitadelClientId` (non-empty string), `zitadelOrgId` (non-empty string), `vapidPublicKey` (non-empty string), `circuitBaseUrl` (string, MAY be empty when ZK circuits are unavailable in the environment), `previewArtistIds` (string array), `previewArtistNames` (string array, same length as `previewArtistIds`), and `logLevel` (one of `trace | debug | info | warn | error`). All fields except `circuitBaseUrl` (which MAY be empty) and the two `previewArtist*` arrays (which MAY be empty) are required-and-non-empty; the spec's "MAY be empty" carve-outs are exhaustive.

#### Scenario: Bootstrap validates required fields

- **WHEN** `/config.json` is fetched and parsed
- **AND** any of `apiBaseUrl`, `zitadelIssuer`, `zitadelClientId`, `zitadelOrgId`, `vapidPublicKey`, `environment`, or `logLevel` is missing, empty, or not a string of the expected shape
- **THEN** bootstrap SHALL throw an error naming the offending field
- **AND** the SPA SHALL NOT call `Aurelia.start()`
- **AND** the page SHALL render a minimal static error notice that surfaces the validation failure to the user

#### Scenario: Empty-string `circuitBaseUrl` disables ZK features

- **WHEN** `circuitBaseUrl` is present in the parsed config but is the empty string
- **THEN** bootstrap SHALL succeed (the field is required-present but MAY be empty per the schema)
- **AND** the `ProofService` (or equivalent ZK-using service) SHALL treat the empty value as "circuits unavailable in this environment" and disable ZK features at the call sites without attempting any circuit fetch

#### Scenario: `previewArtistIds` and `previewArtistNames` length mismatch is rejected

- **WHEN** `/config.json` parses successfully
- **AND** `previewArtistIds.length` does not equal `previewArtistNames.length`
- **THEN** bootstrap SHALL throw an error naming the length-mismatch invariant
- **AND** the SPA SHALL NOT call `Aurelia.start()`
- **AND** the rendered error page SHALL state the observed lengths so the operator can correct the ConfigMap

### Requirement: Bootstrap failures SHALL surface a static error page

When any failure occurs between the page load and `Aurelia.start()` (network failure on `/config.json`, JSON parse error, schema validation failure, or environment cross-check failure), the SPA SHALL replace the document body with a minimal static error page that identifies the failure category and (in non-production environments) the underlying error message. The error page SHALL NOT depend on any Aurelia-provided UI primitive.

#### Scenario: Network failure on /config.json shows error page

- **WHEN** `/config.json` fetch returns a non-2xx status or fails with a network error
- **THEN** the document body SHALL be replaced with a static error block
- **AND** the block SHALL include the literal text "App failed to start" or equivalent
- **AND** the block SHALL include the HTTP status or error class for diagnosis

#### Scenario: Schema validation failure shows error page

- **WHEN** `/config.json` parses successfully but fails the required-field validation
- **THEN** the document body SHALL be replaced with the static error block
- **AND** the block SHALL name the offending field
