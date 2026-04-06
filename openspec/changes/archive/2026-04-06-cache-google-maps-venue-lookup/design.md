## Context

`ConcertCreationUseCase.resolveVenue()` currently calls Google Places API (Text Search, $32/1000 requests) for every scraped concert venue. The batch-local `newVenues` map and the DB lookup by `google_place_id` only de-duplicate **within a single batch** and **after the API has already been called**. Repeated concert discoveries for the same popular venues (Budokan, Zepp, etc.) across different artists or discovery runs will trigger duplicate API calls.

The `venue-normalization` spec explicitly removed an earlier name-based DB fallback in order to ensure all persisted venues have a canonical `google_place_id`. This design reintroduces a name-based pre-check while preserving that invariant: we only skip the API call when a venue record **already has a `google_place_id`** (i.e. was previously canonicalised).

## Goals / Non-Goals

**Goals:**
- Eliminate Google Places API calls for venues that have been resolved before.
- Keep the canonical `google_place_id` invariant: every venue in the DB was created from a Places API response.
- Minimal surface change — no new infrastructure, no caching layer.

**Non-Goals:**
- Reducing API calls for brand-new venues (first resolution always hits the API).
- Caching in-memory or in Redis.
- Changing how `google_place_id` deduplication works post-API.

## Decisions

### Decision: Key the pre-check on `(listed_venue_name, admin_area)` not on normalised name

The scraped `listed_venue_name` is what we have before calling the API. A normalised-name approach would require additional logic and could produce false positives (two different venues with similar names). Using the exact listed name plus optional admin area gives a precise, zero-ambiguity match for re-discovered venues.

**Alternative considered — normalise before lookup**: Lowercasing + stripping punctuation before indexing would improve hit rate for minor scraping variations (e.g., "Zepp Tokyo" vs "ZEPP TOKYO"). Rejected because it adds complexity and the primary benefit (eliminating re-discoveries of the same artist's concert) does not require fuzzy matching.

### Decision: Return the existing venue immediately — do not re-validate with Places API

When `GetByListedName` returns a result, we return it as-is. We do not re-call the API to confirm the `google_place_id` is still valid.

**Rationale**: Venue identity is stable. A venue that exists in our DB was created from a valid Places API response. Validating it again on every hit would negate the cost saving.

### Decision: Add a partial unique index `(listed_venue_name, admin_area)` on the venues table

A unique index (rather than a plain index) prevents duplicate entries for the same listed name + admin area combination, which could otherwise accumulate if two concurrent discovery batches race for the same new venue.

**Alternative considered — application-level dedup only**: The existing batch-local `newVenues` map handles same-batch races, but not across concurrent event consumers. A DB-level index is the safer guard.

### Decision: Lookup is `GetByListedName` on `VenueRepository`, not a usecase-layer cache

Keeping the lookup in the repository layer preserves Clean Architecture: the usecase calls a named operation without knowing the index details. It also means the lookup is exercised by the existing integration test suite without any mock changes.

## Risks / Trade-offs

- **Stale listed name**: If Gemini returns a slightly different `listed_venue_name` for the same venue across scrapes, the pre-check misses and the API is called again. This creates a second venue record for the same physical location. Mitigation: the `google_place_id` unique index (`idx_venues_google_place_id`) remains in place and `GetByPlaceID` will still de-duplicate at the DB level, so no duplicate venue rows will be created — only an extra API call.

- **Index maintenance cost**: Adding an index on `(listed_venue_name, admin_area)` has a minor write overhead. The venues table grows slowly (only on new concert discoveries), so this is negligible.

## Migration Plan

1. Atlas migration: add index `idx_venues_listed_name_admin_area` on `(listed_venue_name, admin_area)`.
2. Deploy backend with updated `VenueRepository` and `resolveVenue()` — backward compatible (no column additions, no proto changes).
3. No rollback risk: the pre-check is purely additive; removing it reverts behaviour to current state.
