## Why

When a user follows an artist, no official site URL is stored. The concert discovery job (`SearchNewConcerts`) requires an official site to construct a targeted Gemini prompt, so any artist without a site record is silently skipped or errors out — meaning followed artists never get concert data.

## What Changes

- **New**: After a successful Follow, the backend asynchronously resolves the artist's official site URL from MusicBrainz (`url-rels`) and persists it via `CreateOfficialSite`.
- **New**: A new `OfficialSiteResolver` interface is introduced in the entity layer, implemented by the MusicBrainz client, responsible for resolving an official site URL from an MBID.
- **Modified**: `ConcertSearcher.Search()` accepts `officialSite *entity.OfficialSite` as nil-safe; when nil, the Gemini prompt instructs the model to find the official site itself rather than referencing a known URL.
- **Modified**: `ConcertUseCase.SearchNewConcerts()` no longer hard-fails on `GetOfficialSite` NotFound — it continues with `site = nil`.

## Capabilities

### New Capabilities

- `official-site-search`: Automatic resolution and persistence of an artist's official site URL, triggered asynchronously on Follow, using MusicBrainz url-rels with source-credit-based selection.

### Modified Capabilities

- `concert-service`: `SearchNewConcerts` no longer requires an official site to proceed; nil site is forwarded to the searcher as a degraded-but-functional path.
- `artist-following`: Follow side-effect now triggers async official site resolution.

## Impact

- **Backend**: `entity`, `usecase`, `infrastructure/music/musicbrainz`, `infrastructure/gcp/gemini`
- **No API/proto changes**: All changes are internal to the backend service.
- **MusicBrainz rate limit**: The async goroutine respects the existing 1 req/sec throttler.
- **Gemini prompt**: Prompt template gains a second variant (no-URL path), affecting search quality for artists without a resolved site.
