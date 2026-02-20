## Why

`ListTop` and `ListSimilar` RPCs return `Artist` entities sourced from Last.fm, but these artists are never persisted to the local database. This means the returned `Artist.id` is empty, violating the proto contract (`required` field), and making it impossible for the frontend to call `Follow(artist_id)` or any other RPC that requires a valid artist ID. As a result, the entire follow → concert search pipeline is broken: no artist in DB → no follow → onboarding always redirects to discover → no concert notifications.

## What Changes

- `ListTop` and `ListSimilar` backend use cases will auto-persist external artists to the local database (get-or-create by MBID), ensuring every returned `Artist` has a valid `id`.
- `ArtistRepository.Create` will be extended to accept a slice of artists (bulk insert), mirroring the existing `ConcertRepository.Create` pattern.
- The bulk insert implementation for both `ArtistRepository` and `ConcertRepository` will adopt the PostgreSQL `unnest` pattern, replacing manual placeholder construction and eliminating the 65,535 parameter limit.
- The `Create` RPC handler bug (ignoring `mbid` field from request) will be fixed.
- Frontend `artist-discovery-service.ts` will wire up the `ArtistService.Follow` RPC call using the artist IDs now returned by `ListTop`/`ListSimilar`.

## Capabilities

### New Capabilities

- `artist-auto-persist`: Automatic persistence of externally-discovered artists during ListTop/ListSimilar, ensuring proto contract compliance and enabling downstream follow/concert-search flows.
- `bulk-insert-unnest`: PostgreSQL unnest-based bulk insert pattern for artist and concert repositories, replacing manual placeholder construction.

### Modified Capabilities

- `artist-service-infrastructure`: ListTop/ListSimilar will now persist artists to the local DB before returning results (get-or-create by MBID).
- `artist-following`: Follow flow will be wired end-to-end from frontend bubble tap to backend persistence.
- `concert-service`: ConcertRepository.Create will be refactored from manual placeholder bulk insert to unnest pattern.
- `artist-discovery-dna-orb-ui`: Frontend will call ArtistService.Follow RPC on bubble tap using valid artist IDs.

## Impact

- **Backend (ArtistService)**: ListTop/ListSimilar use cases gain DB write path; Create handler fix for MBID; new bulk Create repository method.
- **Backend (ConcertService)**: ConcertRepository.Create refactored to unnest pattern (behavioral equivalent, no API change).
- **Frontend**: `artist-discovery-service.ts` gains Follow RPC integration.
- **Proto**: No proto schema changes required (existing RPCs and messages are sufficient).
- **Database**: No schema migration needed (existing tables and columns support all changes).
