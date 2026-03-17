## Why

Frontend domain types are scattered across service clients, route ViewModels, and component files — each defining its own interface for the same concept (e.g., `FollowedArtistInfo`, `FollowedArtist`, `LocalFollowedArtist`). This creates redundant proto-to-POJO mapping, naming inconsistency with the Go backend entity layer, and makes it hard to find where a domain concept is defined. Introducing a dedicated `src/entities/` layer consolidates domain types in one place, aligned with Go's `internal/entity/` package.

## What Changes

- Create `src/entities/` directory with entity modules mirroring Go's `internal/entity/` naming:
  - `artist.ts` — `Artist` (id, name, mbid, fanart URLs)
  - `follow.ts` — `FollowedArtist` (artist + hype), `Hype` type
  - `concert.ts` — `LiveEvent`, `DateGroup`, `HypeLevel`, `LaneType` (relocated from `components/live-highway/live-event.ts`)
  - `venue.ts` — venue-related types if applicable
- Replace `FollowedArtistInfo` (follow-service-client.ts), `FollowedArtist` (my-artists-route.ts), and inline artist map types (dashboard-service.ts) with unified entity types
- Move `LiveEvent` / `DateGroup` from `components/live-highway/live-event.ts` to `entities/concert.ts`
- Update all import paths across services, routes, and components
- Remove `grid view` feature from My Artists (toggle button, grid template, grid CSS, context menu, touch handlers, `tileSpan`, `onThumbError`, `ViewMode` type)

## Capabilities

### New Capabilities
- `frontend-entity-layer`: Centralized domain type definitions for the frontend, aligned with Go backend entity naming

### Modified Capabilities

## Impact

- `src/services/follow-service-client.ts` — Remove `FollowedArtistInfo`, map to entity types
- `src/services/dashboard-service.ts` — Remove inline artist map type, use entity types
- `src/routes/my-artists/my-artists-route.ts` — Remove `FollowedArtist` interface, `ViewMode`, grid-related methods; import from entities
- `src/routes/my-artists/my-artists-route.html` — Remove grid view section, toggle button, context menu dialog
- `src/routes/my-artists/my-artists-route.css` — Remove `.artist-grid`, `.grid-tile*` styles
- `src/components/live-highway/live-event.ts` — Becomes re-export from `entities/concert.ts`
- `src/components/live-highway/event-card.ts` — Update import path
- `src/components/live-highway/event-detail-sheet.ts` — Update import path
- All test files referencing moved types
