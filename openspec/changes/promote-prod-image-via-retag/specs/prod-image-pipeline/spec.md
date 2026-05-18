# prod-image-pipeline Specification

## MODIFIED Requirements

### Requirement: Prod cluster service accounts SHALL NOT hold cross-project Artifact Registry IAM grants

No GCP service account **that runs inside a `liverty-music-prod` GKE cluster** (notably `gke-node@liverty-music-prod.iam.gserviceaccount.com` and `backend-app@liverty-music-prod.iam.gserviceaccount.com`) SHALL hold `roles/artifactregistry.reader` (or any read-equivalent role) on the `liverty-music-dev` GCP project — neither at project level nor at AR-repo level. The historical manual grant on `gke-node@liverty-music-prod` SHALL be removed. **CI service accounts (e.g., `github-actions@liverty-music-prod`) are exempt** — see "CI service accounts MAY hold scoped cross-project AR reader for image promotion" below. The two categories are operationally distinct: cluster SAs hold persistent runtime privilege that is exfiltratable via a compromised Pod; CI SAs are short-lived Workflow-run identities whose impersonation is bound by Workload Identity Federation to a specific GitHub repo and ref.

#### Scenario: No prod cluster SA in dev project IAM policy

- **WHEN** running `gcloud projects get-iam-policy liverty-music-dev --flatten='bindings[].members' --filter='bindings.members~liverty-music-prod'`
- **THEN** the result SHALL contain no `gke-node@liverty-music-prod` or `backend-app@liverty-music-prod` entry
- **AND** the result MAY contain `github-actions@liverty-music-prod` ONLY under repo-scoped resource bindings (per the CI-SA carve-out requirement)

#### Scenario: No prod cluster SA on dev AR repos

- **WHEN** running `gcloud artifacts repositories get-iam-policy <repo> --project=liverty-music-dev --location=asia-northeast2` for each of `backend` and `frontend`
- **THEN** no `members` entry SHALL contain `@liverty-music-prod.iam.gserviceaccount.com` other than the explicit CI-SA carve-out for image promotion (see scenario below)

#### Scenario: Revocation runbook is documented

- **WHEN** an operator searches the cloud-provisioning runbooks
- **THEN** a runbook SHALL document the exact `gcloud projects remove-iam-policy-binding liverty-music-dev` invocation that revokes the manual grant
- **AND** the runbook SHALL warn that revocation MUST follow successful prod image migration (otherwise prod pods enter `ImagePullBackOff`)

### Requirement: Frontend prod image build SHALL be triggered by GitHub Release tags

The frontend `push-image.yaml` workflow SHALL publish to `liverty-music-prod/frontend/web-app` Artifact Registry only when triggered by a published GitHub Release. On the release path, the workflow SHALL **promote the dev AR image via tag-add** rather than rebuild — it resolves the dev AR digest for `github.sha`, then invokes `gcloud artifacts docker tags add` twice to copy that exact digest to `liverty-music-prod/frontend/web-app:<release-tag>` and `:<sha>`. No `docker build` SHALL run on the release path. The existing dev path (push-to-main → `liverty-music-dev/frontend/web-app:latest,:<sha>`) SHALL be preserved unchanged. This ensures prod runs byte-identical bytes to dev: the digest tested in dev is the digest deployed to prod.

#### Scenario: Push to main triggers dev-only frontend build

- **WHEN** a commit is pushed to `liverty-music/frontend:main`
- **THEN** the workflow SHALL push only to `liverty-music-dev/frontend/web-app`
- **AND** SHALL NOT push to `liverty-music-prod/frontend/web-app`

#### Scenario: GitHub Release publish promotes the dev AR digest

- **WHEN** a GitHub Release is published in `liverty-music/frontend` with tag `vX.Y.Z`
- **THEN** the workflow SHALL NOT invoke `docker build` or `docker/build-push-action` on the release path
- **AND** the workflow SHALL resolve the dev AR digest for `liverty-music-dev/frontend/web-app:${github.sha}` via `gcloud artifacts docker images describe`
- **AND** the workflow SHALL run `gcloud artifacts docker tags add <dev-AR-FQDN>@<digest> liverty-music-prod/frontend/web-app:vX.Y.Z`
- **AND** the workflow SHALL run `gcloud artifacts docker tags add <dev-AR-FQDN>@<digest> liverty-music-prod/frontend/web-app:<sha>`

#### Scenario: Prod and dev images share the same digest after promotion

- **WHEN** comparing `gcloud artifacts docker images describe liverty-music-dev/frontend/web-app:<sha>` against `gcloud artifacts docker images describe liverty-music-prod/frontend/web-app:vX.Y.Z` after a release event for that SHA
- **THEN** the `image_summary.digest` field SHALL be identical between the two outputs

#### Scenario: Release CI SHALL refuse if dev AR :<sha> is missing

- **WHEN** a GitHub Release is published with a `github.sha` for which no `liverty-music-dev/frontend/web-app:<sha>` tag exists (e.g., release cut on a non-main commit, or dev build failed)
- **THEN** the release workflow SHALL fail at the digest-resolve step with an explicit error referencing the recovery runbook section
- **AND** the workflow SHALL NOT publish any tag to prod AR
- **AND** the digest-resolve step MAY retry up to 5 times with 60-second waits before failing (to absorb the race window where a release is cut seconds after a push and the dev build is still in-flight)

#### Scenario: Post-build template-presence assertion gates the dev path

- **WHEN** the dev push path runs `npm run build` inside the Dockerfile
- **THEN** the Dockerfile's `RUN npm run verify:build-templates` step SHALL run after `npm run build`
- **AND** the step SHALL fail the build if any route chunk under `dist/assets/*-route-*.js` does not contain its expected template-derived marker string
- **AND** the failed build SHALL prevent the dev AR push
- **AND** therefore SHALL prevent any subsequent release-event retag (because the dev `:<sha>` tag never gets written, the digest-resolve guard fails closed)

## ADDED Requirements

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
- **THEN** any matching binding SHALL be empty (the grant lives at the repo level, not the project level)

#### Scenario: Backend dev AR is NOT yet granted (forward-looking)

- **WHEN** running `gcloud artifacts repositories get-iam-policy backend --project=liverty-music-dev --location=asia-northeast2 --flatten='bindings[].members' --filter='bindings.members~github-actions@liverty-music-prod'`
- **THEN** the output SHALL be empty (this change is frontend-only; backend retag is a separate change that will add the symmetric grant)

## REMOVED Requirements

### Requirement: Prod kustomize overlays SHALL pin image URIs to prod-AR paths — "Image tags are explicit, never `:latest`" scenario

**Reason**: Superseded by `prod-image-tag-immutability`'s "Prod kustomize overlays SHALL pin image URIs to semantic version tags" requirement, which is strictly stricter — it forbids `:<sha>`-only tags that the scenario being removed permitted, and explicitly forbids `:latest`. The `prod-image-tag-immutability` spec already documents this supersession in its "Relationship to `prod-image-pipeline`" cross-spec note (line 47 of that spec).

**Migration**: No operational change. The stricter rule is already in force in canonical specs. Removing the weaker scenario eliminates a contradiction that would otherwise confuse readers comparing the two specs.
