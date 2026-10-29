## 1. Entity operation (backend, components/entity/artist/list-stale-or-missing-fanart)

- [ ] 1.1 Change `listStaleOrMissingFanartQuery` in `internal/infrastructure/database/rdb/artist_repo.go` so a checked artist is returned only when it has a row in `followed_artists` or `concert_artists` (`EXISTS`, so an artist is returned once), keeping the never-checked-first order and the limit, and update the doc comments of `ListStaleOrMissingFanart` in `internal/entity/artist.go` and `artist_repo.go`; verify one contract test per scenario in `TestArtistRepository_ListStaleOrMissingFanart` (`artist_repo_test.go`), annotated `// @spec components/entity/artist/list-stale-or-missing-fanart "<scenario>"`, passes against the test database: "Never-checked and stale artists", "Never-checked artist nobody follows", "Stale artist nobody follows", "Stale artist with a concert", "Artist followed by several fans", "Recently checked artist without images", "More due artists than the limit", "Nothing due"

## 2. Story (stories/discover-artists)

- [ ] 2.1 Add a database test that registers artists, follows and concerts through their repositories and reads `ListStaleOrMissingFanart` with the daily run's age (7 days) and limit (500), annotated `// @spec stories/discover-artists "<scenario>"` for "Stale images", "Artist nobody follows", "Artist followed later" and "Artist registered directly"; verify it passes and `make check` is clean

## 3. Production check (read-only, after the backend release is rolled out)

- [ ] 3.1 After the next `artist-image-sync` run (daily 19:00 JST), read its `artist image sync job complete` log line with `gcloud --configuration=liverty-music logging read` and confirm `artists_attempted` is below 500 with `failures` 0, and that the count matches a read-only prod query (cloud-provisioning `docs/runbooks/cloud-sql-access.md`) of followed or performing artists last checked more than 7 days ago plus never-checked artists
