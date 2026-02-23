## Context

The dashboard currently fetches concerts by calling `ConcertService.List(artist_id)` once per followed artist (N+1 pattern). The authenticated user's identity is already available in RPC context via JWT claims, and the `followed_artists` table links users to artists. The `ArtistService.ListFollowed` handler demonstrates the established pattern for user-scoped queries.

## Goals / Non-Goals

**Goals:**
- Reduce dashboard concert loading from N+1 RPC calls to 1
- Follow established auth-context patterns (`auth.GetUserID`)
- Keep the existing `List` RPC unchanged

**Non-Goals:**
- Adding `passion_level` to the response (future enhancement)
- Pagination or cursor-based fetching
- Caching or materialized views

## Decisions

### Decision 1: `ListByFollower` RPC on ConcertService

Add a new RPC rather than extending the existing `List` RPC.

- **Rationale**: `List` filters by a single artist — a fundamentally different query shape than "all concerts for a user's followed artists." Mixing both into one RPC adds conditional logic and unclear validation rules.
- **Alternative considered**: `ListByArtists(repeated artist_ids)` — still requires 2 RPC calls (ListFollowed + ListByArtists) and leaks orchestration to the frontend.

### Decision 2: Empty request message, auth from context

`ListByFollowerRequest` has no fields. The user identity comes from the JWT claims in the RPC context, following the same pattern as `ArtistService.ListFollowed`.

- **Rationale**: Consistent with existing patterns. Prevents one user from querying another user's followed concerts.

### Decision 3: Single SQL JOIN query

The repository method joins `concerts`, `events`, `venues`, and `followed_artists` in one query filtered by `user_id`.

```sql
SELECT c.event_id, c.artist_id, e.venue_id, e.title, e.listed_venue_name,
       e.local_event_date, e.start_at, e.open_at, e.source_url,
       v.id, v.name, v.admin_area
FROM concerts c
JOIN events e ON c.event_id = e.id
JOIN venues v ON e.venue_id = v.id
JOIN followed_artists fa ON c.artist_id = fa.artist_id
WHERE fa.user_id = $1
ORDER BY e.local_event_date ASC
```

- **Rationale**: `followed_artists` has an index on `user_id`. The query reuses the same column set as `listConcertsByArtistQuery`, so existing row-scanning logic applies.

### Decision 4: Flat response with `repeated Concert`

The response is `repeated entity.v1.Concert` — no grouping by artist.

- **Rationale**: Each `Concert` already contains `artist_id`. The frontend can group client-side if needed. A `map<string, ArtistConcerts>` structure adds proto complexity with no benefit.

### Decision 5: Backend resolves external_id → internal UUID

The handler calls `auth.GetUserID(ctx)` to get the Zitadel external ID, then `resolveUserID` maps it to the internal UUID for the SQL query. This follows the `ListFollowed` pattern.

- **Rationale**: Concert usecase needs a `userRepo` dependency to resolve the user. Since `artistUseCase` already does this, the concert usecase can follow the same pattern.

## Risks / Trade-offs

- **[Cross-domain JOIN]** ConcertService queries `followed_artists`, which is conceptually in the artist/follow domain. → Acceptable in a monolithic DB; revisit only if services split.
- **[Large result sets]** A user following many artists with many concerts could return a large payload. → Mitigated by the practical upper bound of followed artists. Pagination can be added later if needed.
- **[New dependency]** Concert usecase gains a `userRepo` dependency for `resolveUserID`. → Minimal coupling; single method interface.
