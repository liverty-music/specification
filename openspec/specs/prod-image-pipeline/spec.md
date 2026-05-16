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

### Requirement: Frontend prod image SHALL be env-agnostic at the bundle level

The frontend container image SHALL be built with no env-specific build-args, so that the bundle's JavaScript chunks contain no environment-divergent literals (no hardcoded dev or prod hostnames, no OIDC client IDs, no VAPID public keys, no environment flags other than Vite's `import.meta.env.DEV` / `PROD` / `MODE` which encode "vite dev server vs. vite build artifact"). Per-environment values SHALL be sourced exclusively from `/config.json` served at request time (see `frontend-runtime-config` capability). This invariant SHALL be asserted by CI on every build.

#### Scenario: Bundle contains no env-divergent hostnames

- **WHEN** searching every JavaScript chunk in the built `dist/` output (excluding `public/config.json` which is the bundled fallback) for substrings of dev or prod hostnames (`api.dev.liverty-music.app`, `api.liverty-music.app`, `auth.dev.liverty-music.app`, `auth.liverty-music.app`)
- **THEN** zero matches SHALL be found in any chunk's compiled JavaScript

#### Scenario: Bundle contains no OIDC client IDs

- **WHEN** searching every JavaScript chunk for the literal dev OIDC client_id (`371355407710421859`) or the literal prod OIDC client_id (`373015520582107291`)
- **THEN** zero matches SHALL be found

#### Scenario: Image build receives no env-specific build-arg

- **WHEN** inspecting `frontend/Dockerfile`
- **THEN** no `ARG VITE_MODE` declaration SHALL exist
- **AND** the `npm run build` command SHALL NOT receive a `--mode` flag

#### Scenario: Same image SHA can be deployed to multiple environments

- **WHEN** the same image (by digest) is pulled by a `frontend` namespace pod in any of dev, staging, or prod clusters
- **AND** the pod's ConfigMap mount serves a `/config.json` for its target environment
- **THEN** the SPA SHALL function correctly in that environment without any image-level change

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

The frontend `push-image.yaml` workflow SHALL build and push to `liverty-music-prod/frontend/web-app` Artifact Registry only when triggered by a published GitHub Release. The build SHALL be env-agnostic (per the "Frontend prod image SHALL be env-agnostic at the bundle level" requirement) — the same Dockerfile inputs are used whether the workflow's trigger is `push: branches: [main]` (dev path) or `release: types: [published]` (prod path). The image SHALL be tagged with the release's tag and with the commit SHA. The existing dev path (push-to-main → `liverty-music-dev/frontend/web-app:latest,:<sha>`) SHALL be preserved.

#### Scenario: Push to main triggers dev-only frontend build

- **WHEN** a commit is pushed to `liverty-music/frontend:main`
- **THEN** the workflow SHALL push only to `liverty-music-dev/frontend/web-app`
- **AND** SHALL NOT push to `liverty-music-prod/frontend/web-app`

#### Scenario: GitHub Release publish triggers prod frontend build

- **WHEN** a GitHub Release is published in `liverty-music/frontend` with tag `vX.Y.Z`
- **THEN** the workflow SHALL push to `liverty-music-prod/frontend/web-app`
- **AND** the image SHALL carry tag `vX.Y.Z` and the commit SHA

#### Scenario: Prod and dev builds use identical Dockerfile inputs

- **WHEN** comparing the `docker build` invocations of the dev push path and the release prod path
- **THEN** neither invocation SHALL pass a `--build-arg VITE_MODE` (or any other env-specific build-arg)

#### Scenario: Post-build template-presence assertion gates both paths

- **WHEN** either the dev push path or the release prod path runs `npm run build`
- **THEN** a post-build assertion step SHALL run `scripts/verify-build-templates.ts` (or equivalent)
- **AND** the step SHALL fail the workflow if any route chunk under `dist/assets/*-route-*.js` does not contain its expected template-derived marker string
- **AND** the workflow SHALL refuse to push the image if the assertion fails

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

