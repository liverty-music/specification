## ADDED Requirements

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
