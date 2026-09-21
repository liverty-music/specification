## MODIFIED Requirements

### Requirement: CI service accounts MAY hold scoped cross-project AR reader for image promotion

The `github-actions@liverty-music-prod.iam.gserviceaccount.com` service account MAY hold `roles/artifactregistry.reader` on `liverty-music-dev` Artifact Registry repositories, bound at the **repository resource level** (not the project level), for the sole purpose of resolving and copying image digests during release-triggered prod promotion. The binding SHALL be declared in Pulumi and SHALL be limited to repositories whose images participate in the dev → prod retag flow. The grant is structurally distinct from cluster-SA cross-project grants (forbidden above) because CI service accounts are ephemeral Workflow-run identities scoped via Workload Identity Federation to a specific GitHub repo, with no persistent runtime presence in any cluster.

> **Scope of this modification**:
> - **REMOVES** the "Backend dev AR is NOT yet granted (forward-looking)" scenario — the gap it documented is now closed by this change's tasks §1.
> - **ADDS** the positive-presence scenario "Prod CI SA holds repo-scoped reader on dev backend AR".
> - **UPDATES** the "Prod CI SA holds NO writer or admin on dev AR" scenario: canonical asserted only against `frontend`; the delta generalises to iterate `<repo>` over `{frontend, backend}` so the no-writer/admin invariant covers both grants. Same intent, broader assertion surface.
> - **UNCHANGED**: requirement body, the "Prod CI SA holds repo-scoped reader on dev frontend AR" scenario, and the "Prod CI SA holds NO project-level reader on dev project" scenario.

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
