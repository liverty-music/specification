# prod-image-pipeline Specification

## MODIFIED Requirements

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

## MODIFIED Requirements (scenario removals only)

### Requirement: Prod kustomize overlays SHALL pin image URIs to prod-AR paths

> **Scope of this modification**: drops the "Image tags are explicit, never `:latest`" scenario. Requirement body and the two remaining scenarios (Backend / Frontend overlay rewrites) are unchanged.

Each prod overlay under `cloud-provisioning/k8s/namespaces/<ns>/overlays/prod/` whose namespace contains a Deployment whose base references an image SHALL emit a kustomize `images:` transformation (or equivalent JSON 6902 patch) that rewrites the rendered image URI to the corresponding `liverty-music-prod` AR path. This prevents accidental dev-AR pulls if the base manifest's `image:` ever drifts.

#### Scenario: Backend prod overlay rewrites image URIs

- **WHEN** running `kustomize build k8s/namespaces/backend/overlays/prod`
- **THEN** every rendered Deployment's `image:` SHALL begin with `asia-northeast2-docker.pkg.dev/liverty-music-prod/backend/`

#### Scenario: Frontend prod overlay rewrites image URIs

- **WHEN** running `kustomize build k8s/namespaces/frontend/overlays/prod`
- **THEN** the rendered `web-app` Deployment's `image:` SHALL begin with `asia-northeast2-docker.pkg.dev/liverty-music-prod/frontend/`

> **Reason for removing "Image tags are explicit, never `:latest`"**: superseded by `prod-image-tag-immutability`'s "Prod kustomize overlays SHALL pin image URIs to semantic version tags" requirement, which is strictly stricter — it forbids `:<sha>`-only tags that the scenario being removed permitted, and explicitly forbids `:latest`. The `prod-image-tag-immutability` spec already documents this supersession (see the "Relationship to `prod-image-pipeline`" cross-spec note in `prod-image-tag-immutability`). No operational change — the stricter rule is already in force in canonical specs. Removing the weaker scenario eliminates a contradiction that would otherwise confuse readers comparing the two specs.

> **Reason for the bonus scenario drop on the "Frontend prod image build SHALL be triggered by GitHub Release tags" requirement** ("Prod and dev builds use identical Dockerfile inputs"): the retag flow has no prod-side `docker build` invocation to compare against the dev one. The scenario's precondition (`comparing the docker build invocations of the dev push path and the release prod path`) is no longer satisfiable on the release path — only the dev path runs `docker build`. The env-agnostic-bundle invariant that this scenario asserted is preserved by the dev path's own template-presence assertion plus the byte-identity guarantee of the retag (the prod tag points at the exact same digest as the dev image that already passed the template gate). The scenario is dropped as part of the MODIFIED body replacement on that requirement above; no separate REMOVED entry is needed.
