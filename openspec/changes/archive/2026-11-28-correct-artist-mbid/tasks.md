## 1. backend: schema and entity (components/entity/artist, design D1)

- [x] 1.1 Add `artists.other_mbids TEXT[] NOT NULL DEFAULT '{}'` with a `COMMENT ON COLUMN` to `schema.sql`, generate the Atlas migration, and add `OtherMBIDs` to `entity.Artist` and `scanArtist`; verify the migration test applies it and `make lint-schema` passes

## 2. backend: entity operations (components/entity/artist/update-mbid, list-by-mbids, create; design D2, D3)

- [x] 2.1 Make `ListByMBIDs` find an artist under its MBID or an other MBID, once per artist in the order of the first matching MBID; verify one contract test per scenario of `components/entity/artist/list-by-mbids`
- [x] 2.2 Make `Create` skip an MBID that is among another artist's other MBIDs and return that artist for it, under the advisory lock of D3; verify one contract test per scenario of `components/entity/artist/create`
- [x] 2.3 Declare and implement `ArtistRepository.UpdateMBID` as in design D3 (advisory lock, row lock, uniqueness check, replace, clear, delete the official site); verify one contract test per scenario of `components/entity/artist/update-mbid` and of the `components/entity/artist` requirement "One MBID names one artist", including a test that runs `UpdateMBID` and `Create` at the same time

## 3. backend: usecases (components/usecase/artist/correct-mbid, search; design D2, D4)

- [x] 3.1 Resolve a match under an other MBID in `persistArtists` and list an artist once; verify one unit test per MODIFIED scenario of `components/usecase/artist/search`, `list-similar` and `list-top` with the operations mocked
- [x] 3.2 Implement `ArtistUseCase.CorrectMBID` as in design D4; verify one unit test per scenario of `components/usecase/artist/correct-mbid` with the operations mocked

## 4. backend: admin command (design D5)

- [x] 4.1 Add `worker artist correct-mbid <artist id> <mbid>` with its DI (artist repository, MusicBrainz client, use case) and usage text; verify a test of the argument parsing and of the output for one corrected artist, and that a typo in the arguments fails before anything connects

## 5. cloud-provisioning: runbook

- [x] 5.1 Write `docs/runbooks/correct-artist-mbid.md`: when to use the command, how to choose the MBID, the `kubectl exec` line, what the output shows, what is cleared and re-read afterwards, and how to check the result read-only; open the PR citing the change and merge it (documentation only)

## 6. backend: release and production check

- [x] 6.1 Open the backend PR citing the change, merge it, cut the release, and verify read-only in prod: AtlasMigration `Ready` with the new column, the rollout finished, and the workflow worker running the new version

## 7. production: audit (design D6, after 6.1 is live)

- [x] 7.1 Read every registered artist's catalog record and the other catalog artists with exactly its name, list the artists with another candidate with country, life span and disambiguation, and give the list to the owner; the list and the owner's decisions are recorded in the report of this task, not in an issue
