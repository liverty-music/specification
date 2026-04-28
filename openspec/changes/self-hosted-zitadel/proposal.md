## Why

The `dev` environment currently depends on Zitadel Cloud (`dev-svijfm.us1.zitadel.cloud`). Three pressures motivate migration: (1) the long-term direction is to self-host Zitadel in `prod` for data residency, IDP/DAU flexibility, and freedom from SaaS tier fees — `dev` must become the operational proving ground first; (2) Zitadel v4 deprecates the Actions v1 JavaScript mechanism that currently injects the `email` claim, forcing a migration to Actions v2 webhooks regardless of hosting model; (3) operating the identity system in-cluster lets backend and frontend benefit from local JWKS/management latency and enables ephemeral per-test Zitadel instances for E2E.

## What Changes

- **BREAKING**: Replace the Zitadel Cloud issuer with an in-cluster, self-hosted deployment reachable at `https://auth.dev.liverty-music.app`. All OIDC clients (frontend, backend JWT validator, Playwright auth state) must be reconfigured.
- **BREAKING**: Drop all existing `dev` user-scoped data (users, follows, onboarding state) — no migration path is provided; existing Zitadel Cloud users will not exist in the new instance.
- Deploy Zitadel v4.11+ (PG18 support required) as a two-container Kubernetes workload: `zitadel` API (port 8080) plus `zitadel-login` Login V2 UI (port 3000), served behind a single GKE Gateway + managed certificate, with path-based `HTTPRoute` split on `/ui/v2/login/*`.
- Database hosting: reuse the existing Cloud SQL `postgres-osaka` (PG18) with a dedicated `zitadel` database and `zitadel@...iam` IAM-authenticated role. Cloud SQL Auth Proxy sidecar with `--auto-iam-authn` removes the need for a password-bearing DSN secret.
- Migrate Actions v1 (`addEmailClaim` JS + auto-verify-email) to Actions v2 Executions/Targets backed by a new backend HTTP endpoint (`/pre-access-token`) that verifies the incoming webhook via `PAYLOAD_TYPE_JWT` using the Zitadel-issued JWT (same JWKS already trusted by the backend).
- Pulumi provisioning: retain `@pulumiverse/zitadel` for v1 resources (Project, ApplicationOidc, LoginPolicy, SmtpConfig, MachineUser) and introduce a custom Pulumi Dynamic Resource that calls the Zitadel REST API for v2 Target/Execution resources, because the pulumiverse provider (v0.2.0) has not been regenerated against the upstream Terraform provider that added these resources.
- Introduce a `bootstrap-uploader` sidecar container co-located with the Zitadel API container in the same Pod that consumes the `ZITADEL_FIRSTINSTANCE_*`-generated admin machine key (written to a shared `emptyDir`) and uploads it to GCP Secret Manager for subsequent Pulumi stack reads — closing the bootstrap chicken-and-egg inside CI/CD without the cross-Pod-volume problem a separate Job would face.
- TLS mode runs as `external` (Gateway terminates TLS, cluster traffic is HTTP/h2c); the masterkey is generated once and stored immutably in Secret Manager; Zitadel is scheduled onto the existing shared spot node pool with `PodDisruptionBudget` and `podAntiAffinity` to absorb single-pod eviction in `dev`.

## Capabilities

### New Capabilities
- `zitadel-self-hosted-deployment`: Defines the Kubernetes-hosted Zitadel runtime — Helm/Kustomize manifests, two-container layout, Cloud SQL Auth Proxy sidecar with IAM auth, resource limits, HPA/PDB, Gateway routing, in-pod `bootstrap-uploader` sidecar container, masterkey handling, and spot-eviction posture for `dev`.
- `zitadel-action-webhook`: Defines the backend `/pre-access-token` webhook handler that receives Zitadel Actions v2 `preaccesstoken` function calls, verifies the `PAYLOAD_TYPE_JWT` request via the existing JWKS validator, and returns an `append_claims` response that injects the user's `email` claim into the issued access token.

### Modified Capabilities
- `identity-management`: The auto-verify-email behavior migrates from an Actions v1 JavaScript Action on the `INTERNAL_AUTHENTICATION/PRE_CREATION` flow to an Actions v2 Execution + Target pointing at a backend webhook. New requirements are added for the email-claim injection Execution and for the v2 Target / Execution provisioning flow in Pulumi. Existing requirements for Organization, Project, OIDC Application, and Login Policy are unaffected at the requirement level (only the provider `domain` input changes, which is configuration, not spec behavior).
- `authentication`: The backend gains a requirement for verifying Zitadel-issued Actions v2 webhook JWTs using the same JWKS already trusted for end-user access tokens, and for populating the issued access token `email` claim via the new v2 injection path rather than the v1 JS Action.

## Impact

**Affected repositories**
- `cloud-provisioning/`: `src/zitadel/*` (rewrite to target self-hosted), `src/gcp/components/*` (Cloud SQL database + IAM user, GSM secrets, DNS, managed cert), `k8s/namespaces/zitadel/*` (new Kustomize base + dev overlay, ArgoCD application), package.json (possibly add SDK deps for Dynamic Resource HTTP calls).
- `backend/`: new `/pre-access-token` HTTP endpoint + Connect-independent handler, `OIDC_ISSUER_URL` configmap change, Atlas migration to truncate user-scoped tables, `email_verifier` integration unchanged but pointed at new Zitadel.
- `frontend/`: `.env` / Vite variables for `VITE_ZITADEL_ISSUER`, `VITE_ZITADEL_CLIENT_ID`, `VITE_ZITADEL_ORG_ID`; `.auth/` Playwright storage states regenerated.

**APIs / interfaces**
- Zitadel OIDC endpoints move under a new domain — any previously distributed client credentials against the Cloud instance become invalid.
- New internal HTTP endpoint exposed by backend for Zitadel → backend webhook traffic (in-cluster only).

**Dependencies**
- Requires Zitadel container image ≥ `v4.11.0` (for PG18 support).
- Requires Cloud SQL Auth Proxy sidecar image (existing backend pattern reused).
- Retains `@pulumiverse/zitadel@0.2.0` for v1 resources; adds internal Dynamic Resource module in `cloud-provisioning` for v2 resources.
- Requires the in-pod `bootstrap-uploader` sidecar to run on the first boot of the Zitadel API Pod so that the admin SA key lands in GSM before the next Pulumi stack apply reads it. No ArgoCD sync-wave ordering is needed because the sidecar lives in the same Pod as the Zitadel container.

**Systems**
- Rollback path: the existing Zitadel Cloud project is retained (not deleted) for the duration of `dev` stabilization; DNS and frontend env can revert to the Cloud issuer in a follow-up change if unrecoverable failures occur.
- Out of scope: `staging` and `prod` migrations, cross-cluster Zitadel replication, multi-region PostgreSQL, user data migration/export.
