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

No GCP service account **that runs inside a `liverty-music-prod` GKE cluster** (notably `gke-node@liverty-music-prod.iam.gserviceaccount.com` and `backend-app@liverty-music-prod.iam.gserviceaccount.com`) SHALL hold `roles/artifactregistry.reader` (or any read-equivalent role) on the `liverty-music-dev` GCP project — neither at project level nor at AR-repo level. The historical manual grant on `gke-node@liverty-music-prod` SHALL be removed. **CI service accounts (e.g., `github-actions@liverty-music-prod`) are exempt** — see "CI service accounts MAY hold scoped cross-project AR reader for image promotion" below. The two categories are operationally distinct: cluster SAs hold persistent runtime privilege that is exfiltratable via a compromised Pod; CI SAs are short-lived Workflow-run identities whose impersonation is bound by Workload Identity Federation to a specific GitHub repo and ref.

#### Scenario: No prod cluster SA in dev project IAM policy

- **WHEN** running `gcloud projects get-iam-policy liverty-music-dev --flatten='bindings[].members' --filter='bindings.members:(gke-node@liverty-music-prod.iam.gserviceaccount.com OR backend-app@liverty-music-prod.iam.gserviceaccount.com)'`
- **THEN** the result SHALL be empty (the CI-SA's project-level absence is asserted by the CI-SA carve-out's own scenarios)

#### Scenario: No prod cluster SA on dev AR repos

- **WHEN** running `gcloud artifacts repositories get-iam-policy <repo> --project=liverty-music-dev --location=asia-northeast2 --flatten='bindings[].members' --filter='bindings.members:(gke-node@liverty-music-prod.iam.gserviceaccount.com OR backend-app@liverty-music-prod.iam.gserviceaccount.com)'` for each of `backend` and `frontend`
- **THEN** the result SHALL be empty (cluster SAs hold no repo-level grants either; the CI-SA carve-out's own scenarios assert its presence positively)

#### Scenario: Revocation runbook is documented

- **WHEN** an operator searches the cloud-provisioning runbooks
- **THEN** a runbook SHALL document the exact `gcloud projects remove-iam-policy-binding liverty-music-dev` invocation that revokes the manual grant
- **AND** the runbook SHALL warn that revocation MUST follow successful prod image migration (otherwise prod pods enter `ImagePullBackOff`)

### Requirement: CI service accounts MAY hold scoped cross-project AR reader for image promotion

The `github-actions@liverty-music-prod.iam.gserviceaccount.com` service account MAY hold `roles/artifactregistry.reader` on `liverty-music-dev` Artifact Registry repositories, bound at the **repository resource level** (not the project level), for the sole purpose of resolving and copying image digests during release-triggered prod promotion. The binding SHALL be declared in Pulumi and SHALL be limited to repositories whose images participate in the dev → prod retag flow. The grant is structurally distinct from cluster-SA cross-project grants (forbidden above) because CI service accounts are ephemeral Workflow-run identities scoped via Workload Identity Federation to a specific GitHub repo, with no persistent runtime presence in any cluster.

#### Scenario: Prod CI SA holds repo-scoped reader on dev frontend AR

- **WHEN** running `gcloud artifacts repositories get-iam-policy frontend --project=liverty-music-dev --location=asia-northeast2 --flatten='bindings[].members' --filter='bindings.members~github-actions@liverty-music-prod'`
- **THEN** the output SHALL contain a binding for `roles/artifactregistry.reader`
- **AND** the binding SHALL be at the repository resource level (not project IAM)

#### Scenario: Prod CI SA holds NO writer or admin on dev AR

- **WHEN** running `gcloud artifacts repositories get-iam-policy frontend --project=liverty-music-dev --location=asia-northeast2 --flatten='bindings[].members' --filter='bindings.members~github-actions@liverty-music-prod'`
- **THEN** the output SHALL NOT contain `roles/artifactregistry.writer`, `roles/artifactregistry.repoAdmin`, or `roles/artifactregistry.admin`

#### Scenario: Prod CI SA holds NO project-level reader on dev project

- **WHEN** running `gcloud projects get-iam-policy liverty-music-dev --flatten='bindings[].members' --filter='bindings.members~github-actions@liverty-music-prod'`
- **THEN** the result SHALL be empty (the grant lives at the repo level, not the project level)

#### Scenario: Backend dev AR is NOT yet granted (forward-looking)

- **WHEN** running `gcloud artifacts repositories get-iam-policy backend --project=liverty-music-dev --location=asia-northeast2 --flatten='bindings[].members' --filter='bindings.members~github-actions@liverty-music-prod'`
- **THEN** the output SHALL be empty (this change is frontend-only; backend retag is a separate change that will add the symmetric grant)

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

### Requirement: Frontend prod image SHALL be promoted to prod AR on GitHub Release tags

The frontend `push-image.yaml` workflow SHALL publish to `liverty-music-prod/frontend/web-app` Artifact Registry only when triggered by a published GitHub Release. On the release path, the workflow SHALL **promote the dev AR image via cross-repository copy** rather than rebuild — it resolves the dev AR digest for `github.sha`, then invokes `crane copy` (from `google/go-containerregistry`, installed via `imjasonh/setup-crane`) twice to copy that exact digest to `liverty-music-prod/frontend/web-app:<release-tag>` and `:<sha>`. No `docker build` SHALL run on the release path. The existing dev path (push-to-main → `liverty-music-dev/frontend/web-app:latest,:main,:<sha>`) SHALL be preserved unchanged. This ensures prod runs byte-identical bytes to dev: the digest tested in dev is the digest deployed to prod.

#### Scenario: Push to main triggers dev-only frontend build

- **WHEN** a commit is pushed to `liverty-music/frontend:main`
- **THEN** the workflow SHALL push only to `liverty-music-dev/frontend/web-app`
- **AND** SHALL NOT push to `liverty-music-prod/frontend/web-app`

#### Scenario: GitHub Release publish promotes the dev AR digest

- **WHEN** a GitHub Release is published in `liverty-music/frontend` with tag `vX.Y.Z`
- **THEN** the workflow SHALL NOT invoke `docker build` or `docker/build-push-action` on the release path
- **AND** the workflow SHALL resolve the dev AR digest for `asia-northeast2-docker.pkg.dev/liverty-music-dev/frontend/web-app:${GITHUB_SHA}` via `gcloud artifacts docker images describe`
- **AND** the workflow SHALL run `crane copy asia-northeast2-docker.pkg.dev/liverty-music-dev/frontend/web-app@<digest> asia-northeast2-docker.pkg.dev/liverty-music-prod/frontend/web-app:vX.Y.Z`
- **AND** the workflow SHALL run `crane copy asia-northeast2-docker.pkg.dev/liverty-music-dev/frontend/web-app@<digest> asia-northeast2-docker.pkg.dev/liverty-music-prod/frontend/web-app:${GITHUB_SHA}`
- **AND** the workflow SHALL invoke `gcloud auth configure-docker asia-northeast2-docker.pkg.dev` before the copy steps so `crane`'s authentication (which reads `~/.docker/config.json` credential helpers, not `GOOGLE_APPLICATION_CREDENTIALS` directly) resolves to the prod CI service account's WIF token

#### Scenario: Prod and dev images share the same digest after promotion

- **WHEN** comparing `gcloud artifacts docker images describe asia-northeast2-docker.pkg.dev/liverty-music-dev/frontend/web-app:<sha>` against `gcloud artifacts docker images describe asia-northeast2-docker.pkg.dev/liverty-music-prod/frontend/web-app:vX.Y.Z` after a release event for that SHA
- **THEN** the `image_summary.digest` field SHALL be identical between the two outputs

#### Scenario: Release CI SHALL refuse if dev AR :<sha> is missing

- **WHEN** a GitHub Release is published with a `github.sha` for which no `asia-northeast2-docker.pkg.dev/liverty-music-dev/frontend/web-app:<sha>` tag exists (e.g., release cut on a non-main commit, or dev build failed)
- **THEN** the release workflow SHALL fail at the digest-resolve step with an explicit error referencing the recovery runbook section
- **AND** the workflow SHALL NOT publish any tag to prod AR
- **AND** the digest-resolve step SHALL retry up to 5 additional times after the initial attempt (6 total attempts) with 60-second waits between attempts, for a maximum total wait of approximately 5 minutes — to absorb the race window where a release is cut seconds after a push and the dev build is still in-flight

#### Scenario: Post-build template-presence assertion gates the dev path

- **WHEN** the dev push path runs `npm run build` inside the Dockerfile
- **THEN** the Dockerfile's `RUN npm run verify:build-templates` step SHALL run after `npm run build`
- **AND** the step SHALL fail the build if any route chunk under `dist/assets/*-route-*.js` does not contain its expected template-derived marker string
- **AND** the failed build SHALL prevent the dev AR push
- **AND** therefore SHALL prevent any subsequent release-event retag (because the dev `:<sha>` tag never gets written, the digest-resolve guard fails closed)

### Requirement: Prod kustomize overlays SHALL pin image URIs to prod-AR paths

Each prod overlay under `cloud-provisioning/k8s/namespaces/<ns>/overlays/prod/` whose namespace contains a Deployment whose base references an image SHALL emit a kustomize `images:` transformation (or equivalent JSON 6902 patch) that rewrites the rendered image URI to the corresponding `liverty-music-prod` AR path. This prevents accidental dev-AR pulls if the base manifest's `image:` ever drifts.

#### Scenario: Backend prod overlay rewrites image URIs

- **WHEN** running `kustomize build k8s/namespaces/backend/overlays/prod`
- **THEN** every rendered Deployment's `image:` SHALL begin with `asia-northeast2-docker.pkg.dev/liverty-music-prod/backend/`

#### Scenario: Frontend prod overlay rewrites image URIs

- **WHEN** running `kustomize build k8s/namespaces/frontend/overlays/prod`
- **THEN** the rendered `web-app` Deployment's `image:` SHALL begin with `asia-northeast2-docker.pkg.dev/liverty-music-prod/frontend/`

> **Historical note**: the "Image tags are explicit, never `:latest`" scenario that previously lived under this requirement was removed during the archive of `promote-prod-image-via-retag` — it was superseded by `prod-image-tag-immutability`'s strictly stricter "Prod kustomize overlays SHALL pin image URIs to semantic version tags" requirement (which forbids `:<sha>`-only tags and `:latest`).

