## Why

The concert detail sheet displays the raw ISO 3166-2 subdivision code (e.g. `JP-13`) as the venue's administrative area instead of the human-readable localized prefecture name (e.g. `東京都`). The root cause is a layering leak: the presentation `Concert` entity carries BOTH the display-ready `locationLabel` and the raw `adminArea` code, so the UI is forced to choose which to render — and chose wrong. Deciding the user-facing representation of a region is an adapter/domain concern, not a UI concern. Every presentation-layer use of `adminArea` actually wants the human-readable label (the detail sheet's Google Maps query re-derives `displayName(adminArea)`, which is exactly `locationLabel`), so the raw code provides no unique value to the UI.

## What Changes

- The presentation `Concert` entity DROPS the raw `adminArea` field. The adapter (`concert-mapper.ts`) becomes the single owner of the proto-code → user-facing-label translation, producing only `locationLabel`.
- The concert detail sheet renders `locationLabel` for the venue's administrative area (no raw code reaches the template).
- The detail sheet's `googleMapsUrl` consumes `locationLabel` directly instead of re-deriving `displayName(adminArea)`; the now-unused `displayName` import is removed from the component.
- The `concert-detail` spec's "Display venue information" scenario is clarified to require the human-readable localized name, never the raw code.
- The `frontend-entity-layer` spec gains a requirement that the `Concert` entity exposes a presentation-ready region label and does NOT carry the raw subdivision code.
- No change to dashboard lane assignment (it derives `hypeLevel`/`matched` upstream and is passed into the mapper — it never read the entity's `adminArea`).

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `concert-detail`: "Display venue information" is modified so the administrative area shown is the human-readable localized prefecture name, not the raw ISO 3166-2 code.
- `frontend-entity-layer`: adds a requirement that the `Concert` entity's region is a presentation-ready label, with the adapter as the single translation point and no raw subdivision code in the presentation type.

## Impact

- Frontend only — no proto, backend, or BSR changes. The raw `admin_area` code still exists in the proto; it is simply not carried into the presentation entity.
  - `frontend/src/entities/concert.ts` — remove `adminArea?: string` from `Concert`.
  - `frontend/src/adapter/rpc/mapper/concert-mapper.ts` — keep `adminArea` as a local var to derive `locationLabel`; stop assigning it to the returned entity.
  - `frontend/src/components/live-highway/event-detail-sheet.ts` — `googleMapsUrl` uses `locationLabel`; remove the `displayName` import.
  - `frontend/src/components/live-highway/event-detail-sheet.html` — bind the venue line to `event.locationLabel`.
  - Tests: `concert-mapper.spec.ts` (drop `adminArea` assertions), `event-detail-sheet.spec.ts` (mock + `googleMapsUrl` cases use `locationLabel`).
- No data migration, no API surface change.
- Out of scope: the ticket journey status UI redesign (tracked as a separate change).
