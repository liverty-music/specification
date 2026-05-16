## ADDED Requirements

### Requirement: Prod Artifact Registry Docker repositories SHALL enforce tag immutability at the registry API level

Every Docker-format `gcp.artifactregistry.Repository` resource provisioned in the `liverty-music-prod` GCP project SHALL declare `dockerConfig.immutableTags = true`. Once enabled, the Artifact Registry API SHALL reject any attempt to re-point an existing tag to a different image digest (whether issued via `docker push`, `gcloud artifacts docker tags add`, or the AR REST API), returning HTTP 409 Conflict. Dev-project AR repositories SHALL remain at the default (`immutableTags = false`) because ArgoCD Image Updater requires the ability to rewrite `:latest` and `:main` tags during dev iteration.

#### Scenario: Prod backend AR repo enforces immutable tags

- **WHEN** running `gcloud artifacts repositories describe backend --project=liverty-music-prod --location=asia-northeast2 --format='value(dockerConfig.immutableTags)'`
- **THEN** the output SHALL equal `True`

#### Scenario: Prod frontend AR repo enforces immutable tags

- **WHEN** running `gcloud artifacts repositories describe frontend --project=liverty-music-prod --location=asia-northeast2 --format='value(dockerConfig.immutableTags)'`
- **THEN** the output SHALL equal `True`

#### Scenario: Dev AR repos remain mutable

- **WHEN** running `gcloud artifacts repositories describe backend --project=liverty-music-dev --location=asia-northeast2 --format='value(dockerConfig.immutableTags)'`
- **THEN** the output SHALL be empty or `False`
- **AND** the same SHALL hold for the dev `frontend` repo

#### Scenario: Attempting to re-tag an existing prod tag SHALL fail with 409 Conflict

- **WHEN** an operator runs `gcloud artifacts docker tags add asia-northeast2-docker.pkg.dev/liverty-music-prod/backend/server:<existing-digest-A> asia-northeast2-docker.pkg.dev/liverty-music-prod/backend/server:<tag-already-pointing-at-digest-B>` (i.e., attempts to re-point a tag from digest B to digest A)
- **THEN** the command SHALL fail with an error referencing HTTP 409 / "tag already exists" / "immutable tags" semantics
- **AND** the tag SHALL continue to resolve to digest B

### Requirement: Prod kustomize overlays SHALL pin image URIs to semantic version tags

Every kustomize `images:` transformation entry inside `cloud-provisioning/k8s/namespaces/<ns>/overlays/prod/kustomization.yaml` SHALL set `newTag:` to a semantic version string matching the regex `^v\d+\.\d+\.\d+(-[A-Za-z0-9.-]+)?$` (e.g., `v1.0.0`, `v1.2.3-rc1`). Commit-SHA-only tags (40-char hex) SHALL NOT appear as `newTag:` values in any prod overlay. The `:latest` tag SHALL NEVER appear in prod overlays. Each `newTag:` SHALL be accompanied by an inline comment recording the corresponding source commit SHA, in the form `newTag: vX.Y.Z  # commit <40-char-sha>` (or a multi-line equivalent comment block immediately preceding the entry), so incident-response trace from manifest → exact commit does not require an Artifact Registry round-trip.

#### Scenario: Backend prod overlay uses semver tags only

- **WHEN** reading `cloud-provisioning/k8s/namespaces/backend/overlays/prod/kustomization.yaml`
- **THEN** every entry under `images:` SHALL have `newTag:` matching the regex `^v\d+\.\d+\.\d+(-[A-Za-z0-9.-]+)?$`
- **AND** no `newTag:` SHALL match a 40-character hex string (commit SHA form)
- **AND** no `newTag:` SHALL equal `latest`

#### Scenario: Frontend prod overlay uses semver tags only

- **WHEN** reading `cloud-provisioning/k8s/namespaces/frontend/overlays/prod/kustomization.yaml`
- **THEN** the `web-app` `images:` entry SHALL have `newTag:` matching the regex `^v\d+\.\d+\.\d+(-[A-Za-z0-9.-]+)?$`
- **AND** the `newTag:` value SHALL NOT match a 40-character hex string
- **AND** the `newTag:` value SHALL NOT equal `latest`

#### Scenario: Commit SHA is preserved in an inline comment

- **WHEN** reading any `newTag:` line in a prod overlay's `images:` block
- **THEN** an inline comment (`#`) on the same line OR on an adjacent line within 3 lines preceding the entry SHALL contain a 40-character lowercase hex commit SHA
- **AND** the comment SHALL be parseable by a regex of the form `#.*\b[0-9a-f]{40}\b`

#### Scenario: Rendered Deployment image references carry the semver tag

- **WHEN** running `kubectl kustomize cloud-provisioning/k8s/namespaces/backend/overlays/prod` and extracting `.spec.template.spec.containers[*].image` from all rendered Deployments + CronJobs
- **THEN** every rendered image URI SHALL end with `:vX.Y.Z` matching the semver regex
- **AND** the same SHALL hold for `cloud-provisioning/k8s/namespaces/frontend/overlays/prod` (the rendered `web-app` Deployment image)

### Requirement: Prod workload Deployments and CronJobs SHALL carry the app.kubernetes.io/version Recommended Label

Every `Deployment` and `CronJob` rendered from a prod overlay under `cloud-provisioning/k8s/namespaces/<backend|frontend>/overlays/prod/` SHALL carry the Kubernetes Recommended Label `app.kubernetes.io/version` with a value matching the semver pinned in the overlay's `newTag:` for that workload's image. The label value SHALL be the bare semver without the leading `v` (per the Kubernetes Recommended Labels convention: `app.kubernetes.io/version: "1.0.0"`, not `"v1.0.0"`). The label SHALL be applied via a kustomize patch in the prod overlay; the base manifests SHALL NOT carry the label (because dev tags are not stable semvers).

The label SHALL propagate to the Pod template (`spec.template.metadata.labels`) so that Prometheus Pod-level label scraping and OTel resource processors pick up the version dimension.

#### Scenario: Backend prod Deployments carry the version label

- **WHEN** running `kubectl --context=prod -n backend get deploy -o jsonpath='{range .items[*]}{.metadata.labels.app\.kubernetes\.io/version}{"\n"}{end}'`
- **THEN** every line SHALL be a non-empty semver string (without leading `v`) matching `^\d+\.\d+\.\d+(-[A-Za-z0-9.-]+)?$`

#### Scenario: Backend prod CronJobs carry the version label

- **WHEN** running `kubectl --context=prod -n backend get cronjob -o jsonpath='{range .items[*]}{.metadata.labels.app\.kubernetes\.io/version}{"\n"}{end}'`
- **THEN** every line SHALL be a non-empty semver string matching the same regex

#### Scenario: Frontend prod Deployment carries the version label

- **WHEN** running `kubectl --context=prod -n frontend get deploy web-app -o jsonpath='{.metadata.labels.app\.kubernetes\.io/version}'`
- **THEN** the output SHALL be a non-empty semver string matching the regex

#### Scenario: Version label propagates to Pod template

- **WHEN** rendering any prod overlay and inspecting `spec.template.metadata.labels` of any Deployment / CronJob job template
- **THEN** the Pod template SHALL also carry `app.kubernetes.io/version` with the same value as the Deployment/CronJob top-level label

#### Scenario: Dev manifests SHALL NOT carry the version label

- **WHEN** rendering any dev overlay under `cloud-provisioning/k8s/namespaces/<ns>/overlays/dev/`
- **THEN** no Deployment or CronJob SHALL carry `app.kubernetes.io/version` (because dev uses mutable `:latest`/`:main` tags and the label would convey false precision)

### Requirement: A runbook SHALL document the prod image tag pinning policy

The `cloud-provisioning` repository SHALL contain a runbook at `docs/runbooks/prod-image-tag-pinning.md` that documents: (a) which environments use immutable semver tags (prod) vs mutable rolling tags (dev); (b) the operator procedure for cutting a release and bumping the prod overlay `newTag:`; (c) the AR API behavior when an immutable tag re-push is attempted; (d) recovery procedures for the most common error scenarios (Release re-run failures, accidental manual `gcloud artifacts docker tags add`, rollback to a prior version).

#### Scenario: Runbook exists and is referenced

- **WHEN** searching `cloud-provisioning/docs/runbooks/`
- **THEN** a file named `prod-image-tag-pinning.md` SHALL exist
- **AND** the file SHALL include sections covering dev-vs-prod policy, release-cut procedure, AR rejection behavior, and recovery procedures

#### Scenario: Runbook is discoverable from the prod overlay

- **WHEN** reading a prod overlay's `kustomization.yaml`
- **THEN** a comment SHALL reference the runbook path so an operator who lands on the overlay can find the policy documentation
