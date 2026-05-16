# frontend-runtime-config Specification

## ADDED Requirements

### Requirement: Frontend SPA SHALL load environment configuration from `/config.json` at bootstrap

The Aurelia 2 frontend SPA SHALL fetch a same-origin `/config.json` file during application bootstrap and use the parsed values as the source of truth for all environment-divergent configuration (API base URL, OIDC issuer/client/org IDs, VAPID public key, ZK circuit base URL, log level, preview artist data, and the environment identifier). The fetch SHALL complete before `Aurelia.start()` is invoked, so that all services and route components receive the resolved configuration via dependency injection on first construction. The SPA SHALL NOT read these values from `import.meta.env.VITE_*` at runtime in shipped production builds.

#### Scenario: Bootstrap blocks on config fetch before Aurelia starts

- **WHEN** the SPA is loaded in a browser
- **THEN** the bootstrap entry point SHALL invoke `fetch('/config.json', { cache: 'no-store' })` before constructing the Aurelia application instance
- **AND** SHALL await the fetch and JSON parse to completion
- **AND** SHALL only call `Aurelia.start()` (or equivalent) after the parsed configuration is available
- **AND** SHALL register the parsed configuration as a DI singleton accessible to all services

#### Scenario: Bundle contains no env-divergent VITE_ values

- **WHEN** searching any JavaScript chunk in the built `dist/` output for strings matching `https://api\.(dev\.)?liverty-music\.app`, `https://auth\.(dev\.)?liverty-music\.app`, the dev OIDC `client_id`, the prod OIDC `client_id`, the dev VAPID public key, or the prod VAPID public key
- **THEN** zero occurrences SHALL be found in any of those patterns
- **AND** the only origin-specific URL that MAY appear in chunks SHALL be `window.location.origin`-derived (e.g., redirect URIs constructed at runtime)

#### Scenario: All eight legacy VITE_ read sites are migrated

- **WHEN** running `grep -rn 'import\.meta\.env\.VITE_' frontend/src`
- **THEN** the result SHALL be empty
- **AND** the corresponding values SHALL be obtained from the `AppConfig` DI token instead

#### Scenario: import.meta.env.DEV reads are preserved

- **WHEN** running `grep -rn 'import\.meta\.env\.\(DEV\|PROD\|MODE\)' frontend/src`
- **THEN** the result MAY contain reads
- **AND** every such read SHALL encode "running under `vite` dev server vs. running from a `vite build` artifact" — not "which deployed environment serves this bundle"

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

### Requirement: Bootstrap SHALL cross-check the configured environment against the page host

The SPA SHALL refuse to start if the `environment` field in `/config.json` is inconsistent with `window.location.hostname` for the well-known production-tier hostnames (`liverty-music.app` → `prod`, `dev.liverty-music.app` → `dev`, `staging.liverty-music.app` → `staging`). This guards against the failure mode in which a misconfigured deployment serves the image's bundled fallback config in a production-tier environment.

The `staging` environment is reserved/forward-looking: the `AppConfig.environment` union includes it and the host map MUST include `staging.liverty-music.app`, but no Kubernetes overlay or hostname currently maps to `staging` (introduced when the staging cluster is provisioned by a future change). The cross-check requirement holds whether or not the staging cluster exists yet.

#### Scenario: Production host with dev config refuses to start

- **WHEN** the page is loaded at `https://liverty-music.app/` (production apex)
- **AND** `/config.json` has `environment` field equal to `dev` or `staging`
- **THEN** bootstrap SHALL throw an error naming the mismatch
- **AND** the SPA SHALL NOT call `Aurelia.start()`
- **AND** the rendered error page SHALL state the expected and actual environment values

#### Scenario: Staging host with non-staging config refuses to start

- **WHEN** the page is loaded at `https://staging.liverty-music.app/`
- **AND** `/config.json` has `environment` field equal to `dev` or `prod`
- **THEN** bootstrap SHALL throw an error naming the mismatch
- **AND** the SPA SHALL NOT call `Aurelia.start()`

#### Scenario: Staging host with staging config passes

- **WHEN** the page is loaded at `https://staging.liverty-music.app/`
- **AND** `/config.json` has `environment` field equal to `staging`
- **THEN** the host cross-check SHALL pass and bootstrap SHALL proceed

#### Scenario: Localhost or preview hostname skips the check

- **WHEN** the page is loaded at `http://localhost`, `http://127.0.0.1`, or any hostname not in the well-known production-tier list
- **THEN** bootstrap SHALL skip the host-vs-environment check
- **AND** SHALL proceed with whatever `environment` value is in `/config.json`

### Requirement: A checked-in `public/config.json` SHALL provide dev defaults

The frontend repository SHALL maintain a `public/config.json` file at the root of the Vite public directory containing dev environment values. This file serves three purposes: (1) it makes `npm start` (the Vite dev server) work without external configuration, (2) it provides accurate values for Storybook and local Playwright runs, and (3) it acts as an in-image fallback that — combined with the environment cross-check — produces a loud failure mode if a per-environment ConfigMap mount is missing in a non-dev cluster.

#### Scenario: Public config.json contains dev values

- **WHEN** inspecting `frontend/public/config.json`
- **THEN** the file SHALL exist
- **AND** its `environment` field SHALL equal `dev`
- **AND** its `apiBaseUrl` SHALL equal `https://api.dev.liverty-music.app`
- **AND** its `zitadelIssuer` SHALL equal `https://auth.dev.liverty-music.app`

#### Scenario: Public config.json is served by Vite dev server

- **WHEN** running `npm start` and requesting `http://localhost:9000/config.json`
- **THEN** the response status SHALL be `200`
- **AND** the body SHALL be the JSON content of `public/config.json`

### Requirement: The Service Worker SHALL bypass any cache for `/config.json`

The Workbox-based Service Worker SHALL include an explicit `NetworkOnly` route for the `/config.json` request, so that ConfigMap updates (followed by pod rollout) are picked up by subsequent navigations without depending on cache-busting URLs. The runtime config endpoint SHALL NOT be included in the precache manifest (`__WB_MANIFEST`).

#### Scenario: SW route exists for /config.json

- **WHEN** inspecting `frontend/src/sw.ts`
- **THEN** a `registerRoute` call SHALL exist that matches `url.pathname === '/config.json'`
- **AND** the strategy SHALL be `NetworkOnly`

#### Scenario: /config.json is not precached

- **WHEN** inspecting the built `dist/sw.js`'s `__WB_MANIFEST` array
- **THEN** no entry SHALL have a URL ending in `/config.json`

#### Scenario: Online reload picks up new ConfigMap content

- **WHEN** the ConfigMap is updated and pods restart (via Reloader)
- **AND** an online client reloads the page
- **THEN** the SPA SHALL fetch the new `/config.json` content directly from Caddy via the SW pass-through
- **AND** the new values SHALL take effect for the lifetime of the new page load

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
