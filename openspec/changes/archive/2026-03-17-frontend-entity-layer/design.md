## Context

The Go backend defines domain types in `internal/entity/` — plain structs with clear naming (`Artist`, `FollowedArtist`, `Fanart`, `Concert`, `Hype`). The frontend has no equivalent layer; instead, each service or component defines its own interface to flatten proto wrapper types (`ArtistId.value`, `Url.value`). This results in:

- 3 interfaces for the same "followed artist" concept (`FollowedArtistInfo`, `FollowedArtist`, inline type in dashboard-service)
- Domain types co-located with UI logic (e.g., `LiveEvent` inside `components/live-highway/`)
- Naming divergence from Go (`HypeLevel` vs `Hype`, `LiveEvent` vs `Concert`)

Additionally, the grid view feature in My Artists is being removed because the thumbnail display quality is insufficient — this cleanup is bundled here since it removes the `FollowedArtist` interface in `my-artists-route.ts` that would otherwise need migration.

## Goals / Non-Goals

**Goals:**
- Single source of truth for frontend domain types in `src/entities/`
- Naming alignment with Go `internal/entity/` (file names, type names, field names)
- Proto-to-entity mapping happens once, in service clients
- Remove grid view feature from My Artists

**Non-Goals:**
- Introducing entity methods / business logic (keep entities as plain interfaces for now)
- Migrating `ArtistBubble` (discovery-specific UI type, not a domain entity)
- Changing the proto-generated types or BSR workflow
- Adding entity validation (protovalidate handles this at the RPC boundary)

## Decisions

### 1. Plain interfaces, not classes

Use TypeScript `interface` (not `class`) for entity types. Entities are data containers — no constructors, no methods, no inheritance. Services create entity objects via object literals during proto mapping.

**Why over classes:** Interfaces are zero-runtime-cost, work naturally with Aurelia's observation system, and align with how proto-generated `PlainMessage<T>` types work. Classes would add constructor boilerplate with no benefit.

### 2. File and type naming aligned with Go entity package

| Go entity file | Go type | Frontend file | Frontend type |
|---|---|---|---|
| `artist.go` | `Artist` | `artist.ts` | `Artist` |
| `artist.go` | `Fanart` | `artist.ts` | `Fanart` |
| `follow.go` | `FollowedArtist` | `follow.ts` | `FollowedArtist` |
| `follow.go` | `Hype` | `follow.ts` | `Hype` |
| `concert.go` | `Concert` | `concert.ts` | `Concert` (rename from `LiveEvent`) |
| `concert.go` | `ProximityGroup` | `concert.ts` | `DateGroup` (keep — UI groups by date label, not proximity) |
| `proximity.go` | `Proximity` | `concert.ts` | `LaneType` (keep — UI uses lane metaphor) |

**Divergence rationale:** `DateGroup` and `LaneType` are UI-presentation concepts that don't map 1:1 to Go's `ProximityGroup` / `Proximity`. Forcing Go names here would reduce clarity in templates. `Concert` replaces `LiveEvent` since it directly maps to the Go entity.

### 3. UI-only fields are allowed on entities

Frontend entities may include fields that don't exist in Go, annotated with comments:

```typescript
export interface Concert {
  // --- mapped from proto ---
  id: string
  artistName: string
  artistId: string
  // ...

  // --- UI-only ---
  hypeLevel: HypeLevel  // derived from follow hype
  matched: boolean       // computed per lane
  logoUrl?: string       // from artist fanart
  backgroundUrl?: string // from artist fanart
}
```

This avoids creating a separate "view model" wrapper just for 1-2 extra fields.

### 4. Backward-compatible re-exports during migration

`components/live-highway/live-event.ts` will become a re-export barrel:

```typescript
export type { Concert as LiveEvent, DateGroup, HypeLevel, LaneType } from '../../entities/concert'
```

This avoids updating every import in one shot. The re-export file can be removed in a follow-up cleanup if desired, but it keeps the diff focused.

### 5. Grid view removal scope

Remove from `my-artists-route.*`:
- `ViewMode` type, `viewMode` property, `toggleView()` method
- Grid toggle button in template
- `<ul class="artist-grid">` section and all grid tile markup
- Context menu dialog (`<dialog>`) and all related methods
- Grid touch handlers (`onGridTouchStart`, `onGridTouchEnd`, `gridLongPressTimer`)
- `tileSpan()`, `onThumbError()`
- All `.artist-grid`, `.grid-tile*` CSS rules
- `thumbUrl` from `FollowedArtist` entity (grid-only field)

Keep: `logoUrl` on `FollowedArtist` — used by event cards via dashboard service.

## Risks / Trade-offs

- **Rename `LiveEvent` → `Concert`** → Templates and tests use `LiveEvent` extensively. Using re-exports minimizes blast radius, but any direct references to the type name in templates (`LiveEvent` in `repeat.for`) will need updating. Risk: missed references causing runtime errors.
  → Mitigation: `make check` (typecheck + lint + test) catches all type errors at build time.

- **Two changes bundled (entity layer + grid removal)** → Larger PR, harder to review.
  → Mitigation: Grid removal is mechanically simple (delete code). Entity migration is type-safe (compiler catches mismatches). Both are self-contained within the frontend repo.
