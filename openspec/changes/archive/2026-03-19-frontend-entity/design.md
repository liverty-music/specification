## Context

The frontend currently re-exports BSR-generated proto `Artist` class directly from `src/entities/artist.ts` and uses it as the domain type across all layers. This creates two problems:

1. **VO wrapper verbosity**: Proto Value Object wrappers require `artist.id?.value`, `artist.fanart?.hdMusicLogo?.value` etc. across 25+ files.
2. **Business logic scattering**: Proto classes cannot carry domain methods, so logic like `bestLogoUrl()`, `hypeTypeToHype()`, and `protoConcertToEntity()` is scattered across services, routes, and custom attributes — with `hypeTypeToHype` duplicated in two files.

The Go backend solves this with a clean entity layer (`internal/entity/`) where domain structs are proto-independent, and `adapter/rpc/mapper/` handles all Proto ↔ Entity conversion. The frontend has no equivalent boundary.

## Goals / Non-Goals

**Goals:**
- Define proto-independent TypeScript entity interfaces in `src/entities/` that mirror Go entity structs field-for-field, using proto definitions as single source of truth.
- Create `src/adapter/rpc/client/` to encapsulate all RPC calls, proto imports, and VO construction.
- Create `src/adapter/rpc/mapper/` for pure Proto ↔ Entity conversion functions.
- Create `src/adapter/storage/` for entity serialization to/from localStorage.
- Confine all proto imports (`@buf/liverty-music_schema`) to `src/adapter/rpc/` — no other layer touches proto types.
- Consolidate scattered business logic into entity standalone functions.
- Services that contain only RPC logic (no application branching) are absorbed into adapter/rpc/client.
- Strengthen test coverage: entity functions get pure unit tests, adapter mappers get round-trip tests, services test application logic with mocked adapter interfaces.

**Non-Goals:**
- Changing the proto schema, backend API, or wire format.
- Introducing a class-based entity model (interfaces + standalone functions chosen for `@aurelia/state` compatibility).
- Migrating to a different state management library.
- Refactoring components or templates beyond updating import paths and removing `.value` access.

## Decisions

### 1. Interface + standalone functions over Class

**Choice**: Entity types are TypeScript `interface` with `readonly` fields. Business logic is standalone exported functions.

**Rationale**: `@aurelia/state` uses a Redux-style reducer with immutable spread updates (`{ ...state, artist: { ...artist } }`). Class instances lose their prototype on spread. Standalone functions are tree-shakable. Aurelia's observation system works best at the ViewModel boundary, not on domain objects. See explore-mode analysis for full comparison.

**Alternative rejected**: Class with getter methods — breaks reducer spread, requires reconstruction after `JSON.parse`, prevents tree-shaking of unused methods.

### 2. Symmetric adapter structure with Go backend

**Choice**: Mirror Go's `adapter/rpc/` structure:

```
Go (inbound)                         TS (outbound)
adapter/rpc/handler/  ← recv proto   adapter/rpc/client/  ← send proto
adapter/rpc/mapper/   ← convert      adapter/rpc/mapper/  ← convert
```

**Rationale**: Consistent mental model across the poly-repo. Handlers receive proto and convert inward; clients convert outward and send proto. Mappers are pure functions in both.

### 3. RPC clients in adapter, not services

**Choice**: Pure RPC wrapper classes move from `services/` to `adapter/rpc/client/`. Only services with application logic (onboarding branching, multi-service orchestration) remain in `services/`.

| Current service | Application logic? | Destination |
|---|---|---|
| `ArtistServiceClient` | None | `adapter/rpc/client/artist-client.ts` |
| `FollowServiceClient` | Onboarding branching, store dispatch | Split: RPC → `adapter/rpc/client/`, logic → `services/follow-service.ts` |
| `ConcertServiceClient` | Onboarding branching | Split: RPC → `adapter/rpc/client/`, logic → `services/concert-service.ts` |
| `DashboardService` | Orchestration | Stays in `services/` |
| `TicketJourneyServiceClient` | None | `adapter/rpc/client/ticket-journey-client.ts` |
| `GuestDataMergeService` | Best-effort merge, store dispatch | Stays in `services/`, uses adapter/rpc/client |

**Rationale**: Services that are pure RPC wrappers add no value as a separate layer. Moving them to adapter eliminates indirection and makes the proto isolation boundary explicit.

### 4. Mapper naming convention: `artistFrom` / `artistTo`

**Choice**: Mapper functions are named `{entity}From` and `{entity}To` (e.g., `artistFrom`, `artistTo`, `hypeFrom`, `hypeTo`). Within `adapter/rpc/mapper/`, the proto context is self-evident.

**Alternative rejected**: `artistFromProto` — redundant given the file lives in `adapter/rpc/mapper/`.

### 5. Storage adapter for localStorage

**Choice**: `adapter/storage/guest-storage.ts` handles serialization/deserialization of `GuestFollow[]` to/from plain JSON. No proto dependency.

**Rationale**: Current middleware calls `Artist.fromJson()` / `toJsonString()` directly, coupling state persistence to proto. With entity interfaces, serialization becomes plain `JSON.stringify`/`JSON.parse` since entity types are simple data shapes.

### 6. Proto file path in entity comments

**Choice**: Each entity interface includes a JSDoc comment referencing the proto file path as the source of truth.

```typescript
/**
 * A musical artist or group recorded in the system.
 * @source proto/liverty_music/entity/v1/artist.proto — Artist
 */
export interface Artist { ... }
```

**Rationale**: Makes the proto-entity mapping explicit and auditable. When proto fields change, developers know which entity to update.

## Risks / Trade-offs

**[Proto field drift]** Entity interfaces could fall out of sync with proto definitions when fields are added.
→ Mitigation: `@source` comments reference exact proto message. CI could add a lint check later, but manual review is acceptable at current scale.

**[Migration surface]** ~25 files need import path changes and `.value` removal.
→ Mitigation: TypeScript compiler will catch all breakages. No runtime risk — this is a type-level refactor.

**[Onboarding state migration]** Existing localStorage data uses proto JSON format. New format is plain JSON.
→ Mitigation: `adapter/storage/guest-storage.ts` includes backward-compatible deserialization that handles both proto JSON (nested `{ id: { value: "..." } }`) and new flat format (`{ id: "..." }`).

**[DI interface registration]** Moving RPC clients to adapter requires updating Aurelia DI registrations in `main.ts`.
→ Mitigation: Straightforward — update `DI.createInterface` locations and `main.ts` registration calls.
