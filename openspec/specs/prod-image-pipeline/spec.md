# prod-image-pipeline Specification

## Purpose

Defines the container-image build and deployment pipeline for the production environment. Covers release-tag-triggered image builds (backend and frontend), env-scoped Artifact Registry routing, conditional image tagging, prod-only Workload Identity authentication, kustomize overlay image pinning, and cross-project IAM isolation.

## Requirements

### Requirement: Prod container images SHALL be sourced exclusively from the prod project's Artifact Registry

Every container image referenced by a workload in the `liverty-music-prod` GKE cluster SHALL be pulled from an Artifact Registry repository hosted in the `liverty-music-prod` GCP project. Images SHALL NOT be pulled from `liverty-music-dev` (or any other project's) Artifact Registry. Per-environment AR repositories already exist in both projects (`backend` and `frontend` Docker repos created by Pulumi); the requirement here is that the *source* used by prod pulls aligns with the cluster's owning project, eliminating the bootstrap-era cross-project pull pattern.

#### Scenario: Backend prod images come from prod AR

- **WHEN** inspecting any backend Deployment in the prod cluster (`server-app`, `consumer-app`, `concert-discovery-app`, `artist-image-sync-app`)
- **THEN** the container `image` field SHALL match the prefix `asia-northeast2-docker.pkg.dev/liverty-music-prod/backend/`

#### Scenario: Frontend prod image comes from prod AR

- **WHEN** inspecting the frontend `web-app` Deployment in the prod cluster
- **THEN** the container `image` field SHALL match the prefix `asia-northeast2-docker.pkg.dev/liverty-music-prod/frontend/`

#### Scenario: No cross-project image references in prod kustomize overlays

- **WHEN** running `kustomize build k8s/namespaces/<backend|frontend>/overlays/prod` and grepping rendered Deployment images
- **THEN** no rendered image URI SHALL contain the substring `liverty-music-dev/`

### Requirement: Prod cluster service accounts SHALL NOT hold cross-project Artifact Registry IAM grants

No GCP service account owned by the `liverty-music-prod` project (notably `gke-node@liverty-music-prod.iam.gserviceaccount.com` and `backend-app@liverty-music-prod.iam.gserviceaccount.com`) SHALL hold `roles/artifactregistry.reader` (or any read-equivalent role) on the `liverty-music-dev` GCP project — neither at project level nor at AR-repo level. The historical manual grant on `gke-node@liverty-music-prod` SHALL be removed.

#### Scenario: No prod SA in dev project IAM policy

- **WHEN** running `gcloud projects get-iam-policy liverty-music-dev --flatten='bindings[].members' --filter='bindings.members~liverty-music-prod'`
- **THEN** the result SHALL be empty

#### Scenario: No prod SA on dev AR repos

- **WHEN** running `gcloud artifacts repositories get-iam-policy <repo> --project=liverty-music-dev --location=asia-northeast2` for each of `backend` and `frontend`
- **THEN** no `members` entry SHALL contain `@liverty-music-prod.iam.gserviceaccount.com`

#### Scenario: Revocation runbook is documented

- **WHEN** an operator searches the cloud-provisioning runbooks
- **THEN** a runbook SHALL document the exact `gcloud projects remove-iam-policy-binding liverty-music-dev` invocation that revokes the manual grant
- **AND** the runbook SHALL warn that revocation MUST follow successful prod image migration (otherwise prod pods enter `ImagePullBackOff`)

### Requirement: Frontend prod build SHALL bake env-prod values into the SPA bundle

The frontend Vite build that produces the prod container image SHALL load environment values from a prod-specific source (a `.env.prod` file at the repo root or an equivalent build-arg mechanism), not from the default `.env` file. The prod-specific source SHALL provide all `VITE_*` keys consumed by the SPA, with values pointing at prod-side endpoints (apex `liverty-music.app`, prod Zitadel issuer at `auth.liverty-music.app`, prod SPA OIDC client_id, prod product-org-id, prod VAPID public key, `info` log level), so the resulting bundle never references dev hostnames or dev identifiers.

#### Scenario: Prod build resolves API endpoints to prod hostnames

- **WHEN** searching the prod-built `web-app` container's static assets for the string `dev.liverty-music.app`
- **THEN** zero occurrences SHALL be found
- **AND** the strings `api.liverty-music.app` and `auth.liverty-music.app` SHALL each appear in at least one JS chunk

#### Scenario: Prod build uses prod SPA OIDC client_id

- **WHEN** decoding the bundled OIDC client configuration from the prod-built `web-app` static assets
- **THEN** `client_id` SHALL equal the `liverty-music` SPA `ApplicationOidc` client_id provisioned in the prod Zitadel `liverty-music` product org

#### Scenario: Prod build uses info-level logging

- **WHEN** decoding the bundled log configuration from the prod-built `web-app` static assets
- **THEN** the log level SHALL NOT equal `debug`
- **AND** SHALL be one of `info`, `warn`, or `error`

### Requirement: Backend prod image build SHALL be triggered by GitHub Release tags

The backend `deploy.yml` workflow SHALL build and push images to `liverty-music-prod/backend` Artifact Registry only when triggered by a published GitHub Release (i.e., a `release: types: [published]` event), not on push-to-`main`. The image SHALL be tagged with the release's tag (e.g., `v1.2.3`) and with the SHA of the commit at that tag. The existing dev path (push-to-`main` → push to `liverty-music-dev/backend`) SHALL be preserved unchanged.

#### Scenario: Push to main triggers dev-only build

- **WHEN** a commit is pushed to `liverty-music/backend:main`
- **THEN** the `deploy.yml` workflow SHALL push images only to `liverty-music-dev/backend/{server,consumer,concert-discovery,artist-image-sync}`
- **AND** SHALL NOT push to `liverty-music-prod/backend/*`

#### Scenario: GitHub Release publish triggers prod-only build

- **WHEN** a GitHub Release is published in `liverty-music/backend` with tag `vX.Y.Z`
- **THEN** the `deploy.yml` workflow SHALL push images to `liverty-music-prod/backend/{server,consumer,concert-discovery,artist-image-sync}`
- **AND** each pushed image SHALL carry the tag `vX.Y.Z` and the commit SHA at that tag

#### Scenario: Prod build uses prod environment Workload Identity

- **WHEN** the prod build path runs
- **THEN** GitHub Actions SHALL authenticate via the `prod` environment's Workload Identity Provider (`projects/108947861615/.../github-provider` and `github-actions@liverty-music-prod.iam.gserviceaccount.com`)

### Requirement: Frontend prod image build SHALL be triggered by GitHub Release tags

The frontend `push-image.yaml` workflow SHALL build with `.env.prod` (per the build-time env requirement above) and push to `liverty-music-prod/frontend/web-app` Artifact Registry only when triggered by a published GitHub Release. The image SHALL be tagged with the release's tag and with the commit SHA. The existing dev path SHALL be preserved.

#### Scenario: Push to main triggers dev-only frontend build

- **WHEN** a commit is pushed to `liverty-music/frontend:main`
- **THEN** the workflow SHALL push only to `liverty-music-dev/frontend/web-app`
- **AND** SHALL NOT push to `liverty-music-prod/frontend/web-app`

#### Scenario: GitHub Release publish triggers prod frontend build

- **WHEN** a GitHub Release is published in `liverty-music/frontend` with tag `vX.Y.Z`
- **THEN** the workflow SHALL push to `liverty-music-prod/frontend/web-app`
- **AND** the image SHALL carry tag `vX.Y.Z` and the commit SHA
- **AND** the build SHALL have consumed `.env.prod` (asserted via the bake-time invariant in the build-bake requirement above)

### Requirement: Prod kustomize overlays SHALL pin image URIs to prod-AR paths

Each prod overlay under `cloud-provisioning/k8s/namespaces/<ns>/overlays/prod/` whose namespace contains a Deployment whose base references an image SHALL emit a kustomize `images:` transformation (or equivalent JSON 6902 patch) that rewrites the rendered image URI to the corresponding `liverty-music-prod` AR path. This prevents accidental dev-AR pulls if the base manifest's `image:` ever drifts.

#### Scenario: Backend prod overlay rewrites image URIs

- **WHEN** running `kustomize build k8s/namespaces/backend/overlays/prod`
- **THEN** every rendered Deployment's `image:` SHALL begin with `asia-northeast2-docker.pkg.dev/liverty-music-prod/backend/`

#### Scenario: Frontend prod overlay rewrites image URIs

- **WHEN** running `kustomize build k8s/namespaces/frontend/overlays/prod`
- **THEN** the rendered `web-app` Deployment's `image:` SHALL begin with `asia-northeast2-docker.pkg.dev/liverty-music-prod/frontend/`

#### Scenario: Image tags are explicit, never `:latest`

- **WHEN** inspecting any rendered prod Deployment image URI
- **THEN** the URI SHALL end with `:vX.Y.Z` (a release tag) or `:<sha>` (the commit SHA), NOT `:latest`

