## Why

The dashboard filter currently only narrows the concert highway by artist, and the artist chips are listed in an arbitrary, unsorted order — so a fan following many artists cannot quickly find the artists that actually have lots of upcoming concerts (the only ones where filtering pays off). Fans also have no way to narrow the highway by their own ticket-acquisition state (e.g. "show only the shows I've applied to" or "the ones I still need to pay for"), even though that state is already tracked per concert. This change makes the existing filter more useful for high-volume followers and adds ticket-journey status as a second, orthogonal filter dimension.

## What Changes

- **Artist chips show a concert count and are sorted by it.** Each artist chip in the filter bottom sheet is prefixed with the number of that artist's upcoming concerts in the loaded dashboard set, the list is sorted by that count descending (ties broken by name ascending), and artists with zero upcoming concerts are hidden (filtering only matters where concerts exist).
- **A second filter facet: ticket journey status.** The same bottom sheet gains a multi-select journey-status chip group (`TRACKING`, `APPLIED`, `UNPAID`, `PAID`, `LOST`). Selection semantics are OR within the facet and AND across facets (artist set AND journey set). The active filter is reflected in a new `journey` URL query parameter. This is a **pure filtering** feature — it does not display deadlines, sort by urgency, or send reminders (those belong to separate features).
- **Guest availability.** The filter trigger and the artist facet are available to unauthenticated (guest) users, who can already follow artists locally — only the onboarding flow suppresses the filter. The journey facet is shown to authenticated users only.
- **A single canonical journey-status presentation map.** The label, emoji icon, and semantic hue for each journey status are defined once and consumed by the new filter chips, the existing concert-card journey badge, and the concert-detail status control, so the visual identity of each status is consistent app-wide. The failure (`LOST`) status adopts a 💔 icon.

## Capabilities

### New Capabilities
- `dashboard-journey-filter`: A ticket-journey-status filter facet on the dashboard filter sheet — multi-select chips with OR-within / AND-across-facet semantics, a `journey` URL query parameter synchronised with the UI, and facet visibility gated to authenticated users.
- `journey-status-presentation`: A single source-of-truth mapping from each ticket-journey status to its display label, emoji icon, and semantic hue token, consumed by every component that renders journey status (filter chips, concert-card badge, concert-detail status control).

### Modified Capabilities
- `dashboard-artist-filter`: The artist-selection bottom sheet now prefixes each chip with its upcoming-concert count, sorts chips by count descending, and hides zero-concert artists; the filter trigger and artist facet are explicitly available to guest (unauthenticated) users.

## Impact

- **frontend** (only — no proto/backend/infra change):
  - `src/routes/dashboard/dashboard-route.ts` / `.html`: a `filteredStatuses` observable, an extended `filteredDateGroups` predicate (artist AND journey), a `countedArtists` computed list, a combined URL sync (single watcher writing both `artists` and `journey` params), and an `isAuthenticated` binding for facet gating.
  - `src/components/artist-filter-bar/*`: a second journey-status chip group, counted/sorted artist chips, guest-aware journey-facet visibility.
  - `src/entities/ticket-journey.ts`: a new `JOURNEY_STATUS_CONFIG` constant (label key + emoji + hue token) as the canonical map.
  - `src/components/live-highway/event-card.*` and `event-detail-sheet.*`: refactored to source labels/icons from the canonical map (no behavioural change beyond the `LOST` icon becoming 💔).
- **No changes** to Protobuf schema, BSR, backend, or cloud-provisioning. Journey status is already delivered to the frontend via the existing `TicketJourneyService.ListByUser` path and attached to each concert.
