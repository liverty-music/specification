# Tasks

## 1. backend: Entity and schema (components/entity/artist)

- [ ] 1.1 Add `activity_ended BOOLEAN NOT NULL DEFAULT false` with its `COMMENT ON COLUMN` to `artists` in `schema.sql`, generate the Atlas migration with `atlas migrate diff` and add it to the Atlas kustomization (`db-migration-workflow` skill); verify `make lint-schema` and `atlas migrate apply --env local` pass
- [ ] 1.2 Add `ActivityEnded` to `entity.Artist`, read it in the artist row scan, and verify the unit test for the scenarios "New artist" and "Two new artists" of "A new artist starts without images" passes

## 2. backend: Entity operations

- [ ] 2.1 `components/entity/artist/get-artist`: decode `life-span.ended` in the MusicBrainz `GetArtist` (design Decision 5) and verify one contract test per scenario passes ("Known MBID", "Ended activity", "Ended activity without an end date", "Activity not ended", "Unknown MBID", "Catalog unreachable")
- [ ] 2.2 `components/entity/artist/update-activity-ended`: declare `UpdateActivityEnded` on `ArtistRepository`, implement it in the rdb repository, and verify one contract test per scenario passes ("Activity ended", "Activity resumed in the catalog", "Same value", "Unknown artist")
- [ ] 2.3 `components/entity/artist/list-activity-check-due`: declare `ListActivityCheckDue` on `ArtistRepository`, implement it with the UUID-byte slot and `uuid_extract_timestamp` (design Decisions 2 and 3), and verify one contract test per scenario passes ("Same slot on every call", "Every artist in one slot", "Recently registered artist in another slot", "Recently registered artist in the given slot", "No artists")
- [ ] 2.4 Regenerate the repository and identity-manager mocks; verify `make check` passes

## 3. backend: Usecases

- [ ] 3.1 `components/usecase/artist/list-top`: re-read the result with `ListByMBIDs` and drop artists with `ActivityEnded` on every call, cached or not (design Decision 4); verify one unit test per scenario passes ("Chart lists an ended artist", "Artist marked ended after the result was reused", "Chart artist registered by this call") and the existing ListTop tests still pass
- [ ] 3.2 `components/usecase/artist/list-similar`: the same filter before the limit cut; verify one unit test per scenario of both the modified and the added requirement passes ("Known and new similar artists", "Result without MBID", "Limit given", "Limit of zero", "No similar artists", "Ended artist within the limit", "Artist marked ended after the result was reused", "Seed artist whose activity has ended")
- [ ] 3.3 `components/usecase/artist/refresh-activity`: add `ArtistActivityRefreshUseCase` with `RefreshActivity` and `RefreshDueActivity` (slot from the Asia/Tokyo date, since = start - 25h, stop after 3 consecutive failures or on shutdown, one summary log line); verify one unit test per scenario passes with the operations mocked ("Catalog marks the activity as ended", "Catalog no longer marks the activity as ended", "MBID unknown to the catalog", "Catalog unreachable", "Artist gone", "Run picks today's slot", "Every artist within 30 days", "Newly registered artist", "Consecutive failures")

## 4. backend: Job binary

- [ ] 4.1 Add `cmd/job/artist-activity-refresh` mirroring `cmd/job/official-site-refresh` (DI wiring, exit non-zero on a circuit break) and its `docker-bake.hcl` target; verify `docker buildx bake artist-activity-refresh` builds and `make check` passes

## 5. backend: Story (stories/discover-artists)

- [ ] 5.1 Extend the discover-artists story test with the scenarios "Dissolved group in the chart", "Name search for a dissolved group", "Group dissolves after it was registered" and "Ended artist found for the first time" (catalogs faked, database real); verify it passes

## 6. cloud-provisioning: CronJob

- [ ] 6.1 Add `k8s/namespaces/backend/base/cronjob/artist-activity-refresh/` (CronJob at `0 20 * * *`, ConfigMap, kustomization) mirroring `official-site-refresh`, wire it into the base and both overlays, add the prod image override, and add `artist-activity-refresh` to the image list in `.github/workflows/bump-prod-pin.yml`; verify `kustomize build` succeeds for the dev and prod overlays and shows the CronJob with the prod image

## 7. Production verification (read-only)

- [ ] 7.1 After the backend and cloud-provisioning PRs merge and the prod pin is bumped: confirm the AtlasMigration status reports the new version, and that the first scheduled run's log shows its slot, the listed and attempted counts and no circuit break
