## Why

The discovery page artist search returns duplicate entries for the same artist. Last.fm's `artist.search` API returns all name variants (e.g. "ヨルシカ", "ヨルシカ Live", "Yorushika(ヨルシカ)", "ヨルシカ - LIVE") as separate results. The backend passes these through without filtering, cluttering the UI with noise and making it hard for users to find and follow the correct artist.

Additionally, `Search()` is inconsistent with `ListSimilar()` and `ListTop()`: it does not persist artists to the database before returning, so the frontend receives ephemeral UUIDs that are regenerated on every call rather than stable database IDs.

## What Changes

- Filter Last.fm search results: drop entries with empty MusicBrainz ID (MBID), then deduplicate by MBID keeping the first occurrence
- Make `Search()` persist artists to the database before returning (consistent with `ListSimilar()` and `ListTop()`)
- Extract a shared `persistArtists` helper in the UseCase layer used by all three methods (`Search`, `ListSimilar`, `ListTop`)
- Add `ListByMBIDs` method to `ArtistRepository` for efficient lookup of existing artists
- The helper uses a read-then-write pattern: `ListByMBIDs` to find existing artists, `Create` only for missing ones, then merge results preserving input order

## Capabilities

### Modified Capabilities
- `artist-discovery`: Search results are deduplicated by MBID and filtered for MusicBrainz-backed entries only. All discovery methods (`Search`, `ListSimilar`, `ListTop`) return artists with stable database UUIDs via a shared persist helper.

## Impact

- **Backend**: Modified files: `usecase/artist_uc.go` (dedup logic, persist helper, refactor 3 methods), `entity/artist.go` (add `ListByMBIDs` to repository interface), `infrastructure/database/rdb/artist_repo.go` (implement `ListByMBIDs`). Mock regeneration required.
- **Frontend**: No changes. The response shape (`[]*Artist`) is unchanged; IDs become stable.
- **Proto (RPC)**: No changes.
- **Database**: No schema migration required. `ListByMBIDs` uses the existing partial unique index on `mbid`.

## Out of Scope

- `artist.created` event publishing and async canonical name resolution via MusicBrainz (planned as a follow-up change)
- Frontend-side deduplication or grouping
