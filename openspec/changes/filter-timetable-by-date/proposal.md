## Why

The dashboard "My Timetable" currently loads **all** concerts of followed artists, including past ones, because `ListByFollower` applies no date filter. Past concerts pile up at the top of the chronological list, pushing upcoming shows down and making the timetable harder to act on. Fans want the timetable to default to "from today onward", while still being able to look back at past concerts on demand (e.g. to revisit a show they attended).

## What Changes

- **BREAKING (behavioral, not wire)**: `ListByFollower` SHALL default to returning only concerts on/after the current date instead of all concerts. Existing callers that relied on receiving past concerts will now receive future-only results unless they opt in via the new parameter.
- Add an optional `from` date parameter to `ListByFollowerRequest` (`entity.v1.LocalDate`, matching `ListByLocationRequest.from`). When provided, the service returns concerts on/after `from`; when omitted, it defaults to the current date.
- The frontend dashboard SHALL always send `from` so the "today" boundary is anchored to the **client's** local date (avoids server-UTC vs client timezone off-by-one at date boundaries).
- Add a **date facet** to the existing dashboard filter bottom sheet: a collapsed "過去のコンサートも表示" affordance that expands a single date field ("この日付以降を表示"). Selecting an earlier date re-fetches the timetable including past concerts from that date.
- Persist the selected `from` in the dashboard URL (query param) so it survives reload and is shareable, consistent with the existing `artists` / `journey` filters.

## Capabilities

### New Capabilities
- `dashboard-date-filter`: The dashboard timetable's date-based filtering — the URL-synced date query parameter, the collapsible date facet in the filter bottom sheet, its default (today onward) and past-inclusive states, and the RPC round-trip re-fetch it triggers (distinct from the client-side artist/journey facets).

### Modified Capabilities
- `live-events`: The `ListByFollower` RPC contract (Live Schedule Access → "List Concerts by Follower") changes to default to future-only results and to accept an optional `from` date that widens the range into the past.

## Impact

- **specification**: `ListByFollowerRequest` gains a `from` field (`entity.v1.LocalDate`). Additive proto change (non-breaking on the wire); triggers BSR regeneration and a new schema version.
- **backend**: `listConcertsByFollowerQuery` gains a `local_event_date >= $2` predicate; handler/use case thread the `from` value (defaulting to `CURRENT_DATE` when unset). No DB migration.
- **frontend**: `ConcertClient.listByFollower` / `ConcertStore` gain a `from` argument; the store cache key incorporates `from`; the dashboard filter bottom sheet gains the date facet and URL sync. The per-artist / journey chip counts recompute over the newly loaded (possibly past-inclusive) set.
- **cross-repo**: Standard proto → BSR → backend/frontend release coordination applies (spec PR → merge → Release → BSR gen → consumer upgrade → type swap).
