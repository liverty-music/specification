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

#### Scenario: Prod CI SA holds repo-scoped reader on dev backend AR

- **WHEN** running `gcloud artifacts repositories get-iam-policy backend --project=liverty-music-dev --location=asia-northeast2 --flatten='bindings[].members' --filter='bindings.members~github-actions@liverty-music-prod'`
- **THEN** the output SHALL contain a binding for `roles/artifactregistry.reader`
- **AND** the binding SHALL be at the repository resource level (not project IAM)

#### Scenario: Prod CI SA holds NO writer or admin on dev AR

- **WHEN** running `gcloud artifacts repositories get-iam-policy <repo> --project=liverty-music-dev --location=asia-northeast2 --flatten='bindings[].members' --filter='bindings.members~github-actions@liverty-music-prod'` for each of `frontend` and `backend`
- **THEN** the output SHALL NOT contain `roles/artifactregistry.writer`, `roles/artifactregistry.repoAdmin`, or `roles/artifactregistry.admin`

#### Scenario: Prod CI SA holds NO project-level reader on dev project

- **WHEN** running `gcloud projects get-iam-policy liverty-music-dev --flatten='bindings[].members' --filter='bindings.members~github-actions@liverty-music-prod'`
- **THEN** the result SHALL be empty (the grants live at the repo level, not the project level)

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

### Requirement: Backend prod images SHALL be promoted to prod AR on GitHub Release tags

The backend `deploy.yml` workflow SHALL publish to `liverty-music-prod/backend/{server,consumer,concert-discovery,artist-image-sync}` Artifact Registry only when triggered by a published GitHub Release. On the release path, for each of the 4 images in the workflow's strategy matrix, the workflow SHALL **promote the dev AR image via cross-repository copy** rather than rebuild — it resolves the dev AR digest for `<image-name>:${GITHUB_SHA}`, then invokes `crane copy` (from `google/go-containerregistry`, installed via `imjasonh/setup-crane`) twice to copy that exact digest to `liverty-music-prod/backend/<image-name>:<release-tag>` and `:<sha>`. No `docker build` SHALL run on the release path. The dev path (push-to-`main`) SHALL guarantee a resolvable `liverty-music-dev/backend/<image-name>:<sha>` for every `main` commit — by build or by parent-digest inheritance (see "Every main commit SHALL have a resolvable dev AR image") — so a release cut on `main` HEAD always resolves. This ensures prod runs byte-identical bytes to dev for every backend image: the digests tested in dev are the digests deployed to prod.

#### Scenario: Push to main triggers dev-only backend build or inherit

- **WHEN** a commit is pushed to `liverty-music/backend:main`
- **THEN** the `deploy.yml` workflow SHALL publish (by build or by parent-digest inheritance) only to `liverty-music-dev/backend/{server,consumer,concert-discovery,artist-image-sync}`
- **AND** SHALL NOT push to `liverty-music-prod/backend/*`

#### Scenario: GitHub Release publish promotes the 4 dev AR digests

- **WHEN** a GitHub Release is published in `liverty-music/backend` with tag `vX.Y.Z`
- **THEN** the workflow SHALL NOT invoke `docker build` or `docker/build-push-action` on the release path for any of the 4 matrix entries
- **AND** for each `<image-name>` in `{server, consumer, concert-discovery, artist-image-sync}` the workflow SHALL resolve the dev AR digest for `asia-northeast2-docker.pkg.dev/liverty-music-dev/backend/<image-name>:${GITHUB_SHA}` via `gcloud artifacts docker images describe`
- **AND** for each `<image-name>` the workflow SHALL run `crane copy asia-northeast2-docker.pkg.dev/liverty-music-dev/backend/<image-name>@<digest> asia-northeast2-docker.pkg.dev/liverty-music-prod/backend/<image-name>:vX.Y.Z`
- **AND** for each `<image-name>` the workflow SHALL run `crane copy asia-northeast2-docker.pkg.dev/liverty-music-dev/backend/<image-name>@<digest> asia-northeast2-docker.pkg.dev/liverty-music-prod/backend/<image-name>:${GITHUB_SHA}`
- **AND** the workflow SHALL invoke `gcloud auth configure-docker asia-northeast2-docker.pkg.dev` before the copy steps (in every matrix entry) so `crane`'s authentication (which reads `~/.docker/config.json` credential helpers, not `GOOGLE_APPLICATION_CREDENTIALS` directly) resolves to the prod CI service account's WIF token

#### Scenario: Prod and dev backend images share the same digest after promotion

- **WHEN** comparing `gcloud artifacts docker images describe asia-northeast2-docker.pkg.dev/liverty-music-dev/backend/<image-name>:<sha>` against `gcloud artifacts docker images describe asia-northeast2-docker.pkg.dev/liverty-music-prod/backend/<image-name>:vX.Y.Z` after a release event for that SHA, for any `<image-name>` in `{server, consumer, concert-discovery, artist-image-sync}`
- **THEN** the `image_summary.digest` field SHALL be identical between the two outputs

#### Scenario: Release CI SHALL refuse a matrix entry if its dev AR :<sha> is missing

- **WHEN** a GitHub Release is published with a `github.sha` for which `asia-northeast2-docker.pkg.dev/liverty-music-dev/backend/<image-name>:<sha>` does not yet exist for any matrix entry — which, given the "every main commit has a resolvable dev AR image" invariant, can only mean the build/inherit job for that commit is still in-flight (release cut seconds after the push) or that job failed for `<image-name>`
- **THEN** the affected matrix entry SHALL fail at the digest-resolve step with an explicit error referencing the recovery runbook section
- **AND** the affected matrix entry SHALL NOT publish any tag to prod AR for `<image-name>`
- **AND** the digest-resolve step SHALL retry up to 5 additional times after the initial attempt (6 total attempts) with 60-second waits between attempts, for a maximum total wait of approximately 5 minutes — to absorb the race window where a release is cut seconds after a push and the dev build/inherit is still in-flight
- **AND** the error message SHALL NOT attribute the failure to a filtered-out / non-building commit (that cause is eliminated by the invariant) and SHALL NOT instruct re-targeting to an earlier commit
- **AND** other matrix entries SHALL NOT be cancelled by a single failing entry — `strategy.fail-fast: false` SHALL be set so partial-success recovery (per the runbook) is possible

#### Scenario: Prod build uses prod environment Workload Identity

- **WHEN** the prod retag path runs (in any matrix entry)
- **THEN** GitHub Actions SHALL authenticate via the `prod` environment's Workload Identity Provider (`projects/108947861615/.../github-provider` and `github-actions@liverty-music-prod.iam.gserviceaccount.com`)

### Requirement: Frontend prod image SHALL be promoted to prod AR on GitHub Release tags

The frontend `push-image.yaml` workflow SHALL publish to `liverty-music-prod/frontend/web-app` Artifact Registry only when triggered by a published GitHub Release. On the release path, the workflow SHALL **promote the dev AR image via cross-repository copy** rather than rebuild — it resolves the dev AR digest for `github.sha`, then invokes `crane copy` (from `google/go-containerregistry`, installed via `imjasonh/setup-crane`) twice to copy that exact digest to `liverty-music-prod/frontend/web-app:<release-tag>` and `:<sha>`. No `docker build` SHALL run on the release path. The dev path (push-to-`main`) SHALL guarantee a resolvable `liverty-music-dev/frontend/web-app:<sha>` for every `main` commit — by build or by parent-digest inheritance (see "Every main commit SHALL have a resolvable dev AR image") — so a release cut on `main` HEAD always resolves. This ensures prod runs byte-identical bytes to dev: the digest tested in dev is the digest deployed to prod.

#### Scenario: Push to main triggers dev-only frontend build or inherit

- **WHEN** a commit is pushed to `liverty-music/frontend:main`
- **THEN** the workflow SHALL publish (by build or by parent-digest inheritance) only to `liverty-music-dev/frontend/web-app`
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

- **WHEN** a GitHub Release is published with a `github.sha` for which no `asia-northeast2-docker.pkg.dev/liverty-music-dev/frontend/web-app:<sha>` tag exists — which, given the "every main commit has a resolvable dev AR image" invariant, can only mean the build/inherit job for that commit is still in-flight (release cut seconds after the push) or that job failed
- **THEN** the release workflow SHALL fail at the digest-resolve step with an explicit error referencing the recovery runbook section
- **AND** the workflow SHALL NOT publish any tag to prod AR
- **AND** the digest-resolve step SHALL retry up to 5 additional times after the initial attempt (6 total attempts) with 60-second waits between attempts, for a maximum total wait of approximately 5 minutes — to absorb the race window where a release is cut seconds after a push and the dev build/inherit is still in-flight
- **AND** the error message SHALL NOT attribute the failure to a filtered-out / non-building commit (that cause is eliminated by the invariant) and SHALL NOT instruct re-targeting to an earlier commit

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

### Requirement: Every main commit SHALL have a resolvable dev AR image

For both the backend (`deploy.yml`, 4-image matrix) and frontend (`push-image.yaml`, `web-app`) pipelines, every commit observed by the push-to-`main` workflow as `${GITHUB_SHA}` SHALL have a resolvable dev-AR `<image>:${GITHUB_SHA}` tag after that workflow run completes. The workflow SHALL trigger on **every** push to `main` (the `paths:` trigger gate SHALL NOT be used to skip the workflow). The workflow SHALL decide, by diffing the pushed range `${{ github.event.before }}..${GITHUB_SHA}` against the build-relevant glob set, whether to **build** (any matched file) or **inherit** (no matched file):

- On the **build** path the workflow builds and pushes `<image>:latest,:main,:<sha>` to dev AR (unchanged from prior behavior).
- On the **inherit** path the workflow SHALL `crane copy` the parent push tip's dev-AR digest (`<image>:${{ github.event.before }}`, by digest) onto `<image>:${GITHUB_SHA}` (and re-point `:main` and `:latest` at that digest), with no `docker build`. This is byte-exact: a commit that changed no build-relevant file produces bytes identical to its parent.

This makes "any `main` commit is releasable" a true invariant: the release path's digest-resolve (`<image>:${GITHUB_SHA}`) always succeeds for a `main` HEAD. The invariant is maintained inductively; it is self-seeding because the commit that introduces this behavior edits the workflow file, which is inside the build glob set and therefore takes the build path.

The inductive chain depends on consecutive `main` pushes being processed in order: the workflow SHALL declare `concurrency: { group: <workflow>-<ref>, cancel-in-progress: false }` so push N+1's inherit step cannot start before push N's build/inherit step has finished writing `<image>:<push-N-sha>`. Without this, a merge train (back-to-back merges) could leave push N+1 unable to resolve its parent, breaking the chain.

A force-push or branch-creation push SHALL take the BUILD path, never the inherit path: on a force-push `github.event.before` is the **previous (now-orphaned) tip**, not the zero SHA, and that tip is not necessarily an ancestor of the new tip — inheriting its digest would pin `<image>:${GITHUB_SHA}` to non-equivalent bytes. The zero `before` SHA (true branch creation) likewise has no valid ancestor image to inherit. Both are routed to build.

#### Scenario: Build-relevant push produces a built image

- **WHEN** a push to `main` changes at least one file matching the build glob set (backend: `**.go`, `go.mod`, `go.sum`, `Dockerfile`, `.github/workflows/deploy.yml`; frontend: `src/**`, `public/**`, `scripts/**`, `package.json`, `package-lock.json`, `vite.config.ts`, `Dockerfile`, `Caddyfile`, `.github/workflows/push-image.yaml`) anywhere in `${{ github.event.before }}..${GITHUB_SHA}`
- **THEN** the workflow SHALL build and push `<image>:${GITHUB_SHA}` (and `:latest`, `:main`) to the dev AR for every image in the pipeline (the 4 backend matrix images, or frontend `web-app`)

#### Scenario: Build-irrelevant push inherits the parent digest

- **WHEN** a normal (non-forced, non-creation) push to `main` changes no file matching the build glob set across `${{ github.event.before }}..${GITHUB_SHA}` (e.g., a CI-config- or docs-only commit)
- **THEN** the workflow SHALL NOT invoke `docker build`
- **AND** for every image in the pipeline it SHALL resolve the dev-AR digest of `<image>:${{ github.event.before }}` and `crane copy` it to `<image>:${GITHUB_SHA}`
- **AND** the resulting `<image>:${GITHUB_SHA}` digest SHALL equal the `<image>:${{ github.event.before }}` digest

#### Scenario: A release cut on main HEAD always resolves a dev image

- **WHEN** a GitHub Release is published on the current `main` HEAD, regardless of whether HEAD was a build-relevant or build-irrelevant commit
- **THEN** the release path's digest-resolve for `<image>:${GITHUB_SHA}` SHALL succeed for every image (the failure mode "HEAD is a filtered-out commit with no image" no longer occurs)

#### Scenario: Force-push or branch-creation takes the build path

- **WHEN** a push to `main` is a force-push (`github.event.forced == true`) or a branch creation (`github.event.created == true`, i.e. `github.event.before` is the zero SHA)
- **THEN** the workflow SHALL take the BUILD path and SHALL NOT take the inherit path
- **AND** it SHALL NOT inherit a digest from `github.event.before` (which on a force-push is an orphaned, non-ancestor tip whose bytes are not equivalent to the new commit's tree)

#### Scenario: Missing parent image fails loudly with no tag fallback

- **WHEN** the inherit path runs (a normal, non-forced push that changed no build-relevant file) and the parent digest `<image>:${{ github.event.before }}` cannot be resolved
- **THEN** the workflow SHALL classify the resolve failure: an auth failure (`PERMISSION_DENIED` / `401` / `403`) SHALL fail fast with auth-specific guidance; a transient failure SHALL be retried within a bounded budget; a genuine `NOT_FOUND` after retries SHALL fail with a non-zero exit and a message instructing the operator to seed the chain (push a build-relevant change) and re-cut the release on the new HEAD
- **AND** the workflow SHALL NOT fall back to any other tag (`:main`, `HEAD^1`, or otherwise) to obtain a digest — when `<image>:${{ github.event.before }}` is missing the chain has a gap, so any other tag may resolve to a commit whose tree differs, and inheriting it would pin non-equivalent bytes
- **AND** the workflow SHALL NOT publish a `<image>:${GITHUB_SHA}` tag pointing at an incorrect digest

#### Scenario: Consecutive main pushes are serialized to preserve the chain

- **WHEN** two pushes to `main` occur in rapid succession (e.g., a merge train)
- **THEN** the workflow's `concurrency` group (`<workflow>-<ref>`, `cancel-in-progress: false`) SHALL serialize them so the second run's parent-digest resolution observes the first run's completed `<image>:<sha>` write

