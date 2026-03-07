## Architecture

All changes are in the backend repository. No cross-repo coordination required.

## Data Flow: Search (Before vs After)

### Before

```
lastfm.Search("ヨルシカ")
  → 11 results (duplicates, empty MBIDs)
  → cache as-is
  → return with ephemeral UUIDs (regenerated per call)
```

### After

```
lastfm.Search("ヨルシカ")
  → 11 results
  → filter: drop empty MBID          → 5 remain
  → dedup: keep first per MBID       → 2 remain (ヨルシカ, suis from ヨルシカ)
  → persistArtists(ctx, filtered)
      1. ListByMBIDs(["abc","def"])   → find existing in DB
      2. Create(missing only)         → insert new artists
      3. merge existing + created     → preserve input order
  → cache persisted results
  → return with stable DB UUIDs
```

## Search Dedup Rules

1. **Drop empty MBID**: Entries without a MusicBrainz ID are user-submitted Last.fm pages with no canonical identity. Liverty Music requires MBID for artist identity.
2. **Dedup by MBID**: Keep the first occurrence per MBID. Last.fm returns results by popularity, so the first variant is the most recognized name.
3. **Different MBID = different artist**: Even if names look related (e.g. "suis from ヨルシカ"), a distinct MBID means MusicBrainz recognizes it as a separate entity.

## Shared Helper: `persistArtists`

### Motivation

Three UseCase methods fetch artists from external APIs and need to return them with stable DB UUIDs:

| Method | Currently persists? | After |
|--------|-------------------|-------|
| `Search` | No | Yes, via helper |
| `ListSimilar` | Yes, via `Create(all...)` | Yes, via helper |
| `ListTop` | Yes, via `Create(all...)` | Yes, via helper |

`ListSimilar` and `ListTop` currently call `Create(all...)` which issues INSERT for every artist (relying on ON CONFLICT DO NOTHING). The helper optimizes this by reading first, writing only missing.

### Signature

```go
func (uc *artistUseCase) persistArtists(
    ctx context.Context,
    artists []*entity.Artist,
) ([]*entity.Artist, error)
```

All input artists MUST have non-empty MBID (caller responsibility).

### Algorithm

```
Input: [A(mbid:abc), B(mbid:def), C(mbid:ghi)]

Step 1 — Collect MBIDs
  mbids = ["abc", "def", "ghi"]

Step 2 — Read existing
  existing = artistRepo.ListByMBIDs(ctx, mbids)
  → [{id:uuid-1, name:"ヨルシカ", mbid:"abc"}]
  existingSet = {"abc"}

Step 3 — Determine missing
  missing = [B(mbid:def), C(mbid:ghi)]

Step 4 — Create missing (only if non-empty)
  created = artistRepo.Create(ctx, missing...)
  → [{id:uuid-2, ...}, {id:uuid-3, ...}]

Step 5 — Merge preserving input order
  Build lookup map: mbid → *Artist (from existing + created)
  Iterate input slice, lookup each mbid → result slice
  → [uuid-1, uuid-2, uuid-3]
```

### Why read-then-write instead of Create-all?

- Prepares for the follow-up change: the helper will know exactly which artists are new (step 4), enabling `artist.created` event publishing without modifying the repo contract.
- Reduces unnecessary write pressure on the DB for frequently searched artists.

## New Repository Method: `ListByMBIDs`

### Interface Addition

```go
// entity/artist.go — added to ArtistRepository interface

// ListByMBIDs retrieves artists matching the provided MusicBrainz IDs.
// Returns only artists that exist in the database. The result order
// matches the input mbids order. Unknown MBIDs are silently skipped.
ListByMBIDs(ctx context.Context, mbids []string) ([]*Artist, error)
```

### SQL

```sql
SELECT a.id, a.name, COALESCE(a.mbid, '')
FROM artists a
JOIN unnest($1::varchar[]) WITH ORDINALITY AS t(mbid, ord)
  ON a.mbid = t.mbid
ORDER BY t.ord
```

This reuses the exact pattern of the existing `selectArtistsByMBIDsQuery` in `artist_repo.go`. The query leverages the existing partial unique index on `mbid`.

## Refactored Methods

### Search

```
func (uc *artistUseCase) Search(ctx, query) ([]*Artist, error)
  1. Validate query
  2. Check cache → return if hit
  3. artistSearcher.Search(ctx, query)
  4. Filter: remove entries with empty MBID
  5. Dedup: keep first per MBID (seen map)
  6. persistArtists(ctx, filtered)
  7. Cache persisted results
  8. Return
```

### ListSimilar (refactored)

```
func (uc *artistUseCase) ListSimilar(ctx, artistID, limit) ([]*Artist, error)
  1. Check cache → return if hit
  2. Get artist from DB
  3. artistSearcher.ListSimilar(ctx, artist, limit)
- 4. artistRepo.Create(ctx, artists...)   // OLD: write all
+ 4. Filter: remove entries with empty MBID
+ 5. persistArtists(ctx, filtered)        // NEW: read-then-write
  6. Cache + return
```

### ListTop (refactored)

```
func (uc *artistUseCase) ListTop(ctx, country, tag, limit) ([]*Artist, error)
  1. Check cache → return if hit
  2. artistSearcher.ListTop(ctx, country, tag, limit)
- 3. artistRepo.Create(ctx, artists...)   // OLD: write all
+ 3. Filter: remove entries with empty MBID
+ 4. persistArtists(ctx, filtered)        // NEW: read-then-write
  5. Cache + return
```

## Decisions

- **Empty MBID filtering applies to all three methods**, not just Search. This ensures consistency: Liverty Music only works with MusicBrainz-backed artists regardless of discovery path.
- **No name heuristics needed**: MBID-based dedup is sufficient. Canonical name resolution will be handled asynchronously in the follow-up change.
- **Cache stores post-dedup, post-persist results**: Subsequent cache hits return clean, stable data.
