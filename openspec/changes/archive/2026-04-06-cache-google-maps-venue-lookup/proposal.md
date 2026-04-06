## Why

`resolveVenue()` calls the Google Places API for every scraped concert venue, even when the same venue was resolved in a previous concert discovery batch and its record already exists in the database. Google Places Text Search is billed per request, so recurring discoveries for popular venues (e.g., Budokan, Zepp) incur unnecessary API costs.

The existing `venue-normalization` spec intentionally removed name-based DB fallback in favour of always obtaining a canonical `google_place_id` from the API first. This change introduces a DB-first lookup keyed on `(listed_venue_name, admin_area)` that runs **before** the API call, preserving the canonical-ID invariant while eliminating redundant billing.

## What Changes

- Add `GetByListedName(listedVenueName string, adminArea *string)` to `VenueRepository`.
- Add a `(listed_venue_name, admin_area)` index to the `venues` table.
- Prepend a DB lookup step to `resolveVenue()` in `ConcertCreationUseCase`: if a venue is found by listed name, return it immediately without calling the Places API.
- The existing Places API → DB (`GetByPlaceID`) → create flow is unchanged when the DB lookup misses.

## Capabilities

### New Capabilities

- `venue-name-cache`: DB-first venue lookup by listed name and admin area to avoid redundant Google Places API calls.

### Modified Capabilities

- `venue-normalization`: Resolution strategy gains a DB-first step before the Places API call; the canonical `google_place_id` requirement is retained for all newly created venues.

## Impact

- **Backend**: `entity.VenueRepository` interface, `rdb.VenueRepository`, `ConcertCreationUseCase.resolveVenue()`.
- **Database**: New index on `venues(listed_venue_name, admin_area)`; new `VenueRepository.GetByListedName` query.
- **Billing**: Google Places API calls reduced for any venue seen more than once across discovery batches.
- **No proto changes**: purely internal; no RPC surface changes.
