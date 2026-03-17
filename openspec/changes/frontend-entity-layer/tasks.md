## 1. Create Entity Layer

- [x] 1.1 Create `src/entities/artist.ts` with `Artist` and `Fanart` interfaces (fields: id, name, mbid, fanart)
- [x] 1.2 Create `src/entities/follow.ts` with `FollowedArtist` interface (artist fields + hype) and `Hype` string union type
- [x] 1.3 Create `src/entities/concert.ts` with `Concert` interface (renamed from `LiveEvent`), `DateGroup`, `HypeLevel`, `LaneType`
- [x] 1.4 Create `src/entities/index.ts` barrel export

## 2. Migrate Service Clients to Entity Types

- [x] 2.1 Update `follow-service-client.ts`: remove `FollowedArtistInfo` interface, return `FollowedArtist[]` from entity layer
- [x] 2.2 Update `dashboard-service.ts`: replace inline artist map type with `FollowedArtist` entity, import `Concert`/`DateGroup`/`HypeLevel`/`LaneType` from entities

## 3. Migrate Components

- [x] 3.1 Replace `components/live-highway/live-event.ts` contents with re-exports from `entities/concert.ts` (`export type { Concert as LiveEvent, ... }`)
- [x] 3.2 Update `event-card.ts` imports if directly referencing `live-event.ts` types
- [x] 3.3 Update `event-detail-sheet.ts` imports if directly referencing `live-event.ts` types

## 4. Remove Grid View from My Artists

- [x] 4.1 Remove grid toggle button from `my-artists-route.html` (svg-icon list/grid toggle)
- [x] 4.2 Remove `<ul class="artist-grid">` section and all grid tile markup from template
- [x] 4.3 Remove context menu `<dialog>` from template
- [x] 4.4 Remove `viewMode === 'list'` condition from list `<ul>` (make list always visible)
- [x] 4.5 Remove from `my-artists-route.ts`: `ViewMode` type, `viewMode` property, `toggleView()`, `tileSpan()`, `onThumbError()`, `contextMenuArtist`, `contextMenuDialog`, all context menu methods, grid touch handlers, `gridLongPressTimer`
- [x] 4.6 Remove from `my-artists-route.css`: `.artist-grid`, `.grid-tile`, `.grid-tile::before`, `.grid-tile-content`, `.grid-tile-name`, `.grid-tile-hype`, span selectors
- [x] 4.7 Update `my-artists-route.ts`: replace local `FollowedArtist` interface with import from `entities/follow.ts`, remove `thumbUrl` field

## 5. Update Tests

- [x] 5.1 Update unit tests referencing `FollowedArtistInfo` or `LiveEvent` to use new entity types
- [x] 5.2 Remove or update E2E tests for grid view (`artist-image-ui.spec.ts` grid scenarios)

## 6. Verification

- [x] 6.1 Run `make check` (lint + typecheck + test) — all pass
- [x] 6.2 Run `npm run build` — production build succeeds
