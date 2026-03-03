## Context

During onboarding, the Discover page (Step 1) lets guest users follow artists stored in localStorage. The Loading screen (Step 2) skips `SearchNewConcerts` entirely (3-second delay only) because it requires authentication. This means no concert data is written to the database, so the Dashboard (Step 3) displays an empty state.

Separately, `ArtistDiscoveryService.checkLiveEvents()` uses a hash-based mock to simulate whether an artist has upcoming events (~30% return true). The TS Connect-RPC client for `ConcertService/List` is already available and used elsewhere.

The backend already has a `publicProcedures` mechanism in `di/provider.go` that allows specific RPC endpoints to bypass JWT authentication. Four endpoints are already public: `ArtistService/{ListTop,ListSimilar,Search}` and `ConcertService/List`.

## Goals / Non-Goals

**Goals:**
- Populate concert data in the database during onboarding so the Dashboard shows real content.
- Replace the `checkLiveEvents` mock with a real `ConcertService/List` call.
- Keep the change minimal — use existing infrastructure (`publicProcedures`, `searchLog` cache).

**Non-Goals:**
- Changing the onboarding step order (signup remains at Step 6).
- Adding rate limiting or bot protection (searchLog 24h cache is sufficient for now).
- Changing the Loading screen behavior (remains 3-second delay).
- Modifying the `SearchNewConcerts` RPC signature or backend logic.

## Decisions

### D1: Make `SearchNewConcerts` a public procedure

Add `ConcertService/SearchNewConcerts` to the `publicProcedures` map in `di/provider.go`.

**Why this over alternatives:**
- The `publicProcedures` pattern already exists and is proven.
- `SearchNewConcerts` has built-in abuse protection via `searchLog` (24h TTL per artist).
- No proto changes needed, no new endpoints, no breaking changes.

### D2: Fire-and-forget `SearchNewConcerts` on follow during Discover

In `ArtistDiscoveryService.followArtist()`, after the localStorage write and optimistic UI update, call `ConcertServiceClient.searchNewConcerts(artistId)` without awaiting the result. Log errors to console only.

**Why fire-and-forget:**
- The user spends significant time on the Discover page selecting multiple artists. By the time they reach Loading (Step 2) and Dashboard (Step 3), the async event consumers have had enough time to write concert data to the DB.
- Awaiting would slow down the bubble absorption animation and degrade UX.

**Why call from `ArtistDiscoveryService` (not `ArtistServiceClient.follow()`):**
- `ArtistServiceClient.follow()` during onboarding only writes to localStorage — it has no dependency on `IConcertService`. Adding it there would create a circular dependency or require injecting a new service.
- `ArtistDiscoveryService` already has access to both artist and concert concerns and is the right orchestration point.

### D3: Replace `checkLiveEvents` mock with `ConcertService/List`

Change `checkLiveEvents(artistName)` signature to `checkLiveEvents(artistId)` and call `ConcertServiceClient.listConcerts(artistId)`. Return `true` if the result array is non-empty.

**Why change the parameter from `artistName` to `artistId`:**
- `ConcertService/List` requires `artist_id`, not name.
- The callers (`discover-page.ts`, `artist-discovery-page.ts`) already have access to `artist.id` on the `ArtistBubble` object.

## Risks / Trade-offs

- **[Race condition] Concert data may not be ready when Dashboard loads** → Mitigated by the natural delay: users spend time on Discover selecting multiple artists, then 3 seconds on Loading. For the first artist followed, this gives 30+ seconds for the async consumer to process. If some data is still missing, the user will see a partial dashboard (better than empty).
- **[Public API abuse] Unauthenticated `SearchNewConcerts` calls** → Mitigated by `searchLog` 24h TTL: duplicate calls for the same artist are no-ops. Creating new artist IDs requires other RPCs. Accepted risk for current scale.
- **[Breaking test changes] `checkLiveEvents` signature change** → Callers and test mocks need updating from `artistName` to `artistId`. Small scope: 3 call sites, 2 test files, 1 mock helper.
