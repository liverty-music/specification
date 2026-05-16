# frontend-hosting Specification

## ADDED Requirements

### Requirement: Caddy SHALL serve `/config.json` with no-cache headers

The Caddy web server in the frontend container SHALL serve `/config.json` from the document root (`/srv/config.json`) with `Cache-Control: no-cache, no-store, must-revalidate` and `Content-Type: application/json; charset=utf-8` response headers. This ensures that ConfigMap updates (followed by pod rollout) propagate to clients on the next page load without depending on cache busting at the URL level.

#### Scenario: Caddyfile defines the /config.json header rule

- **WHEN** inspecting `frontend/Caddyfile`
- **THEN** a matcher SHALL be defined for `path /config.json`
- **AND** the matcher SHALL set `Cache-Control` to a value containing `no-cache`
- **AND** the matcher SHALL set `Content-Type` to `application/json; charset=utf-8` (the file extension default also produces JSON, but the explicit header guards against future mount-source changes)

#### Scenario: Live response carries the headers

- **WHEN** running `curl -I https://<env>.liverty-music.app/config.json` (or the apex for prod)
- **THEN** the response status SHALL be `200`
- **AND** the `Cache-Control` header SHALL contain `no-cache`
- **AND** the `Content-Type` header SHALL be `application/json` (charset suffix permitted)

### Requirement: Frontend Deployment SHALL mount a per-environment runtime-config ConfigMap

The Kubernetes Deployment for the `web-app` container SHALL mount a ConfigMap volume at `/srv/config.json` using a `subPath` mount, sourced from a ConfigMap named `web-app-runtime-config` in the same namespace. Each environment overlay under `cloud-provisioning/k8s/namespaces/frontend/overlays/<env>/` SHALL define this ConfigMap with the values appropriate for that environment. The Deployment SHALL carry a Reloader annotation so that ConfigMap changes trigger a rolling restart.

#### Scenario: Base Deployment declares the volume and volumeMount

- **WHEN** inspecting `cloud-provisioning/k8s/namespaces/frontend/base/web/deployment.yaml` (or an equivalent base patch)
- **THEN** the `caddy` container SHALL declare a `volumeMounts` entry with `name: runtime-config`, `mountPath: /srv/config.json`, and `subPath: config.json`
- **AND** the pod template SHALL declare a `volumes` entry with `name: runtime-config` sourced from a ConfigMap with `name: web-app-runtime-config`

#### Scenario: Per-environment overlay defines the ConfigMap

- **WHEN** inspecting `cloud-provisioning/k8s/namespaces/frontend/overlays/<env>/` for each env in `{dev, prod}` (and `staging` if/when introduced)
- **THEN** a ConfigMap named `web-app-runtime-config` SHALL exist (defined inline in `configmap.yaml` or via `configMapGenerator`)
- **AND** the ConfigMap SHALL have a `config.json` key whose value parses as JSON
- **AND** the parsed JSON SHALL conform to the AppConfig schema declared in the `frontend-runtime-config` capability
- **AND** the `environment` field SHALL match the overlay's environment identifier (`dev` → `dev`, `prod` → `prod`)

#### Scenario: Reloader annotation triggers rollout on ConfigMap change

- **WHEN** inspecting the rendered `web-app` Deployment in any environment overlay
- **THEN** the Deployment metadata SHALL include the annotation `reloader.stakater.com/auto: "true"`
- **AND** when the `web-app-runtime-config` ConfigMap is updated in-cluster, Reloader SHALL initiate a rolling restart of the Deployment within 30 seconds

#### Scenario: Pod is healthy with the mounted config

- **WHEN** a pod from this Deployment is running
- **AND** `kubectl exec` into the container reads `/srv/config.json`
- **THEN** the file content SHALL equal the `config.json` value from the ConfigMap (modulo trailing whitespace)
- **AND** `curl localhost/config.json` from inside the pod SHALL return the same content with the headers defined in the "Caddy SHALL serve `/config.json` with no-cache headers" requirement

### Requirement: Post-deploy smoke verification SHALL assert the SPA renders

After any deploy that updates the frontend image or ConfigMap in any environment, an automated post-deploy smoke check SHALL fetch the environment's homepage URL, load it in a headless browser (Playwright), and assert that the rendered DOM is non-empty and that the SPA's first-screen UI element is present. This catches blank-page regressions agnostic of root cause. The smoke run SHALL be bounded by a wall-clock timeout (60 seconds default) so that a hanging deploy fails closed rather than indefinitely blocking the pipeline.

#### Scenario: Smoke check asserts non-empty rendered DOM

- **WHEN** the smoke check loads `https://<env-host>/` after a deploy
- **AND** waits for `networkidle` (or equivalent stabilization signal)
- **THEN** `document.body.innerText.trim()` SHALL be non-empty
- **AND** at least one element matching the welcome route's first-screen selector (e.g., `.welcome-hero` or `[data-screen-1]`) SHALL be present in the DOM

#### Scenario: Smoke check validates /config.json environment field

- **WHEN** the smoke check fetches `https://<env-host>/config.json` after a deploy
- **THEN** the response's `environment` field SHALL equal the expected environment for that host (`dev` for `dev.liverty-music.app`, `prod` for `liverty-music.app`)

#### Scenario: Smoke failure blocks promotion

- **WHEN** a deploy to a non-prod environment triggers the smoke check
- **AND** any smoke assertion fails OR the smoke run exceeds its wall-clock timeout
- **THEN** the deploy workflow SHALL be marked failed
- **AND** the promotion of the same artifact to the next environment SHALL NOT proceed automatically
