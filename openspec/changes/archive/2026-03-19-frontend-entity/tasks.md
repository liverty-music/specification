## 1. Entity interfaces

- [x] 1.1 Rewrite `src/entities/artist.ts` — replace proto re-exports with `Artist`, `ArtistFanart`, `LogoColorProfile` interfaces (readonly fields, `@source` comments). Keep `bestLogoUrl()` and `bestBackgroundUrl()` as standalone functions operating on entity types.
- [x] 1.2 Update `src/entities/follow.ts` — `FollowedArtist.artist` type changes from proto `Artist` to entity `Artist`. `Hype` type unchanged.
- [x] 1.3 Update `src/entities/concert.ts` — `Concert.artist` type changes from proto `Artist` to entity `Artist`. Other fields unchanged.
- [x] 1.4 Update `src/entities/index.ts` — export new types (`ArtistFanart`, `LogoColorProfile`), remove proto class re-exports.

## 2. Adapter RPC mapper

- [x] 2.1 Create `src/adapter/rpc/mapper/artist-mapper.ts` — `artistFrom(proto)` → entity, `fanartFrom(proto)` → entity, `logoColorProfileFrom(proto)` → entity. Unit tests for each function including nil/undefined cases.
- [x] 2.2 Create `src/adapter/rpc/mapper/follow-mapper.ts` — `hypeFrom(proto)` and `hypeTo(entity)` consolidated from the two duplicated `hypeTypeToHype()` implementations. Unit tests for all enum values including unspecified/default.
- [x] 2.3 Create `src/adapter/rpc/mapper/concert-mapper.ts` — move `protoConcertToEntity()` from `dashboard-service.ts`, rename to `concertFrom()`, adapt to return entity types. Move `timestampToTimeString()` helper. Unit tests including null localDate case.
- [x] 2.4 Create `src/adapter/rpc/mapper/ticket-journey-mapper.ts` — move `journeyStatusFrom(proto)` and `journeyStatusTo(entity)` from `ticket-journey-service.ts`. Unit tests for all status values.

## 3. Adapter storage

- [x] 3.1 Create `src/adapter/storage/guest-storage.ts` — `serializeGuestFollows(follows)` and `deserializeGuestFollows(json)` with backward-compatible deserialization (handles both proto VO format and new flat format). Unit tests for new format, legacy format, and corrupt data.

## 4. Adapter RPC clients

- [x] 4.1 Create `src/adapter/rpc/client/artist-client.ts` — move `ArtistServiceClient` from `services/`, update return types to use `artistFrom()` mapper. DI interface `IArtistRpcClient`.
- [x] 4.2 Create `src/adapter/rpc/client/follow-client.ts` — extract pure RPC logic from `FollowServiceClient` (follow, unfollow, listFollowed). Accept plain string IDs, construct ArtistId VO internally, return entity types via mapper. DI interface `IFollowRpcClient`.
- [x] 4.3 Create `src/adapter/rpc/client/concert-client.ts` — extract pure RPC logic from `ConcertServiceClient` (listConcerts, listByFollower, listWithProximity, searchNewConcerts, listSearchStatuses). DI interface `IConcertRpcClient`.
- [x] 4.4 Create `src/adapter/rpc/client/ticket-journey-client.ts` — move `TicketJourneyServiceClient` from `services/`, update to use mapper for status conversion. DI interface `ITicketJourneyRpcClient`.

## 5. Service layer refactor

- [x] 5.1 Rewrite `src/services/follow-service.ts` — keep onboarding branching and store dispatch logic. Depend on `IFollowRpcClient` (not proto client). Accept/return entity types. Remove proto imports.
- [x] 5.2 Rewrite `src/services/concert-service.ts` — keep onboarding branching logic. Depend on `IConcertRpcClient`. Remove proto imports (Home VO construction moves to adapter).
- [x] 5.3 Update `src/services/dashboard-service.ts` — remove `protoConcertToEntity()` and `timestampToTimeString()` (moved to adapter mapper). Use `concertFrom()` from adapter. Remove proto imports. Update `fetchFollowedArtistMap` to use entity `Artist.id` (not `.id?.value`).
- [x] 5.4 Update `src/services/guest-data-merge-service.ts` — replace proto `ArtistId` construction with `rpcClient.follow(artist.id)`. Remove proto imports.
- [x] 5.5 Delete old service client files that were moved to adapter (`artist-service-client.ts`, `ticket-journey-service.ts` as standalone services).

## 6. State management update

- [x] 6.1 Update `src/state/app-state.ts` — `GuestFollow.artist` type is now entity `Artist`. No proto import.
- [x] 6.2 Update `src/state/middleware.ts` — replace proto `toJsonString()`/`fromJson()` with `adapter/storage/guest-storage.ts` functions. Remove proto imports. Preserve legacy migration path via adapter's backward-compatible deserializer.
- [x] 6.3 Update `src/state/reducer.ts` — replace `artist.id?.value` with `artist.id`. Remove any proto imports.
- [x] 6.4 Update `src/state/actions.ts` — ensure action payloads use entity `Artist` type.

## 7. Component and route migration

- [x] 7.1 Update `src/routes/discovery/` files — `bubble-manager.ts`, `follow-orchestrator.ts`, `search-controller.ts`, `discovery-route.ts`. Replace proto `Artist` imports with entity imports. Update `.value` access patterns.
- [x] 7.2 Update `src/components/dna-orb/dna-orb-canvas.ts` — use entity `Artist` type. Update `bestLogoUrl()` import to entity version (signature unchanged).
- [x] 7.3 Update `src/routes/my-artists/my-artists-route.ts` — remove local `hypeTypeToHype()` duplicate, import `hypeFrom` from adapter mapper or use entity `Hype` type directly. Remove proto imports.
- [x] 7.4 Update `src/custom-attributes/artist-color.ts` — use entity `LogoColorProfile` type instead of proto.
- [x] 7.5 Update remaining component files that import proto types — scan for any remaining `@buf/liverty-music_schema` imports outside `adapter/rpc/`.

## 8. DI registration and wiring

- [x] 8.1 Update `src/main.ts` — register new adapter RPC client DI interfaces (`IArtistRpcClient`, `IFollowRpcClient`, `IConcertRpcClient`, `ITicketJourneyRpcClient`). Remove old service client registrations that moved to adapter.

## 9. Test updates

- [x] 9.1 Add unit tests for entity functions — `bestLogoUrl`, `bestBackgroundUrl` with entity types (plain object fixtures, no proto construction).
- [x] 9.2 Add unit tests for all mapper functions — round-trip tests, edge cases (undefined, nil fields, enum boundaries).
- [x] 9.3 Add unit tests for storage adapter — serialization round-trip, legacy format migration, corrupt data handling.
- [x] 9.4 Update existing service tests — replace proto `Artist` construction with plain object literals. Verify services are testable without proto dependencies.

## 10. Proto boundary verification

- [x] 10.1 Run `grep -r '@buf/liverty-music_schema' src/ --include='*.ts'` and verify all matches are in `src/adapter/rpc/` only.
- [x] 10.2 Run `make check` — full lint + type check + unit tests pass.
