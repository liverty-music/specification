## 1. backend: entity, schema and operations (components/entity/artist, list-by-name-keys, update-name-keys, create, update-mbid, get-artist; design D1 to D3)

- [ ] 1.1 Add the name key function and `NameKeys` to `entity.Artist`; verify one unit test per scenario of the `components/entity/artist` requirement "An artist is found by its name keys"
- [ ] 1.2 Add `artists.name_keys TEXT[] NOT NULL DEFAULT '{}'` with a `COMMENT ON COLUMN` and the GIN index to `schema.sql`, generate the Atlas migration and add the backfill of design D2; verify the migration test applies it to a copy with rows (a full-width, mixed-case name gets its key) and `make lint-schema` passes
- [ ] 1.3 Add `ListByNameKeys` and `UpdateNameKeys` to the artist repository, and make `Create` and `UpdateMBID` store the keys; verify one contract test per scenario of `components/entity/artist/list-by-name-keys`, `update-name-keys`, and the ADDED requirements of `create` and `update-mbid`
- [ ] 1.4 Make the MusicBrainz `GetArtist` ask `inc=aliases` and return the name keys; verify one contract test per scenario of the ADDED requirement of `components/entity/artist/get-artist` against recorded MusicBrainz responses

## 2. backend: usecases (design D3, D4)

- [ ] 2.1 Pass the keys in VerifyMBID, CorrectMBID, Create and Search, and call `UpdateNameKeys` in Refresh; verify one unit test per scenario of the ADDED requirements of `components/usecase/artist/verify-mbid`, `correct-mbid`, `create`, `search` and `refresh`
- [ ] 2.2 Match results without an MBID in ListSimilar and log the counts; verify one unit test per scenario of the MODIFIED and ADDED requirements of `components/usecase/artist/list-similar`

## 3. backend: release and production check

- [ ] 3.1 Open the backend PR citing the change, merge it, cut the release, and verify read-only in prod: AtlasMigration `Ready`, the rollout finished, and one `ListSimilar` for sumika logging the match counts
- [ ] 3.2 After the rollout, add the migration that repeats the backfill for rows with empty `name_keys` (design Migration Plan step 3), merge it, and verify read-only in prod: AtlasMigration `Ready` and no artist with empty `name_keys`
- [ ] 3.3 File an issue in liverty-music/backend to decide stage 2 from the logged counts 30 days after the release, with the 3.1 numbers as its baseline

## 4. story check (stories/discover-artists)

- [ ] 4.1 Verify the scenarios of the ADDED requirement of `stories/discover-artists` in production after 3.1 (an artist whose alias has been read, listed without an MBID, appears in the similar artists; an unregistered name adds nothing) and record each as `@spec-manual stories/discover-artists "<scenario>" -- <how and when it was verified>` in design.md
