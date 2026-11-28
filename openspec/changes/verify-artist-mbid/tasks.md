## 1. specification: proto (design D6)

- [ ] 1.1 Add `entity.v1.CatalogArtist` (mbid, name, country, begin, end, disambiguation, official_site_url, wrapper types with protovalidate per the attribute table of `components/entity/catalog-artist`) and `entity.v1.ArtistMbidStatus` (UNSPECIFIED, UNVERIFIED, VERIFIED, AMBIGUOUS); move `Create` from `rpc.artist.v1.ArtistService` to `rpc.admin.artist.v1.ArtistService` (label `buf skip breaking`), add `ListByMbidStatus` and `CorrectMbid` to the admin service, and a new `rpc.admin.catalog_artist.v1.CatalogArtistService` with `ListByArtist`, with their request and response messages and error comments; verify `buf lint`, `buf format` and the breaking check pass in the proto PR
- [ ] 1.2 Merge the proto PR, cut the specification release, and verify the BSR generation run (`buf-release.yml`) succeeds

## 2. backend: schema and entity (components/entity/artist, components/entity/catalog-artist; design D1, D2)

- [ ] 2.1 In `schema.sql` add `artists.listening_mbid TEXT NOT NULL` with a unique index and `artists.mbid_status TEXT NOT NULL DEFAULT 'unverified'` with its CHECK, each with a `COMMENT ON COLUMN`, and drop `other_mbids`; generate the Atlas migration and add to it the backfill `listening_mbid = mbid`, `mbid_status = 'verified'` for the existing test artists by id (design Migration Plan step 2; list read-only from prod the artists whose MBID MusicBrainz answers 404 for, ask the owner which of them are test artists, and put only the confirmed ones in the migration; record the list and the owner's answer in the task report), and Penthouse's `listening_mbid` (design Migration Plan step 2, after a read-only prod check that no row holds `c94eaf81-baae-465d-8197-9951c2ef52cd`); verify the migration test applies it on a copy with rows and `make lint-schema` passes
- [ ] 2.2 Add `ListeningMBID` and `MBIDStatus` to `entity.Artist` (removing `OtherMBIDs`) and the `entity.CatalogArtist` type with its validation, and the "offered to fans" check; verify one unit test per scenario of `components/entity/artist` ("A new artist starts without images", "One MBID names one artist", "Only a verified artist whose activity has not ended is offered") and `components/entity/catalog-artist`

## 3. backend: entity operations (design D1, D3)

- [ ] 3.1 Change `ArtistRepository.Create` and `ListByMBIDs` to match `mbid` or `listening_mbid` and store the given listening MBID and status, under the advisory lock of D1; verify one contract test per scenario of `components/entity/artist/create` and `list-by-mbids`
- [ ] 3.2 Change `ArtistRepository.UpdateMBID` to keep `listening_mbid` and set Verified, and add `MarkMBIDAmbiguous` and `ListByMBIDStatus`; verify one contract test per scenario of `components/entity/artist/update-mbid`, `mark-mbid-ambiguous` and `list-by-mbid-status`, including the test that runs `UpdateMBID` and `Create` at the same time
- [ ] 3.3 Make the Last.fm client ask `artist.getsimilar` with the artist's `listening_mbid`; verify one contract test per scenario of `components/entity/artist/list-similar` against a stubbed Last.fm server
- [ ] 3.4 Add `ListNamesakes` to the MusicBrainz client (artist search by exact name, case-insensitive filter, country, life span and disambiguation), through the existing throttle and retry; verify one contract test per scenario of `components/entity/artist/list-namesakes` against recorded MusicBrainz responses

## 4. backend: usecases and triggers (design D2 to D5)

- [ ] 4.1 Implement `ArtistUseCase.VerifyMBID` with the decision of D3 and its ERROR log; verify one unit test per scenario of `components/usecase/artist/verify-mbid` with the operations mocked
- [ ] 4.2 Run `VerifyMBID` instead of `Refresh` in the `refresh-artist` consumer, and make the `artist-refresh` job verify every Unverified artist before its slot of `Refresh`; verify the consumer test (announced artist, ambiguous result returns success) and the job test (Unverified first, stop after 3 consecutive failures), covering the trigger scenarios of `components/usecase/artist/verify-mbid` and the REMOVED requirement of `components/usecase/artist/refresh`
- [ ] 4.3 Change `ArtistUseCase.Search` to decide the MBID of each new match before `Create`, and `Search`, `ListTop` and `ListSimilar` to return only artists offered to fans, also on a cache hit (the cache keeps the result before the filter); verify one unit test per scenario of `components/usecase/artist/search`, `list-top` and `list-similar` with the operations mocked
- [ ] 4.4 Change `ArtistUseCase.CorrectMBID` to store the catalog's details with one `UpdateMBID` and `ArtistUseCase.Create` to register Verified with the looked-up activity status, and add `ArtistUseCase.ListByMBIDStatus` and `CatalogArtistUseCase.ListByArtist`; verify one unit test per scenario of `components/usecase/artist/correct-mbid`, `create`, `list-by-mbid-status` and `components/usecase/catalog-artist/list-by-artist`

## 5. backend: admin RPC, removals and documentation (design D6, D7; after 1.2)

- [ ] 5.1 Upgrade the generated package, remove `Create` from the fan artist handler, and add the admin `ArtistService.Create`, `ArtistService.ListByMbidStatus`, `ArtistService.CorrectMbid` and `CatalogArtistService.ListByArtist` handlers with their mappers, registered in the admin list of `internal/di/provider.go`; verify one handler test per scenario of `components/adapter/admin/api/rpc/artist` (ADDED requirements), `components/adapter/admin/api/rpc/catalog-artist` and `components/adapter/fan/api/rpc/artist`
- [ ] 5.2 Remove the `worker artist correct-mbid` command, its DI and tests; verify `make check` passes and `worker artist` no longer lists it
- [ ] 5.3 Rewrite the Last.fm client doc comment from the current Terms of Service and API intro page as design D7 states, keeping `rateLimitInterval` at 200 ms; verify the comment cites https://www.last.fm/api/tos clauses 2.3, 3.1, 4.3 and 4.4 and liverty-music/backend#953

## 6. backend: release

- [ ] 6.1 Open the backend PR citing the change, merge it, cut the release, and verify read-only in prod: AtlasMigration `Ready` with the new columns and `other_mbids` gone, Penthouse's `listening_mbid` set, every artist Unverified except the test artists listed in 2.1 (Verified), and the rollout of every backend workload finished

## 7. frontend: admin console Artist MBIDs screen and test-artist Create (components/infrastructure/admin/web/route/artist-mbids; right after 6.1)

- [ ] 7.1 Switch the admin artist client's `create` to the admin `ArtistService.Create` (verify the existing organizers route test for `Create test artist` passes), and add the `admin/artist-mbids/` route, its navigation entry and the admin artist client methods, reading every value from the RPC fields design D6 names; verify one vitest route test per scenario of `components/infrastructure/admin/web/route/artist-mbids` with the clients mocked
- [ ] 7.2 Merge and release the admin console, then run the screen in the deployed admin console with Playwright: open `Artist MBIDs`, select an Ambiguous artist, check its namesakes and the `Current` label, and cancel a `Choose` with Escape (no write)

## 8. production check and corrections

- [ ] 8.1 Start the `artist-refresh` job by hand and watch it until no artist is Unverified, reading its log for stops; then list the Ambiguous artists read-only and record their count and names in the task report
- [ ] 8.2 Measure `Search` for three names never searched before (Fan API logs or a timed request): if a first search exceeds 15 seconds, apply the fallback of design "Risks" (verify only the first matches, register the rest Unverified) in a follow-up commit of this change; record the timings in the task report
- [ ] 8.3 Check read-only in prod that `ListSimilar` for sumika returns similar artists, and that `ListTop` for Japan, a name search for sumika and one for Penthouse return only Verified artists whose activity has not ended
- [ ] 8.4 The owner chooses the right MBID for each Ambiguous artist on the screen (production writes the owner makes, including any of Ado, Aimer, Yama, Sumika, Saji and Penthouse still Ambiguous); then verify read-only for each: Verified, the chosen `mbid`, `listening_mbid` unchanged, and the next search for its name registers nothing

## 9. cloud-provisioning: runbook removal (design D7)

- [ ] 9.1 Remove `docs/runbooks/correct-artist-mbid.md` and every link to it; open the PR citing the change and merge it (documentation only)

## 10. story check (stories/discover-artists)

- [ ] 10.1 Verify the scenarios of `stories/discover-artists` in production after 8.1 and 8.4 (a first search of a new name, a chart artist appearing on a later call, an ended artist absent from search, an Ambiguous artist on the screen and returned after the choice), and record each as `@spec-manual stories/discover-artists "<scenario>" -- <how and when it was verified>` in design.md, since no E2E suite reaches the music catalog
