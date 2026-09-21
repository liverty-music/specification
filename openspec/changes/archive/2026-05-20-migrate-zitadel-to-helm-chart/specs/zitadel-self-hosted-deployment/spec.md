## ADDED Requirements

### Requirement: Login V2 UI Base Path Collapsed to `/ui/v2`

The Login V2 UI container SHALL serve at base path `/ui/v2` (NOT the chart-default `/ui/v2/login`), and the Zitadel API SHALL be configured with `DefaultInstance.Features.LoginV2.BaseURI: /ui/v2` so its OIDC redirect target is `/ui/v2/login?authRequest=<id>` instead of the historical `/ui/v2/login/login?authRequest=<id>`. The HTTPRoute path-prefix rule for the Login UI SHALL match `/ui/v2` (NOT `/ui/v2/login`), and Pod-level + Gateway-level health probes SHALL use the new probe paths `/ui/v2/healthy` and `/ui/v2/ready`.

**Rationale**: The user-visible URL `/ui/v2/login/login` is a redundant concatenation of the Login UI's base path (`/ui/v2/login`, chart default) and its `/login` Next.js page route. Collapsing the base path to `/ui/v2` eliminates the redundancy while preserving the route structure of the upstream Zitadel Login V2 UI app. The `/ui/v2` prefix does NOT collide with the API's `/ui/console` Admin Console SPA (they diverge at the second path segment). The chart's `login.{liveness,readiness}Probe.enabled: true` defaults serve the now-stale paths `/ui/v2/login/{healthy,ready}` (template helpers `login.livenessProbePath` / `login.readinessProbePath` hard-code these); we set `enabled: false` on the chart probes and re-inject correct probes via a Kustomize patch (`overlays/<env>/login-probe-patch.yaml`).

#### Scenario: OIDC redirect lands on the single-`/login` URL

- **WHEN** a browser starts an OIDC authorize flow against `https://auth.dev.liverty-music.app/oauth/v2/authorize?...`
- **THEN** the Zitadel API SHALL redirect the browser to `https://auth.dev.liverty-music.app/ui/v2/login?authRequest=<id>` (NOT `.../ui/v2/login/login?authRequest=<id>`)

#### Scenario: Login UI register flow lands on the single-base URL

- **WHEN** a browser navigates from `/ui/v2/login?authRequest=<id>` to the register flow
- **THEN** the URL SHALL become `https://auth.dev.liverty-music.app/ui/v2/register?...` (NOT `.../ui/v2/login/register?...`)

#### Scenario: Pod liveness/readiness probes target the new paths

- **WHEN** the chart-rendered Login UI Deployment is inspected
- **THEN** the container's `livenessProbe.httpGet.path` SHALL be `/ui/v2/healthy`
- **AND** the container's `readinessProbe.httpGet.path` SHALL be `/ui/v2/ready`
- **AND** the chart's hard-coded `/ui/v2/login/{healthy,ready}` paths SHALL NOT appear in the rendered Deployment (chart probes disabled via `login.{readiness,liveness}Probe.enabled: false`)

#### Scenario: Existing instance Feature flag updated post-cutover

- **WHEN** the chart values' `DefaultInstance.Features.LoginV2.BaseURI: /ui/v2` is applied
- **THEN** the value SHALL take effect for NEW instances created from that point forward
- **AND** for the already-bootstrapped instance (where `FirstInstance.Skip: true`), the operator SHALL invoke `instance.v2.SetInstanceFeatures` with `loginV2.baseUri = "/ui/v2"` post-deploy to apply the change to the running instance

## MODIFIED Requirements

### Requirement: Two-Container Deployment with Path-Based Routing

The system SHALL deploy Zitadel as two separate Kubernetes Deployments — one for the API container (`ghcr.io/zitadel/zitadel`, port `8080`, Deployment name `zitadel-api`) and one for the Login V2 UI container (`ghcr.io/zitadel/zitadel-login`, port `3000`, Deployment name `zitadel-api-login`) — and SHALL expose both through a single hostname via a GKE Gateway `HTTPRoute` that routes the path prefix `/ui/v2` to the Login UI Service (`zitadel-api-login`) and all other paths to the API Service (`zitadel-api`). Both Deployments SHALL be rendered by the official `zitadel/zitadel-charts` Helm chart with `fullnameOverride: zitadel-api` (NOT hand-written manifests under `k8s/namespaces/zitadel/base/`).

**Rationale**: Zitadel v4 split the Login UI into a dedicated container. Keeping both on the same hostname preserves OIDC issuer identity; path-based routing avoids the extra DNS and certificate surface of a second hostname. The API Deployment / Service is named `zitadel-api` to avoid the legacy `ZITADEL_PORT` env-var Viper collision that would occur with the chart-default `zitadel` name (Kubernetes' service-discovery env-var injection would inject `ZITADEL_PORT=tcp://<ip>:80` which Viper parses as the binary's `Port` config field — startup fails). The Login UI Deployment / Service is named `zitadel-api-login` because the chart hard-codes the Login UI's resource name to `<zitadel.fullname>-login` regardless of `login.fullnameOverride`. The image path is `ghcr.io/zitadel/zitadel-login`, NOT `ghcr.io/zitadel/login` (the latter 404s); the upstream Helm chart default uses the same path. Rendering via the official chart eliminates the divergence from upstream defaults that hand-tuned manifests accumulated.

#### Scenario: API request reaches the API container

- **WHEN** a request arrives at `https://auth.dev.liverty-music.app/oauth/v2/keys`
- **THEN** the HTTPRoute SHALL forward the request to the `zitadel-api` Service on port `80` (Service targetPort 8080)

#### Scenario: Login UI request reaches the Login UI container

- **WHEN** a browser requests `https://auth.dev.liverty-music.app/ui/v2/register`
- **THEN** the HTTPRoute SHALL forward the request to the `zitadel-api-login` Service on port `80` (Service targetPort 3000)

#### Scenario: HealthCheckPolicy targets chart-natural Service names

- **WHEN** the GKE Gateway evaluates backend health
- **THEN** a `HealthCheckPolicy` named `zitadel-api-policy` SHALL target the `zitadel-api` Service with probe path `/debug/healthz`
- **AND** a `HealthCheckPolicy` named `zitadel-web-policy` SHALL target the `zitadel-api-login` Service with probe path `/ui/v2/healthy` (the resource name `zitadel-web-policy` is retained for ops continuity; the targetRef and probe path are updated)

#### Scenario: Both Deployments are chart-rendered with the expected names

- **WHEN** `kustomize build --enable-helm k8s/namespaces/zitadel/overlays/dev` is rendered
- **THEN** both Deployments SHALL carry the `app.kubernetes.io/managed-by: Helm` label
- **AND** their `metadata.name` SHALL be `zitadel-api` (top-level `fullnameOverride`) and `zitadel-api-login` (chart-hard-coded `<fullname>-login`)

## REMOVED Requirements

### Requirement: Login V2 UI Calls Zitadel API via Public URL

**Reason**: The original "Public URL" pattern (`ZITADEL_API_URL=https://auth.<env>.liverty-music.app`) caused the Login UI Pod to hairpin through the GCP HTTPS LB external IP back into the same cluster. Node's HTTP/1.1 client + GCP HTTPS LB exhibits intermittent 30 s hangs at the record-layer (Zitadel upstream PR #12022 documented this on Cloud Run, with the same symptom on GKE). The canonical upstream solution — shipped in `zitadel/zitadel-charts` and `zitadel/zitadel/deploy/compose/docker-compose.yml` — routes via the in-cluster Service while presenting the external hostname as `Host` header. Public-URL routing is therefore not just suboptimal but operationally broken on GCP HTTPS LB, and is no longer the right baseline behavior to specify.

**Migration**: The replacement is the ADDED requirement above, "Login V2 UI Routes Outbound Calls Via Cluster-Internal Service Using CUSTOM_REQUEST_HEADERS", which captures the same intent (Login UI reaching the API) but with the chart-native pattern that survives the hairpin. The chart auto-generates `ZITADEL_API_URL=http://zitadel-api:80` and `CUSTOM_REQUEST_HEADERS=Host:<ExternalDomain>,X-Zitadel-Public-Host:<ExternalDomain>` via its `login-config-dotenv` ConfigMap; no operator action beyond setting `zitadel.configmapConfig.ExternalDomain` in `base/values.yaml` is required.
