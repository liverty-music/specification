## ADDED Requirements

### Requirement: Apex serving SHALL route to the `web-app` frontend Service via HTTPRoute hostname matching
The Kubernetes HTTPRoute that serves the apex SHALL match on `hostnames: ['liverty-music.app']` and route to the `web-app` Service in the `frontend` namespace. This HTTPRoute SHALL share the same Gateway as the HTTPRoutes for `api.liverty-music.app` (routing to backend) and `auth.liverty-music.app` (routing to Zitadel) — differentiation is by HTTPRoute hostname, not by Gateway listener.

> **Note**: The HTTPRoute hostname binding is pre-existing — configured by the prior `prod-k8s-manifests` change (archived 2026-05-14) in `cloud-provisioning/k8s/namespaces/frontend/overlays/prod/kustomization.yaml`. The `consolidate-public-dns-on-cloudflare` change consumes the existing binding and verifies it via a pre-flight task; it does not author or modify any HTTPRoute YAML. The requirement is documented here because the apex-frontend-serving capability collects the end-to-end serving contract regardless of which change first satisfied each piece.

#### Scenario: Frontend HTTPRoute binds apex hostname
- **WHEN** rendering `cloud-provisioning/k8s/namespaces/frontend/overlays/prod/`
- **THEN** an `HTTPRoute` resource SHALL exist with `spec.hostnames` containing `liverty-music.app`
- **AND** the HTTPRoute SHALL reference the shared prod Gateway via `spec.parentRefs`
- **AND** the HTTPRoute SHALL route to the `web-app` Service via `spec.rules[].backendRefs`

#### Scenario: Apex traffic reaches the frontend SPA
- **WHEN** an end user requests `https://liverty-music.app/` after the prod cutover completes
- **THEN** the request SHALL receive a `200 OK` response from the Caddy-served frontend SPA
- **AND** the response body SHALL be `index.html` from the frontend container image
- **AND** the TLS certificate presented SHALL be the `web-app-cert` Google-managed certificate
