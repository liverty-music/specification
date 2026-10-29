## 1. Entity operation (backend, components/entity/artist/list-stale-or-missing-fanart)

- [x] 1.1 Change `listStaleOrMissingFanartQuery` in `internal/infrastructure/database/rdb/artist_repo.go` to return never-checked artists, and checked artists past the age only with `EXISTS (SELECT 1 FROM followed_artists f WHERE f.artist_id = a.id)` (as `listStaleOfficialSiteQuery` does), keeping the never-checked-first order and the limit; update the doc comments of `ListStaleOrMissingFanart` in `internal/entity/artist.go` and `artist_repo.go`; verify one contract test per scenario in `TestArtistRepository_ListStaleOrMissingFanart` (`artist_repo_test.go`), annotated `// @spec components/entity/artist/list-stale-or-missing-fanart "<scenario>"`, passes against the test database: "Never-checked and stale artists", "Never-checked artist nobody follows", "Stale artist nobody follows", "Artist followed by several fans", "Recently checked artist without images", "More due artists than the limit", "Nothing due"

## 2. Story (stories/discover-artists)

- [x] 2.1 Add `internal/infrastructure/database/rdb/discover_artists_story_test.go`, in the style of `publish_concert_story_test.go`: the real `ArtistUseCase`, `FollowUseCase` and `ArtistImageSyncUseCase` over the real repositories and local Postgres, with a fake image catalog that counts lookups. Run the daily image run's steps as `cmd/job/artist-image-sync` runs them (`ListStaleOrMissingFanart` with 7 days and 500, then `SyncArtistImage` for each artist), set check times through `UpdateFanart`, and annotate `// @spec stories/discover-artists "<scenario>"` for "Stale images", "Artist nobody follows", "Artist followed later" and "Artist registered directly"; verify it passes and `make check` is clean

## 3. Production check (read-only, after the backend release is rolled out)

- [x] 3.1 After the next `artist-image-sync` run (daily 19:00 JST), read its `artist image sync job complete` log line with `gcloud --configuration=liverty-music logging read` and confirm `artists_attempted` is below 500 with `failures` 0, and that it matches a read-only prod query (cloud-provisioning `docs/runbooks/cloud-sql-access.md`) of never-checked artists plus followed artists last checked more than 7 days before the run

## 4. Archive (specification, edited in the main specs when the change is archived)

- [x] 4.1 Change the Purpose of `components/entity/artist/list-stale-or-missing-fanart` to "Returns the artists whose images are due for a check: never checked, or followed by a fan and last checked longer ago than a given age."; verify `openspec validate --specs` passes
- [x] 4.2 Change the Purpose of `components/usecase/artist/sync-artist-image` so the daily run is for artists whose images were never checked and for followed artists last checked more than 7 days ago; verify `openspec validate --specs` passes
