## 1. Entity Layer

- [x] 1.1 Add `OfficialSiteResolver` interface to `internal/entity/artist.go` with `ResolveOfficialSiteURL(ctx, mbid string) (string, error)`

## 2. MusicBrainz Client

- [x] 2.1 Add `urlRelsResponse` struct to `internal/infrastructure/music/musicbrainz/client.go` to decode `url-rels` JSON (relations array with `type`, `url.resource`, `source-credit`, `ended`)
- [x] 2.2 Implement `ResolveOfficialSiteURL` on `musicbrainz.client`: call `GET /ws/2/artist/{mbid}?inc=url-rels&fmt=json`, apply priority selection (source-credit match → empty credit → first active), return empty string if none found
- [x] 2.3 Verify `musicbrainz.client` satisfies both `entity.ArtistIdentityManager` and `entity.OfficialSiteResolver` with compile-time checks

## 3. Artist UseCase — Follow Side-Effect

- [x] 3.1 Add `siteResolver entity.OfficialSiteResolver` field to `artistUseCase` struct and update `NewArtistUseCase` constructor signature
- [x] 3.2 Implement `resolveAndPersistOfficialSite` helper on `artistUseCase`: check existing site, call resolver, call `CreateOfficialSite`, log errors at WARN without returning them
- [x] 3.3 Update `Follow()` in `artist_uc.go`: after `artistRepo.Follow()` succeeds, spawn goroutine using `context.WithoutCancel(ctx)` calling `resolveAndPersistOfficialSite`
- [x] 3.4 Update `artist_uc_test.go` to cover the new Follow side-effect scenarios (site already exists, resolver returns empty, resolver errors)

## 4. Gemini Concert Searcher — Nil-Safe Official Site

- [x] 4.1 Change `Search()` signature in `internal/infrastructure/gcp/gemini/searcher.go` to accept `officialSite *entity.OfficialSite` (nil-safe)
- [x] 4.2 Add a second prompt template variant (no-URL path) and apply conditional branching on `officialSite == nil` in `Search()`
- [x] 4.3 Update `entity.ConcertSearcher` interface signature in `internal/entity/concert.go` to match the nil-safe `officialSite` parameter
- [x] 4.4 Update `searcher_test.go` and `searcher_integration_test.go` to cover the nil-site path

## 5. Concert UseCase — Degrade Gracefully on Missing Site

- [x] 5.1 Update `SearchNewConcerts()` in `internal/usecase/concert_uc.go`: change `GetOfficialSite` error handling so `NotFound` continues with `site = nil` instead of returning error
- [x] 5.2 Update `concert_uc_test.go` to cover the no-official-site scenario

## 6. Dependency Injection

- [x] 6.1 Update `internal/di/provider.go`: pass `musicbrainzClient` as `OfficialSiteResolver` to `NewArtistUseCase`
- [x] 6.2 Verify `internal/di/job.go` requires no changes (JobApp does not use `artistUseCase`)
