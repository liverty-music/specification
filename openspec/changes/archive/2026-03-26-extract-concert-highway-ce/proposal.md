## Why

The Welcome page needs to display the same concert dashboard UI that authenticated users see, so new visitors can experience the product's value before signing up. Currently the 3-column lane grid (home/nearby/away), event cards, laser beams, and date separators are all embedded directly in `dashboard-route`. This makes reuse impossible without duplicating code.

Additionally, `dashboard-service` bundles orchestration logic for three unrelated domains (follows, concerts, journeys) into a single service, preventing `welcome-route` from accessing the `ProximityGroup → DateGroup` conversion.

## What Changes

- Extract a new `<concert-highway>` custom element (CE) from `dashboard-route` encapsulating the 3-column lane grid, stage header, date separators, laser beam overlay, and scroll tracking
- Decompose `dashboard-service` by moving each method to its domain service:
  - `protoGroupToDateGroup()` → `concert-service` (as public `toDateGroups()`)
  - `fetchFollowedArtistMap()` → `follow-service`
  - `fetchJourneyMap()` → `journey-service`
  - Orchestration (`loadDashboardEvents`) → `dashboard-route` (inline)
- Delete `dashboard-service` after migration
- Rewrite `welcome-route` to use `<concert-highway>` with data from `listWithProximity` RPC (tokyo fixed home, preview artist IDs)
- Apply "Sticky CTA + Peek Preview" UX layout to `welcome-route`: fixed-height scrollable preview with fade mask and sticky CTA at bottom

## Capabilities

### New Capabilities

- `concert-highway-ce`: Reusable custom element that renders the 3-column concert lane grid with laser beam effects, accepting `DateGroup[]` data and supporting readonly mode

### Modified Capabilities

- `welcome-dashboard-preview`: Preview now uses the real dashboard CE with `listWithProximity` RPC instead of a custom inline implementation; layout changes to Sticky CTA + Peek Preview pattern

## Impact

- **frontend/src/components/live-highway/**: New `concert-highway.*` files (CE)
- **frontend/src/routes/dashboard/**: Refactored to consume `<concert-highway>`, grid/beam CSS moves to CE
- **frontend/src/routes/welcome/**: Rewritten template and data loading; new CSS for peek preview layout
- **frontend/src/services/dashboard-service.ts**: Deleted
- **frontend/src/services/concert-service.ts**: Gains `toDateGroups()` method
- **frontend/src/services/follow-service.ts**: Gains `fetchFollowedArtistMap()` method
- **frontend/src/services/journey-service.ts**: Gains `fetchJourneyMap()` method (if not already present)
- No backend or proto changes required — uses existing `ListWithProximity` RPC
