## Context

`ListTop` and `ListSimilar` RPCs fetch artist data from Last.fm and return `entity.Artist` structs. These structs have `Name` and `MBID` populated but `ID` is empty because the artists are never persisted to the local database. The proto `Artist` message requires `id`, so every response violates the wire contract. Downstream RPCs (`Follow`, `ListSimilar`, `CreateOfficialSite`) require a valid `artist_id` referencing a DB row, making the entire follow pipeline non-functional.

Current repository stack: Go 1.25, pgx v5.8.0, PostgreSQL with UUIDv7 PKs. The existing `ConcertRepository.Create` uses manual `fmt.Sprintf` placeholder construction with a 500-row batch limit to stay within PostgreSQL's 65,535 parameter ceiling.

## Goals / Non-Goals

**Goals:**
- Every `Artist` returned by `ListTop`/`ListSimilar` SHALL have a valid database-backed `id`
- `ArtistRepository.Create` SHALL be extended to variadic (`Create(ctx, artists ...*Artist)`) for bulk support, consistent with `ConcertRepository.Create`
- Both artist and concert bulk inserts SHALL use the PostgreSQL `unnest` pattern
- The `Create` RPC handler SHALL correctly pass `mbid` to the use case
- Frontend `followArtist()` SHALL call `ArtistService.Follow` RPC

**Non-Goals:**
- OfficialSite auto-population (deferred; requires separate Last.fm/MusicBrainz URL enrichment)
- `DeleteOfficialSite` implementation (existing TODO, separate concern)
- Proto schema changes (existing messages and RPCs are sufficient)
- Database schema migrations (existing columns support all changes)

## Decisions

### Decision 1: Auto-persist in UseCase layer (ListTop/ListSimilar)

**Choice**: `ListTop` and `ListSimilar` use cases will get-or-create each external artist before returning results.

**Rationale**: The proto contract requires `Artist.id` to be present. The use case layer is the correct place for this orchestration because:
- The RPC handler should not contain persistence logic
- The repository layer should not call external APIs
- The use case already has access to both `ArtistRepository` and `ArtistSearcher`

**Flow**:
```
UseCase.ListTop(country)
  1. artistSearcher.ListTop(country)  → []*Artist (no ID, has MBID)
  2. artistRepo.Create(artists...)    → upsert by MBID, returns []*Artist (with ID)
  3. return persisted artists
```

**Alternative considered**: Persist in the RPC handler — rejected because it violates layered architecture (handler should only map proto ↔ entity).

**Alternative considered**: Persist in `ArtistSearcher` adapter — rejected because the searcher is a read-only external API client and should not have DB access.

### Decision 2: PostgreSQL `unnest` for bulk inserts

**Choice**: Replace manual placeholder construction with `unnest` array pattern.

**Rationale**:
- Eliminates `fmt.Sprintf("($%d, $%d, ...)", offset+1, ...)` offset arithmetic entirely
- Parameter count is always fixed (one `$N` per column, regardless of row count) — removes the 65,535 limit
- Removes the `maxConcertsPerBatch` batching loop
- Single SQL statement, single round trip
- pgx v5 natively serializes Go slices to PostgreSQL arrays
- Fully supports `ON CONFLICT DO NOTHING`

**SQL pattern**:
```sql
INSERT INTO artists (id, name, mbid, created_at)
SELECT * FROM unnest($1::uuid[], $2::text[], $3::varchar[], $4::timestamptz[])
ON CONFLICT (mbid) DO NOTHING
```

**Alternative considered**: `pgx.Batch` + `SendBatch` — sends N individual INSERT statements in one round trip. Simpler refactor but still N statements. `unnest` is a single statement which is more efficient for the typical 30-row ListTop result.

**Alternative considered**: `CopyFrom` + staging table — maximum throughput but cannot use `ON CONFLICT` directly, requires temp table management. Over-engineered for our batch sizes (≤50 rows).

### Decision 3: Extend `Create` to variadic with return value

**Choice**: Change `ArtistRepository.Create` signature from `Create(ctx, artist *Artist) error` to `Create(ctx, artists ...*Artist) ([]*Artist, error)`, consistent with the existing `ConcertRepository.Create(ctx, concerts ...*Concert) error` pattern. The artist version returns the persisted slice because callers need the database-assigned IDs.

**Implementation**: `INSERT ... ON CONFLICT (mbid) DO NOTHING` via `unnest`, followed by `SELECT WHERE mbid = ANY($1)` to return all artists (both newly inserted and pre-existing) with valid IDs.

**Rationale**: `ListTop` returns ~30 artists. Some may already exist in the DB. We need all of them with valid IDs. Using `ON CONFLICT DO NOTHING` + `SELECT WHERE mbid = ANY($1)` ensures idempotency without requiring individual `GetByMBID` calls per artist.

**Alternative considered**: Adding a separate `CreateBulk` method — rejected to maintain naming consistency with `ConcertRepository.Create`.

### Decision 4: `ON CONFLICT (mbid)` for artist deduplication

**Choice**: Use MBID as the deduplication key for artist upserts.

**Rationale**: MusicBrainz ID is the canonical cross-system identifier. Two Last.fm results with the same MBID represent the same artist. A UNIQUE index on `mbid` is required (currently missing — needs to be added).

**Note**: Some Last.fm artists may have empty MBIDs. These will be inserted as new rows each time (no conflict). This is acceptable as a temporary state; MBID enrichment can be added later.

### Decision 5: Fix Create handler to pass MBID

**Choice**: Update `artist_handler.go` Create method to read `req.Msg.Mbid` and set it on the entity.

**Rationale**: The proto `CreateRequest` already has an `mbid` field. The use case already has MBID normalization logic via `ArtistIdentityManager`. The handler simply drops the field — a bug, not a design choice.

### Decision 6: Frontend Follow wiring

**Choice**: In `followArtist()`, call `this.artistClient.follow({ artistId: new ArtistId({ value: artist.id }) })` after local state update.

**Rationale**: With ListTop now returning valid IDs, the frontend has everything needed. The call is fire-and-forget from UX perspective (local state updates immediately, backend call is best-effort with error logging).

## Risks / Trade-offs

- **[Last.fm data retention policy]** → Storing `name` + `mbid` is metadata-level caching, not creating a substitute database. Only identifiers are stored, not Last.fm-specific data (play counts, images, bios). Mitigation: no Last.fm-proprietary fields are persisted.

- **[Empty MBID artists]** → Some Last.fm results lack MBIDs, causing duplicate rows on repeated ListTop calls. → Mitigation: acceptable for MVP; can add name-based deduplication or MBID enrichment via MusicBrainz API later.

- **[ListTop latency increase]** → Adding DB writes to ListTop adds latency. → Mitigation: `unnest` bulk insert is a single statement (~2-5ms for 30 rows). Cache (already in place) means DB writes happen only on cache miss (first call per country per TTL period).

- **[UNIQUE index migration needed]** → `mbid` column needs a UNIQUE index for `ON CONFLICT (mbid)`. Current index is non-unique. → Mitigation: `CREATE UNIQUE INDEX CONCURRENTLY` is non-blocking and safe for production.
