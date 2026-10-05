## 1. Artist entity (components/entity/artist)

- [ ] 1.1 Add the Atlas migration `ALTER TABLE artists ADD COLUMN official_site_checked_at TIMESTAMPTZ` (with a column comment). Mirror it in `internal/infrastructure/database/rdb/schema/schema.sql`. Verify `atlas migrate diff --env local` reports no drift and `atlas migrate apply --env local` succeeds.
- [ ] 1.2 Add `OfficialSiteCheckTime *time.Time` to the Go Artist entity. Keep it nil in `NewArtist`. Verify the unit test for the scenarios "New artist" and "Two new artists" asserts no official_site_check_time.

## 2. Selection rule (components/entity/artist/resolve-official-site-url)

- [ ] 2.1 Narrow active `official homepage` relations to top-page URLs (empty or `/` path, no query, no fragment) when any exist, then apply the existing credit priority in `selectOfficialSiteURL`. Verify one table-driven test case per scenario passes: "Top page preferred over a label page", "Several top pages", "No top page", "Link credited to the artist's name", "Uncredited link", "Only other credits", "All links ended" and "No homepage link".
- [ ] 2.2 Add a regression table of the 30 multi-link followed artists recorded on 2026-10-05 (fixture of relation lists and expected URL). Verify the test passes with the 5 label-page artists resolving to their own domains and the other 25 unchanged.

## 3. Entity operations (components/entity/artist/list-stale-official-site, update-official-site-url, mark-official-site-checked)

- [ ] 3.1 Declare `ListStaleOfficialSite(ctx, age, limit)` on `ArtistRepository` and implement it in `rdb.ArtistRepository`. Scan `official_site_checked_at` into the entity. Verify a contract test per scenario passes against the local database: "Never-checked and stale artists", "Recently checked artist", "Followed artist without an official site", "Artist nobody follows", "More due artists than the limit" and "Nothing due".
- [ ] 3.2 Declare and implement `UpdateOfficialSiteURL(ctx, artistID, url)`, validating the URL with the OfficialSite rule. Verify a contract test per scenario passes: "Artist with a site", "Artist without a site" and "Invalid URL".
- [ ] 3.3 Declare and implement `MarkOfficialSiteChecked(ctx, artistID, t)`. Verify a contract test per scenario passes: "Artist checked", "Artist without an official site" and "Unknown artist".
- [ ] 3.4 Regenerate the `ArtistRepository` mocks with mockery. Verify `go build ./...` and `make lint` pass.

## 4. Usecase (components/usecase/artist/refresh-official-site)

- [ ] 4.1 Implement `OfficialSiteRefreshUseCase.RefreshOfficialSite(ctx, artistID, mbid)`. Log old and new URL on every create or replace. Verify one unit test per scenario passes with the operations mocked: "Catalog resolves to a different site", "Catalog resolves to the stored site", "Artist without a site gets one", "Catalog lists no active homepage", "No site anywhere" and "Catalog unreachable".
- [ ] 4.2 Add the daily-run loop (batch = ceil(len(Follow.ListAll)/7), age 7 days, stop after 3 consecutive failures or on shutdown, final summary log), with the batch computation in a testable function. Verify unit tests for "Batch size" (133 followed → 19), "Nobody followed" and "Consecutive failures" pass.

## 5. Job wiring and build (backend)

- [ ] 5.1 Add `cmd/job/official-site-refresh/main.go` and `di.InitializeOfficialSiteRefreshJobApp`: database, `ArtistRepository`, `FollowRepository`, MusicBrainz client, telemetry and shutdown phases. Verify `go build ./cmd/job/official-site-refresh` succeeds and a local run against docker-compose Postgres logs the summary.
- [ ] 5.2 Add the `official-site-refresh` Dockerfile target and the `deploy.yml` matrix entry. Verify `docker build --target official-site-refresh .` succeeds.
- [ ] 5.3 Open the backend PR (OpenSpec-Change `refresh-artist-official-site`), get CI green, merge and release. Verify the release tag exists and the dev image is pushed.

## 6. Deployment (cloud-provisioning)

- [ ] 6.1 Add `k8s/namespaces/backend/base/cronjob/official-site-refresh/`: a CronJob at `0 19 * * *` UTC with `concurrencyPolicy: Forbid`, a kustomization and `configmap.env`. Register it in the base kustomization. Verify `kubectl kustomize` renders the CronJob.
- [ ] 6.2 Add the dev and prod overlay entries: ConfigMap merge, prod image name and pin, and Spot patch coverage. Verify `make lint` passes, including kubeconform and the Spot check.
- [ ] 6.3 Add the image to `bump-prod-pin`, merge the cloud-provisioning PR and wait for ArgoCD to sync. Verify `official-site-refresh-app` exists in prod and is not suspended.

## 7. Rollout verification

- [ ] 7.1 After the first scheduled run, check Cloud Logging. Verify the summary shows 19 attempted and no failures, each create or replace is logged with old and new URL, and there are no MusicBrainz 503 retries at that hour.
- [ ] 7.2 After 7 days, query prod read-only. Verify every followed artist has `official_site_checked_at` within the last 8 days, and ヨルシカ, あいみょん, 04 Limited Sazabys, ILLIT, SPYAIR and 羊文学 store their own-domain URLs.
