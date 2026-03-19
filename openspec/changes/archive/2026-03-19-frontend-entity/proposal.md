## Why

The frontend uses BSR-generated proto classes as domain entities directly. Proto Value Object wrappers force verbose access patterns (`artist.id?.value`, `artist.fanart?.hdMusicLogo?.value`) across 25+ files. Business logic is scattered across services, routes, and components because proto classes cannot carry domain methods. This prevents the frontend from matching the backend's clean entity layer (`internal/entity/`) where domain types are proto-independent and business logic is co-located.

## What Changes

- **BREAKING**: Replace proto `Artist` class re-exports in `src/entities/` with plain TypeScript interfaces that mirror Go entity structs (proto as single source of truth for field definitions, proto file paths documented in comments).
- **BREAKING**: Introduce `src/adapter/rpc/client/` layer — RPC client classes that encapsulate proto imports, VO construction, and response mapping. Current service clients (`ArtistServiceClient`, `FollowServiceClient`, `ConcertServiceClient`, `TicketJourneyServiceClient`) move here.
- **BREAKING**: Introduce `src/adapter/rpc/mapper/` layer — pure conversion functions (`artistFrom`, `concertFrom`, `hypeFrom`, etc.) that handle Proto-to-Entity and Entity-to-Proto transformations.
- Introduce `src/adapter/storage/` layer for entity serialization to/from localStorage, replacing direct proto `toJsonString()`/`fromJson()` usage in state middleware.
- Consolidate duplicated business logic (`hypeTypeToHype` in 2 files, `bestLogoUrl`, `bestBackgroundUrl`, `protoConcertToEntity`) into entity standalone functions or adapter mappers.
- Slim down `src/services/` to application-logic-only services (onboarding branching, orchestration). Pure RPC wrappers are absorbed by `adapter/rpc/client/`.

## Capabilities

### New Capabilities
- `frontend-entity`: Domain entity interfaces, standalone business logic functions, adapter layers (rpc/client, rpc/mapper, storage), and proto isolation boundary.

### Modified Capabilities
- `frontend-entity-layer`: **Superseded** — the requirement to use proto `Artist` class directly across all layers is replaced by proto-independent entity interfaces with an adapter boundary.

## Impact

- **Frontend (all layers)**: Every file importing from `@buf/liverty-music_schema` outside `adapter/rpc/` must be updated. ~25 files affected.
- **State management**: `GuestFollow` type changes from storing proto `Artist` to plain entity `Artist`. Persistence middleware switches from proto serialization to adapter/storage.
- **Tests**: Existing tests that construct proto `Artist` instances directly will use plain object literals instead, simplifying test setup.
- **No proto/backend/API changes**: This is purely a frontend architectural refactor. Wire format is unchanged.
