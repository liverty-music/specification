## MODIFIED Requirements

### Requirement: `/config.json` SHALL conform to the AppConfig schema

The runtime configuration document SHALL be a JSON object whose top-level shape exactly matches the TypeScript `AppConfig` interface declared in `frontend/shared/config/app-config.ts`. The interface SHALL be the single source of truth for the contract between the SPA bundle and any environment that serves `/config.json`. The schema fields SHALL include: `environment` (one of `dev | staging | prod`), `apiBaseUrl` (absolute https URL), `zitadelIssuer` (absolute https URL), `zitadelClientId` (non-empty string), `zitadelOrgId` (non-empty string), `vapidPublicKey` (non-empty string), `circuitBaseUrl` (string, MAY be empty when ZK circuits are unavailable in the environment), `previewArtistIds` (string array), `previewArtistNames` (string array, same length as `previewArtistIds`), `logLevel` (one of `trace | debug | info | warn | error`), and `releaseVersion` (optional string — the semver release tag for the deployed image, e.g. `"v1.26.0"`). All fields except `circuitBaseUrl` (which MAY be empty), the two `previewArtist*` arrays (which MAY be empty), and `releaseVersion` (which is optional) are required-and-non-empty; the spec's "MAY be empty" and "optional" carve-outs are exhaustive.

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

#### Scenario: Absent `releaseVersion` is tolerated

- **WHEN** `/config.json` is fetched and parsed
- **AND** the `releaseVersion` field is absent or `undefined`
- **THEN** bootstrap SHALL succeed
- **AND** `AppConfig.releaseVersion` SHALL be `undefined`
- **AND** any UI that would display `releaseVersion` SHALL render a safe placeholder (e.g., `—`) without throwing
