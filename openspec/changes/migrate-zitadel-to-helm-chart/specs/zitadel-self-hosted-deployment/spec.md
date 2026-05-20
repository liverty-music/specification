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

### Requirement: Zitadel Deployment Rendered by Official Helm Chart

The Zitadel API and Login V2 UI Deployments, Services, ServiceAccounts, PodDisruptionBudgets, and ConfigMap SHALL be rendered from the official `zitadel/zitadel-charts` Helm chart via Kustomize's `helmCharts:` integration (pinned to a specific chart version in each overlay's `kustomization.yaml`), NOT hand-written. The chart's top-level `fullnameOverride: zitadel-api` SHALL preserve the API Deployment / Service / ConfigMap names; the Login V2 UI subchart hard-codes its resource name to `<zitadel.fullname>-login` (i.e., `zitadel-api-login`) — `login.fullnameOverride` exists as a values key but is NOT honored by the chart templates. HTTPRoute backendRefs and HealthCheckPolicy targets SHALL be updated to reference `zitadel-api-login` for the Login UI side; the API side remains `zitadel-api`.

**Rationale**: The Helm chart is the upstream-supported deployment artifact for Zitadel self-hosting. Hand-rolled Kustomize Deployments diverge from upstream defaults at every release. The `helmCharts:` integration pattern is already in use for `external-secrets`, `reloader`, `nats`, `keda`, and `atlas-operator`, so adopting it for Zitadel keeps the manifest tree internally consistent. The `fullnameOverride: zitadel-api` (not the chart-default `zitadel`) avoids re-introducing the legacy `ZITADEL_PORT` env-var Viper collision that motivated the prior `zitadel`→`zitadel-api` rename. Per-overlay self-contained `values.yaml` (rather than a shared base + additionalValuesFiles) is necessary because Kustomize's default `LoadRestrictionsRootOnly` blocks cross-directory file refs used by CI's `kustomize build --enable-helm`.

#### Scenario: API Deployment originates from the chart

- **WHEN** `kustomize build --enable-helm k8s/namespaces/zitadel/overlays/dev` is rendered
- **THEN** the output SHALL include a Deployment named `zitadel-api` whose `app.kubernetes.io/managed-by` label is `Helm`
- **AND** the Deployment SHALL run the image `ghcr.io/zitadel/zitadel:<pinned-tag>` at port `8080`

#### Scenario: Login UI Deployment originates from the chart

- **WHEN** `kustomize build --enable-helm k8s/namespaces/zitadel/overlays/dev` is rendered
- **THEN** the output SHALL include a Deployment named `zitadel-api-login` whose `app.kubernetes.io/managed-by` label is `Helm`
- **AND** the Deployment SHALL run the image `ghcr.io/zitadel/zitadel-login:<pinned-tag>` at port `3000`

#### Scenario: Chart version is pinned

- **WHEN** the `helmCharts:` entry for `zitadel/zitadel-charts` is inspected in `kustomization.yaml`
- **THEN** the `version:` field SHALL be set to an explicit semver value (not `latest`)
- **AND** chart upgrades SHALL be performed by explicit edit to that field in a pull request

#### Scenario: HTTPRoute and HealthCheckPolicy reference chart-natural Service names

- **WHEN** the chart-rendered Services replace the hand-rolled Services
- **THEN** the `HTTPRoute` SHALL list backendRefs `zitadel-api` (API catch-all) and `zitadel-api-login` (Login UI path prefix `/ui/v2/login`)
- **AND** the `HealthCheckPolicy` resource `zitadel-api-policy` SHALL target the `zitadel-api` Service
- **AND** the `HealthCheckPolicy` resource `zitadel-web-policy` SHALL target the `zitadel-api-login` Service (the resource name `zitadel-web-policy` is retained for ops continuity; the targetRef is updated)

### Requirement: Login V2 UI Routes Outbound Calls Via Cluster-Internal Service Using CUSTOM_REQUEST_HEADERS

The `zitadel-web` container SHALL set `ZITADEL_API_URL` to the cluster-internal Service URL of the API (e.g., `http://zitadel-api:8080` or the Helm chart's default `http://<release>-zitadel:<port>`) AND SHALL set `CUSTOM_REQUEST_HEADERS=Host:<ExternalDomain>` so that Connect-RPC traffic stays in-cluster while presenting the public issuer hostname as the `Host` header.

**Rationale**: This is the canonical upstream pattern, documented in `zitadel/zitadel-charts/charts/zitadel/values.yaml` and `zitadel/zitadel/deploy/compose/docker-compose.yml`. The Login V2 UI's `apps/login/src/lib/custom-headers.ts` parses `CUSTOM_REQUEST_HEADERS` and merges those headers into every outbound Connect-RPC call. The API's `internal/api/grpc/server/connect_middleware/instance_interceptor.go` resolves the instance by the `Host` header, matching it against `InstanceDomains` (which already contains the public ExternalDomain). No per-instance domain registration, no System User, no JWT signing pipeline, and no instance-id discovery are required. Eliminates the entire `route-login-v2-via-internal-zitadel-api` apparatus (Pulumi Dynamic Resource + System User + GSM Secrets) by replacing it with two env values delivered via chart configuration. Simultaneously eliminates the prod GCP HTTPS LB hairpin that caused the original 30s timeout on `/ui/v2/login/login?authRequest=...`.

#### Scenario: Login UI Pod reaches the API via cluster-internal Service DNS

- **WHEN** the `zitadel-web` Pod issues an outbound Connect-RPC call
- **THEN** the connection target SHALL be the cluster-internal Service DNS name of the chart-rendered API Service (resolvable as `zitadel-api.zitadel.svc.cluster.local`)
- **AND** the request SHALL NOT egress to the GKE Gateway external IP

#### Scenario: Outbound calls carry the public Host header

- **WHEN** the Zitadel API Pod receives a request from the Login UI Pod
- **THEN** the `Host` header SHALL be the configured `ExternalDomain` (`auth.dev.liverty-music.app` in dev, `auth.liverty-music.app` in prod)
- **AND** the API's `instance_interceptor` SHALL resolve the request to the correct virtual instance

#### Scenario: CUSTOM_REQUEST_HEADERS is set from chart values, not Kustomize patches

- **WHEN** the Login UI container env is inspected
- **THEN** the `CUSTOM_REQUEST_HEADERS` env var SHALL be sourced from the chart's values (`login.env` or the chart-equivalent key)
- **AND** there SHALL NOT be a Kustomize patch overriding `ZITADEL_API_URL` to a public hostname

## MODIFIED Requirements

### Requirement: Two-Container Deployment with Path-Based Routing

The system SHALL deploy Zitadel as two separate Kubernetes Deployments — one for the API container (`ghcr.io/zitadel/zitadel`, port `8080`, Deployment name `zitadel-api`) and one for the Login V2 UI container (`ghcr.io/zitadel/zitadel-login`, port `3000`, Deployment name `zitadel-api-login`) — and SHALL expose both through a single hostname via a GKE Gateway `HTTPRoute` that routes the path prefix `/ui/v2/login` to the Login UI Service (`zitadel-api-login`) and all other paths to the API Service (`zitadel-api`). Both Deployments SHALL be rendered by the official `zitadel/zitadel-charts` Helm chart with `fullnameOverride: zitadel-api` (NOT hand-written manifests under `k8s/namespaces/zitadel/base/`).

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

### Requirement: Login V2 UI Calls Zitadel API via Public URL

The `zitadel-web` container SHALL route its outbound Connect-RPC traffic through the cluster-internal Service DNS of the API (via the chart's default `ZITADEL_API_URL`) and SHALL present the public issuer hostname in the `Host` header through `CUSTOM_REQUEST_HEADERS=Host:<ExternalDomain>`, NOT via a public URL.

**Rationale**: The original "Public URL" pattern (set `ZITADEL_API_URL=https://auth.dev.liverty-music.app`) caused the Login UI Pod to hairpin through the GCP HTTPS LB external IP back into the same cluster. Node's HTTP/1.1 client + GCP HTTPS LB exhibits intermittent 30s hangs (record-layer faults documented in Zitadel upstream PR #12022). The canonical upstream solution — used by `zitadel/zitadel-charts` and `zitadel/zitadel/deploy/compose/docker-compose.yml` — is to route via the in-cluster Service while presenting the external hostname as `Host` header. The Login V2 UI's `apps/login/src/lib/custom-headers.ts` parses `CUSTOM_REQUEST_HEADERS` and merges those headers into every outbound Connect-RPC call; the API's `instance_interceptor` resolves the instance from the `Host` header against the configured `InstanceDomains` (which already includes the ExternalDomain). No InstanceCustomDomain registration, System User, or JWT signing pipeline is required.

#### Scenario: Login UI does NOT hairpin through the external Gateway

- **WHEN** the `zitadel-web` Pod issues an outbound Connect-RPC request
- **THEN** the request SHALL be routed via the chart-rendered cluster-internal Service (resolvable as `zitadel-api.zitadel.svc.cluster.local`)
- **AND** the request SHALL NOT traverse the GKE Gateway external IP

#### Scenario: Outbound calls present the public Host header

- **WHEN** the API Pod receives a request from the Login UI Pod
- **THEN** the `Host` header on that request SHALL equal the configured `ExternalDomain`
- **AND** the API SHALL match the `Host` header to a configured `InstanceDomain` and resolve the request to the correct virtual instance
