## Context

The `fix-venue-dedup` change moved venue resolution to be synchronous at concert creation time via Google Places API. This made the async enrichment pipeline (`venue.created.v1` → `VenueConsumer` → `VenueEnrichmentUseCase`) redundant — it now only processes venues that Places API already failed to find, and almost always fails again.

Current venue creation has two paths:
1. Places API success → venue created with `enrichment_status = 'enriched'`, coordinates, canonical name
2. Places API NotFound → venue created with `enrichment_status = 'pending'`, no coordinates → enrichment retries → fails → `enrichment_status = 'failed'`

Path 2 produces unusable data. This design eliminates it.

## Goals / Non-Goals

**Goals:**
- Eliminate path 2: skip concerts whose venues can't be resolved, log full scraped data for manual recovery
- Remove the entire enrichment pipeline (UC, consumer, event, repository methods)
- Remove venue schema fields that only existed for enrichment: `enrichment_status`, `raw_name`, `mbid`
- Make `placeSearcher` a required dependency (remove nil-guard)
- Remove `GetByName` fallback from venue resolution

**Non-Goals:**
- Removing the `musicbrainz` package — it's still used by `ArtistNameResolutionUseCase`
- Removing `AdminAreaResolver` from the codebase — check if it's used elsewhere; remove only if venue enrichment was its sole consumer
- Changing the Google Places API integration itself
- Handling manual venue data entry (future work if needed)

## Decisions

### 1. Skip concert instead of creating unusable venue

**Decision**: When Places API returns NotFound, emit a structured Warn log with all `ScrapedConcert` fields and skip the concert. Do not create a venue or concert record.

**Alternatives considered**:
- Create venue with NULL coordinates (current behavior) — produces unusable data that degrades proximity calculations and map display
- Queue for manual review in a database table — adds complexity; structured logs can be queried in Cloud Logging and are sufficient for the current scale

**Rationale**: At current scale, manual review of venue resolution failures can be handled via Cloud Logging queries. A dedicated review queue can be added later if volume warrants it.

### 2. Return semantics for `resolveVenue`

**Decision**: `resolveVenue` returns `(venueID string, venue *Venue, skip bool, err error)`. When Places API returns NotFound, return `skip = true` with nil error. The caller skips the concert without aborting the batch.

**Alternative**: Return a sentinel error — but this conflates "skip this concert" with "something went wrong", making the caller's control flow less clear.

### 3. Remove `GetByName` fallback entirely

**Decision**: After Places API, do not fall back to name-based DB lookup. The only lookup path is: Places API → `GetByPlaceID` → create new venue.

**Rationale**: `GetByName` was the pre-Places-API dedup mechanism. With `google_place_id` as the canonical identifier, name-based lookup is unreliable (different scrapers use different name variants). Keeping it creates a false sense of safety.

### 4. Make `placeSearcher` required

**Decision**: Remove the `placeSearcher != nil` guard. Panic at startup if not provided.

**Impact on local dev**: Local development must either configure a real Places API key or provide a stub implementation. This is acceptable since the Gemini-based searcher is already used in dev.

### 5. Schema migration: drop columns

**Decision**: Single migration that drops `enrichment_status`, `raw_name`, `mbid`, the `venue_enrichment_status` enum, and the `idx_venues_mbid` unique index.

**Ordering**: This migration runs after the `fix-venue-dedup` data cleanup migration (which DELETEs all venues), so there are no data concerns.

## Risks / Trade-offs

**[Risk] Permanent data loss for unresolvable venues** → Mitigated by structured logging with full `ScrapedConcert` fields. Logs are retained in Cloud Logging for 30 days. If a pattern of failures emerges, a manual review process or Places API query adjustment can be implemented.

**[Risk] Places API outage causes all concerts to be skipped** → The Gemini searcher already has retry with backoff for transient errors (429, 503, 504). True outages would cause the entire batch to fail (non-retryable error propagated up), not silent skipping. Only definitive NotFound results cause skipping.

**[Trade-off] No MusicBrainz venue lookup** → MusicBrainz venue data was a secondary source that rarely provided data Google Places didn't. The MBID field was never exposed via API. Acceptable loss.

**[Trade-off] No `raw_name` preservation** → With synchronous Places API resolution, `Name` is always the canonical name from Places API. The scraped name is logged in the skip log and stored in `events.listed_venue_name`. No need for a separate `raw_name` column.
