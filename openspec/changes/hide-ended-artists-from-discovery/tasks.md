# Tasks

## 1. cloud-provisioning: new durable alongside the old one (design Migration Plan step 1)

- [ ] 1.1 Add `k8s/namespaces/nats/base/jetstream/consumer-refresh-artist.yaml` (the spec of `consumer-resolve-artist-name.yaml` with `durableName: refresh-artist`) to the jetstream kustomization, and a `refresh-artist` trigger next to `resolve-artist-name` in `k8s/namespaces/backend/base/event-consumer/scaledobject.yaml`; verify `kustomize build` succeeds for the nats and backend overlays and shows both Consumers and both triggers

## 2. backend: Entity and schema (components/entity/artist)

- [ ] 2.1 Add `activity_ended BOOLEAN NOT NULL DEFAULT false` with its `COMMENT ON COLUMN` to `artists` in `schema.sql`, generate the Atlas migration with `atlas migrate diff` and add it to the Atlas kustomization (`db-migration-workflow` skill); verify `make lint-schema` and `atlas migrate apply --env local` pass
- [ ] 2.2 Add `ActivityEnded` to `entity.Artist`, read it in the artist row scan, and verify the unit test for the scenarios "New artist" and "Two new artists" of "A new artist starts without images" passes

## 3. backend: Entity operations

- [ ] 3.1 `components/entity/artist/get-artist`: decode `life-span.ended` in the MusicBrainz `GetArtist` (design Decision 5) and verify one contract test per scenario passes ("Known MBID", "Ended activity", "Ended activity without an end date", "Activity not ended", "Unknown MBID", "Catalog unreachable")
- [ ] 3.2 `components/entity/artist/update-activity-ended`: declare `UpdateActivityEnded` on `ArtistRepository`, implement it in the rdb repository, and verify one contract test per scenario passes ("Activity ended", "Activity resumed in the catalog", "Same value", "Unknown artist")
- [ ] 3.3 `components/entity/artist/list-refresh-due`: declare `ListRefreshDue` on `ArtistRepository`, implement it with the UUID-byte slot (design Decision 3), and verify one contract test per scenario passes ("Same slot on every call", "Every artist in one slot", "Spread over the slots", "Empty slot")
- [ ] 3.4 `components/entity/follow/list-all`: add `a.activity_ended` to `followListAllQuery` and its scan; verify one contract test per scenario passes ("Artist followed by two fans", "Unfollowed artist", "No follows", "Followed artist whose activity has ended")
- [ ] 3.5 Regenerate the repository and identity-manager mocks; verify `make check` passes

## 4. backend: Artist usecases

- [ ] 4.1 `components/usecase/artist/refresh`: add `Refresh` and `RefreshDue` to `ArtistUseCase` (design Decisions 2, 3 and 7), remove `ArtistNameResolutionUseCase` and its test, point the `ARTIST.created` consumer at `ArtistUseCase.Refresh` and rename its behavior-table row to `refresh-artist` (`internal/di/consumer.go`); verify one unit test per scenario passes with the operations mocked ("Catalog name differs", "Catalog name equal", "Catalog name empty", "Catalog marks the activity as ended", "Catalog no longer marks the activity as ended", "MBID unknown to the catalog", "Catalog unavailable", "Artist gone", "Artist announced", "Run picks today's slot", "Every artist within 30 days", "Consecutive failures"), and that `git grep -n "ResolveCanonicalName\|ArtistNameResolution\|resolve-artist-name"` in backend finds nothing
- [ ] 4.2 `components/usecase/artist/list-top`: filter on `ActivityEnded` from the registration lookup on a cache miss and from one `ListByMBIDs` call on a cache hit (design Decision 4); verify one unit test per scenario of the modified and the added requirements passes ("First call for a country", "Repeated call keeps identities", "Chart artist already registered", "Chart artist without MBID", "Empty chart", "Repeated call", "Result older than 6 hours", "Chart lists an ended artist", "Artist marked ended after the result was reused", "Chart artist registered by this call"), and that each call makes exactly one `ListByMBIDs` call
- [ ] 4.3 `components/usecase/artist/list-similar`: the same filter before the limit cut; verify one unit test per scenario of the modified and the added requirements passes ("Known and new similar artists", "Result without MBID", "Limit given", "Limit of zero", "No similar artists", "Repeated call", "Repeated call with a different limit", "Result older than 6 hours", "Ended artist within the limit", "Artist marked ended after the result was reused", "Seed artist whose activity has ended")

## 5. backend: Search usecases

- [ ] 5.1 `components/usecase/concert/search-new-concerts`: read the artist and skip it when `ActivityEnded` (design Decision 6); verify one unit test per scenario passes ("Ended artist", "Ended artist in the daily run", "Ended artist followed for the first time")
- [ ] 5.2 `components/usecase/ticket-sale/discover-for-artist`: return 0 first when the artist's `ActivityEnded`; verify the unit test for "Ended artist" passes

## 6. backend: Job binary

- [ ] 6.1 Add `cmd/job/artist-refresh` mirroring `cmd/job/official-site-refresh` (DI wiring, exit non-zero on a circuit break) and its `docker-bake.hcl` target; verify `docker buildx bake artist-refresh` builds and `make check` passes

## 7. backend: Story (stories/discover-artists)

- [ ] 7.1 Update the discover-artists story test for the modified requirement ("Newly discovered artist", "Already registered artist") and add the scenarios "Dissolved group in the chart", "Name search for a dissolved group", "Group dissolves after it was registered" and "Ended artist found for the first time" (catalogs faked, database real); verify it passes

## 8. cloud-provisioning: retire the old durable and add the CronJob (design Migration Plan step 3)

- [ ] 8.1 After the backend image with the `refresh-artist` consumer is pinned in prod: remove `consumer-resolve-artist-name.yaml` and its kustomization entry and the `resolve-artist-name` KEDA trigger; add `k8s/namespaces/backend/base/cronjob/artist-refresh/` (CronJob at `0 20 * * *`, ConfigMap, kustomization) mirroring `official-site-refresh`, wire it into the base and both overlays, add the prod image override and `artist-refresh` to the image list in `.github/workflows/bump-prod-pin.yml`; verify `kustomize build` succeeds for the dev and prod overlays and shows the CronJob with the prod image and no `resolve-artist-name`
- [ ] 8.2 Delete the `resolve-artist-name` durable from the prod NATS server by hand (one-time action, `preventDelete: true`); verify `nats consumer ls ARTIST` lists `refresh-artist` and `resolve-artist-image` only

## 9. Production verification (read-only)

- [ ] 9.1 Confirm the AtlasMigration status reports the new version, the event consumer logs show `refresh-artist` handling `ARTIST.created`, and the first scheduled `artist-refresh` run logs its slot, the listed and attempted counts and no circuit break
