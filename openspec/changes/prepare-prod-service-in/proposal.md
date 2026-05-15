## Why

`https://liverty-music.app/` cannot be served to real users today: the apex DNS landing change (#263) only closes the network/cert gap, while a deeper audit of the prod env-var surface (Pulumi ESC, K8s ConfigMaps, frontend build-time `.env`, GSM secrets, GitHub Actions vars, Artifact Registry IAM) revealed **eight independent gaps** that each break prod in their own way. These gaps cluster into one product question — "what does it take to actually launch?" — so we bundle them into one change rather than dribbling out four micro-changes that each leave the system half-cooked.

The change is deliberately scoped to *prerequisites for service-in*, not feature work. Every requirement closes a measurable gap surfaced during the 2026-05-15 audit (post-`refactor-unify-env-dispatch` deploy).

## What Changes

- **NEW** Frontend prod build pipeline: a release-tag-triggered GitHub Actions job builds the Vite bundle against `.env.prod` (separate from `.env`), pushes to `liverty-music-prod/frontend` Artifact Registry, and the prod kustomize overlay patches the image to that prod-AR path.
- **NEW** Backend prod build pipeline: the existing `deploy.yml` matrix gains a release-tag-triggered prod path that pushes the four images (server, consumer, concert-discovery, artist-image-sync) to `liverty-music-prod/backend` AR; prod kustomize overlay patches images to prod-AR.
- **NEW** Backend Atlas migration prod overlay: `liverty-music/backend:k8s/atlas/overlays/prod/` is created so the `backend-migrations` ArgoCD Application (already wired in cloud-provisioning) stops failing with `Unknown` sync status.
- **REMOVE** manual `gke-node@liverty-music-prod` cross-project `roles/artifactregistry.reader` grant on the `liverty-music-dev` project (a bootstrap-era band-aid that is invisible to Pulumi state). Once prod images live in the prod AR, the grant is no longer needed.
- **NEW** prod Zitadel SPA `ApplicationOidc` client (`web-frontend` equivalent of the dev one) provisioned via Pulumi, with its client_id + product-org-id surfaced to `frontend/.env.prod` (mirrors the dev recording pattern documented in `cloud-provisioning/docs/runbooks/zitadel-oauth-client-recreate.md`).
- **NEW** mainnet ticket SBT contract deployment: replace the placeholder `TICKET_SBT_ADDRESS=0x0000…` in `k8s/namespaces/backend/overlays/prod/{server,consumer,cronjob/concert-discovery}/configmap.env` with the deployed mainnet address.
- **NEW** prod ESC seeding: `gcp.monitoring.slackNotificationChannels.alertBackend`, `gcp.billingAlertEmail`, and `gcp.budgetAmountJpy` (currently MISSING in `liverty-music/prod` → `MonitoringComponent`, `ZitadelMonitoringComponent`, billing alert + budget all silently DORMANT).
- **NEW** VAPID keypair integrity invariant: the `VAPID_PUBLIC_KEY` baked into prod's K8s ConfigMaps and the `VITE_VAPID_PUBLIC_KEY` baked into the prod frontend bundle SHALL be the public half of the `vapid-private-key` GSM Secret (regenerate prod keypair if current values diverge).
- **NEW** prod blockchain mainnet-value invariant: `blockchain.{deployerPrivateKey, rpcUrl, bundlerApiKey}` in prod ESC SHALL reference mainnet (Polygon mainnet RPC, mainnet bundler API key, mainnet deployer private key) — verify by inspection during this change.
- **NEW** prod admin Google sub validation: `zitadel.adminGoogleSubs.pannpers` in prod ESC SHALL be the Google sub-id issued by the *prod* OAuth client (`108947861615-2g7me…`) for the pannpers identity, not a dev-OAuth sub.
- **CLEANUP** stale ESC fields with no live consumer: `zitadel.domain`, `zitadel.orgId` (legacy Zitadel Cloud values, removed during the self-hosted migration), and `zitadel.pulumiJwtProfileJson` (replaced by GSM `zitadel-machine-key-for-pulumi-admin`) — removed from both `liverty-music/dev` and `liverty-music/prod`.

**Explicitly out of scope** (verified-current, no change needed): `GCP_GEMINI_MODEL=gemini-3-flash-preview` stays as-is because preview is the only available `gemini-3-flash` SKU today.

## Capabilities

### New Capabilities

- `prod-image-pipeline`: contracts how prod-bound container images are built, tagged, pushed, and consumed — release-tag-driven CI build path, prod-AR-only image source for prod clusters, frontend build-time env separation via `.env.prod`, and the absence of cross-project IAM grants from prod-cluster SAs to dev-project AR.

### Modified Capabilities

- `prod-environment-bootstrap`: gains requirements that prod runtime config is filled with prod-appropriate values rather than placeholders — mainnet `TICKET_SBT_ADDRESS`, VAPID keypair integrity (configmap public ↔ GSM private match), blockchain-mainnet-value invariant, and admin Google sub correctness. These are preconditions the capability never asserted before but the `refactor-unify-env-dispatch` audit shows are required for the env to be operational.
- `gcp-cost-guardrails`: generalizes "Dev Project Billing Budget Alert" to a per-env "Project Billing Budget Alert" so that prod can declare its own budget threshold + email channel via ESC (the existing `gcpConfig.billingAlertEmail` / `gcpConfig.budgetAmountJpy` code paths are already env-agnostic; this aligns the spec).
- `atlas-operator`: gains the requirement that a `k8s/atlas/overlays/prod/` directory exists in the backend repository so the corresponding ArgoCD `backend-migrations` Application can sync (currently `Unknown` due to missing path).
- `identity-management`: extends per-env coverage — modifies "Manage OIDC Application" so the SPA `client_id` and product-org-id are committed to a per-env build-time env file (not just `.env`), and adds a sibling "Maintain Google OAuth Client in Prod Infrastructure" to mirror the dev requirement at line 477. The prod Google OAuth client already exists in the prod GCP project; the spec just needs to acknowledge it.

## Impact

**Repositories touched**:
- `liverty-music/specification` — this change's artifacts + spec deltas.
- `liverty-music/cloud-provisioning` — kustomize image patches (frontend + backend prod overlays); Pulumi component for prod SPA `ApplicationOidc`; runbook update for the IAM revocation.
- `liverty-music/frontend` — `.env.prod` addition; `push-image.yaml` workflow extended with release-tag-triggered prod build path; `environment: prod` wiring.
- `liverty-music/backend` — `deploy.yml` workflow extended with release-tag-triggered prod build path; new `k8s/atlas/overlays/prod/` directory.

**External / operator-attended actions** (cannot be done by code alone):
- Mainnet ticket SBT contract deployment + address recording.
- VAPID prod keypair generation (if current pair diverges) + GSM rotation.
- `esc env set liverty-music/prod` calls for Slack channel ID, billing email, budget amount JPY.
- `esc env rm liverty-music/{dev,prod}` calls for the three stale fields.
- `gcloud projects remove-iam-policy-binding liverty-music-dev` to revoke the manual `gke-node@prod` grant — done **after** verifying prod images now pull from prod AR (otherwise prod cluster will ImagePullBackOff).
- Pulumi prod apply (manual via Pulumi Cloud) for the new `ApplicationOidc` resource.
- Frontend release tag cut after the new workflow lands, to produce the first prod-built image.
- Backend release tag cut after the workflow + Atlas overlay land.

**Risk surface**:
- Image source migration (dev-AR → prod-AR) is irreversible without a re-push to dev-AR; sequencing matters (push to prod-AR first, then patch overlay, then revoke IAM, never reorder).
- The cross-project IAM grant revocation is the single point that, if mis-sequenced, causes `ImagePullBackOff` on every prod pod. Documented as a guarded final step.
- Prod ESC seeding does not roll back automatically; an `esc env set` with a wrong value silently produces wrong alerts/budgets until the next `pulumi up`.

**Companion follow-ups** explicitly *not* covered here (to keep this change focused):
- Continuous backend Atlas migration authoring workflow (this change only adds the prod *overlay*, not the migration cadence policy).
- Frontend `VITE_PREVIEW_ARTIST_IDS/_NAMES` prod tuning — covered as a task, but the spec-level requirement (artist list freshness) is operational, not deployment.
- Removing the `liverty-music-prod` Artifact Registry repos as a separate Pulumi cleanup if the cross-project pull pattern is ever reinstated.
