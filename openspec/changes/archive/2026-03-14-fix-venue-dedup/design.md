## Context

The concert discovery pipeline scrapes multiple sources per artist. Each source may use a slightly different text representation for the same venue (e.g., "SGCホール有明" vs "SGC HALL ARIAKE"). The current `resolveVenue` uses exact string matching (`WHERE name = $1 OR raw_name = $1`), which creates duplicate venue records for each text variant. These duplicates cascade into duplicate event records because the DB natural key `(venue_id, local_event_date, start_at)` treats different venue IDs as distinct.

The async enrichment pipeline (MusicBrainz → Google Maps fallback) is designed to merge duplicates post-hoc, but this has gaps: enrichment can fail, and timing windows allow duplicates to persist before enrichment completes.

## Goals / Non-Goals

**Goals:**
- Eliminate venue duplication at creation time by using Google Places API `place_id` as the canonical identifier
- Prevent event duplication caused by venue text variants by removing venue from the dedup key
- Clean up existing inconsistent data for a fresh start

**Non-Goals:**
- Removing the async enrichment pipeline entirely — it remains as a fallback for venues not found by Google Places (small/new venues)
- Changing the MusicBrainz integration — it continues to work as before for MBID enrichment
- Handling multi-artist events (festivals where multiple artists share an event) — out of scope

## Decisions

### Decision 1: Synchronous Google Places lookup in `resolveVenue`

**Choice**: Call Google Places API Text Search synchronously during `CreateFromDiscovered` to obtain `place_id` and canonical name before creating/looking up a venue.

**Flow**:
```
resolveVenue(listed_venue_name, admin_area)
  ├─ Check batch cache (newVenues map by place_id) → hit: return existing
  ├─ Google Places API Text Search(listed_venue_name + admin_area)
  │   ├─ Found: GetByPlaceID(place_id)
  │   │   ├─ Exists: return existing venue ID
  │   │   └─ Not found: Create venue (name=canonical, raw_name=listed, place_id, enriched)
  │   └─ Not found: fallback to current flow
  │       ├─ GetByName(listed_venue_name) → return if found
  │       └─ Create venue (name=raw_name=listed, pending enrichment)
  └─ API error: fallback to current flow (same as "Not found")
```

**Alternatives considered**:
- *Batch all venues then call API*: More complex, marginal benefit since batches are small (5-10 venues)
- *Keep async-only enrichment, improve matching*: Fuzzy matching is fragile and doesn't solve the root cause

**Rationale**: Google Places `place_id` is a stable, globally unique identifier. Looking it up at creation time eliminates the entire class of text-matching bugs. Cost is negligible at current volume (~$0.032/request, <10 unique venues per batch).

### Decision 2: Remove venue from dedup key, add artist_id

**Choice**: Change the dedup key from `(date|venue|start_at)` to `(date|start_at)` at the application layer, and the DB unique constraint from `(venue_id, local_event_date, start_at)` to `(artist_id, local_event_date, start_at)` on the events table.

**Rationale**: An artist cannot perform at two different venues at the same time on the same day. This is a stronger invariant than venue matching, and it's immune to text variations.

**Application-layer dedup (concert_uc.go)**:
- `DateVenueKey()` → `DateKey()`: returns `date` only
- `DedupeKey()`: returns `date|start_at_utc` (no venue)
- `seen` map key: `date|start_at_utc`
- `seenDate` map key: `date` (replaces `seenDateVenue`)

**DB constraint**:
- `artist_id` must be added to the `events` table (currently only on `concerts`)
- New unique constraint: `UNIQUE NULLS NOT DISTINCT (artist_id, local_event_date, start_at)`
- The upsert query references this new constraint

**Alternatives considered**:
- *Keep venue in key, normalize venue text first*: Still fragile — normalization can't handle all variants
- *Use venue_id after Places API resolution*: Better than text, but adding artist_id is simpler and more robust

### Decision 3: Data cleanup via migration

**Choice**: A DB migration that truncates all concerts, events, and orphaned venues. The next discovery cron run will re-populate with clean, deduplicated data.

**Rationale**: The existing data has known duplicates that cannot be reliably de-duplicated in-place (some venues have `enrichment_status = 'failed'`). Since the discovery pipeline can regenerate all data within one cron cycle, a clean slate is the simplest approach.

**Migration steps**:
1. `DELETE FROM concerts` (removes FK references to events)
2. `DELETE FROM events` (removes FK references to venues)
3. `DELETE FROM venues WHERE NOT EXISTS (SELECT 1 FROM events WHERE events.venue_id = venues.id)` — clean up orphaned venues (should be all of them after step 2)
4. Add `artist_id` column to events (NOT NULL, FK to artists)
5. Drop old constraint `uq_events_natural_key`
6. Add new constraint `UNIQUE NULLS NOT DISTINCT (artist_id, local_event_date, start_at)`

## Risks / Trade-offs

**[Risk] Google Places API unavailability during venue resolution** → Mitigation: Fallback to current text-based flow. Venue will be created with `pending` enrichment status and handled by the async pipeline as before.

**[Risk] Google Places API returns wrong venue for ambiguous names** → Mitigation: Include `admin_area` in the search text to disambiguate. Accept that edge cases may still occur — the async enrichment pipeline remains as a second pass.

**[Risk] Data loss during cleanup migration** → Mitigation: Data is fully recoverable via the next cron run. The migration only deletes concert/event/venue data, not artist or user data. Search logs are preserved so the 24h cooldown applies normally.

**[Risk] `artist_id` on events table denormalization** → Trade-off accepted. The `artist_id` already exists on the `concerts` table (1:1 with events for now). Adding it to `events` enables a stronger unique constraint. The cost is one extra UUID column.

**[Trade-off] Same-day, same-time events for different artists at the same venue** → The new constraint `(artist_id, local_event_date, start_at)` is per-artist, so different artists at the same venue/time are not affected. This is correct behavior.
