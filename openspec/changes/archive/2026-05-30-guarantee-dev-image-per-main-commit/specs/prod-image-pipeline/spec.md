## MODIFIED Requirements

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
