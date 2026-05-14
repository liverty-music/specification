## MODIFIED Requirements

### Requirement: Self-Hosted Zitadel Runtime in Each Environment Cluster

The system SHALL run Zitadel as an in-cluster Kubernetes workload in each environment's GKE cluster (`dev` and `prod`), reachable at the environment-specific OIDC issuer URL, replacing the previous dependency on a Zitadel Cloud tenant.

| Environment | Cluster | OIDC issuer |
|---|---|---|
| `dev` | `standard-cluster-osaka` (`liverty-music-dev`) | `https://auth.dev.liverty-music.app` |
| `prod` | `autopilot-cluster-osaka` (`liverty-music-prod`) | `https://auth.liverty-music.app` |

**Rationale**: Long-term strategy calls for self-hosted Zitadel in all environments. Running in-cluster eliminates SaaS tier constraints, gives full control over release cadence, and lets the backend reach the JWKS endpoint without leaving the cluster. The `prod-k8s-manifests` change extends this requirement (originally dev-scoped under the `self-hosted-zitadel` change) to also cover the prod cluster after `migrate-prod-to-autopilot` brought the prod Autopilot cluster online.

#### Scenario: Issuer reachable at the dev domain

- **WHEN** an OIDC client resolves `https://auth.dev.liverty-music.app/.well-known/openid-configuration`
- **THEN** the system SHALL return Zitadel's discovery document
- **AND** the `issuer` field SHALL equal `https://auth.dev.liverty-music.app`
- **AND** the response SHALL be served by the in-cluster Zitadel deployment in the dev cluster, not Zitadel Cloud

#### Scenario: Issuer reachable at the prod domain

- **WHEN** an OIDC client resolves `https://auth.liverty-music.app/.well-known/openid-configuration`
- **THEN** the system SHALL return Zitadel's discovery document
- **AND** the `issuer` field SHALL equal `https://auth.liverty-music.app`
- **AND** the response SHALL be served by the in-cluster Zitadel deployment in the prod cluster, not Zitadel Cloud

#### Scenario: Zitadel version meets PG18 requirement

- **WHEN** the Zitadel container is started in either env
- **THEN** the image tag SHALL be `v4.11.0` or later
- **AND** the startup SHALL succeed against the `POSTGRES_18` Cloud SQL instance

#### Scenario: Prod Zitadel uses prod Cloud SQL + prod GSM secrets

- **WHEN** inspecting the rendered `k8s/namespaces/zitadel/overlays/prod/` manifests
- **THEN** the `cloud-sql-proxy` sidecar SHALL connect to the prod Cloud SQL instance `liverty-music-prod:asia-northeast2:postgres-osaka`
- **AND** the `ExternalSecret` resources SHALL reference the `liverty-music-prod` GSM secrets (`zitadel-machine-key`, `zitadel-login-pat`) via the prod-scoped `ClusterSecretStore`
- **AND** the bootstrap admin SA key SHALL be present in `zitadel-machine-key` BEFORE the first Zitadel sync (manually seeded via `gcloud secrets versions add` per the §10.1 incident note from the prior dev deployment)
