## Why

The dashboard shows concerts from all followed artists with no way to narrow the view. When a user receives a push notification about a new concert for a specific artist, there is no way to land on a filtered dashboard — every notification click drops the user into the full, unfiltered feed. Users with many followed artists cannot quickly answer "when is this artist playing?"

## What Changes

- Add `artists` query parameter to the dashboard URL (`/dashboard?artists=id1,id2`) supporting multiple artist IDs (comma-separated)
- Filter the concert highway to show only concerts matching the selected artist(s) when the parameter is present
- Synchronise filter state with the URL via `IHistory.replaceState` so the filtered view is shareable and bookmarkable
- Add a filter UI in the page header: active-filter chips (each dismissible) + a trigger button to open an artist-selection bottom sheet
- Update push notification payloads to include `/dashboard?artists=<artistId>` as the action URL so tapping a notification opens a pre-filtered dashboard

## Capabilities

### New Capabilities

- `dashboard-artist-filter`: URL-driven artist filter on the dashboard — query param parsing, computed filtered date groups, URL sync, filter chip UI, and artist-selection bottom sheet

### Modified Capabilities

- `dashboard-lane-introduction`: No requirement changes; implementation touches the same route file but the onboarding flow is unaffected
- `concert-highway-ce`: No requirement changes; `dateGroups` binding source changes from raw groups to filtered groups, component contract is unchanged

## Impact

- **Frontend routes**: `dashboard-route.ts` — `loading()` signature, new `filteredArtistIds` state, new `filteredDateGroups` getter, URL sync
- **Frontend components**: New `artist-filter-bar` component (header chips + bottom sheet); `dashboard-route.html` updated bindings
- **Service Worker** (`sw.ts`): No changes needed — already passes `notification.data.url` through unchanged
- **Backend (out of scope for this change)**: Push notification service must include `/dashboard?artists=<artistId>` in the notification payload URL
