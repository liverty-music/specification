## ADDED Requirements

### Requirement: Self-Hosted Zitadel Runtime in Dev Cluster

The system SHALL run Zitadel as an in-cluster Kubernetes workload in the `dev` GKE cluster, reachable at the OIDC issuer URL `https://auth.dev.liverty-music.app`, replacing the previous dependency on a Zitadel Cloud tenant.

**Rationale**: Long-term strategy calls for self-hosted Zitadel in all environments. Running in-cluster eliminates SaaS tier constraints, gives full control over release cadence, and lets the backend reach the JWKS endpoint without leaving the cluster.

#### Scenario: Issuer reachable at the dev domain

- **WHEN** an OIDC client resolves `https://auth.dev.liverty-music.app/.well-known/openid-configuration`
- **THEN** the system SHALL return Zitadel's discovery document
- **AND** the `issuer` field SHALL equal `https://auth.dev.liverty-music.app`
- **AND** the response SHALL be served by the in-cluster Zitadel deployment, not Zitadel Cloud

#### Scenario: Zitadel version meets PG18 requirement

- **WHEN** the Zitadel container is started
- **THEN** the image tag SHALL be `v4.11.0` or later
- **AND** the startup SHALL succeed against the `POSTGRES_18` Cloud SQL instance

### Requirement: Login V2 UI Calls Zitadel API via Public URL

The `zitadel-login` container SHALL set `ZITADEL_API_URL` to the public issuer URL (`https://auth.dev.liverty-music.app`), NOT the cluster-internal Service URL (`http://zitadel.zitadel.svc.cluster.local`).

**Rationale**: Zitadel v4 selects the virtual instance from the request's `Host` header and matches it against the configured `InstanceDomains`. The cluster-internal Service hostname is not registered as an InstanceDomain, so calls with `Host: zitadel.zitadel.svc.cluster.local` return HTTP 404 before reaching any handler — the Login UI's SSR sees `Failed to fetch security settings ... status:404` and returns HTTP 500. Setting `ZITADEL_API_URL` to the public URL makes the Login UI's outbound calls carry the correct `Host` header. Traffic still stays in-cluster (Login Pod → Gateway external IP → HTTPRoute `/` catch-all → `zitadel` API Service); the Gateway round-trip adds ~10ms versus a direct Service hop, acceptable for dev.

#### Scenario: Login UI Pod reaches Zitadel API via the public hostname

- **WHEN** the `zitadel-login` Pod issues an outbound request to fetch instance settings
- **THEN** the request URL SHALL be `https://auth.dev.liverty-music.app/...`
- **AND** the resulting `Host` header SHALL match the configured `ExternalDomain`
- **AND** Zitadel SHALL resolve the request to the correct virtual instance

#### Scenario: Login UI does not bypass the Gateway

- **WHEN** the `zitadel-login` Pod's `ZITADEL_API_URL` is configured
- **THEN** the value SHALL be the public HTTPS URL (terminated at the Gateway)
- **AND** the value SHALL NOT be the cluster-internal Service URL — that bypass produces 404s because the Service hostname is not in `InstanceDomains`
