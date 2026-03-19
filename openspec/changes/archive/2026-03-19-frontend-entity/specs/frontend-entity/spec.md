## ADDED Requirements

### Requirement: Proto-independent Artist entity
The `src/entities/artist.ts` file SHALL export an `Artist` interface with plain fields (`id: string`, `name: string`, `mbid: string`, `fanart?: ArtistFanart`) instead of re-exporting the proto `Artist` class. All fields SHALL be `readonly`. The interface SHALL include a `@source` JSDoc comment referencing `proto/liverty_music/entity/v1/artist.proto — Artist`.

#### Scenario: Artist entity has flat field access
- **WHEN** code accesses an Artist entity's ID
- **THEN** the access pattern SHALL be `artist.id` (not `artist.id?.value`)

#### Scenario: Artist entity fanart has flat field access
- **WHEN** code accesses an Artist entity's HD music logo URL
- **THEN** the access pattern SHALL be `artist.fanart?.hdMusicLogo` (not `artist.fanart?.hdMusicLogo?.value`)

### Requirement: ArtistFanart entity
The `src/entities/artist.ts` file SHALL export an `ArtistFanart` interface with optional string fields for image URLs (`artistThumb`, `artistBackground`, `hdMusicLogo`, `musicLogo`, `musicBanner`) and an optional `logoColorProfile: LogoColorProfile`. All fields SHALL be `readonly`.

#### Scenario: ArtistFanart fields correspond to proto Fanart
- **WHEN** a proto `Fanart` message has `hd_music_logo.value` set to `"https://example.com/logo.png"`
- **THEN** the mapped `ArtistFanart` SHALL have `hdMusicLogo` set to `"https://example.com/logo.png"`

### Requirement: LogoColorProfile entity
The `src/entities/artist.ts` file SHALL export a `LogoColorProfile` interface with `readonly` fields `dominantHue: number`, `dominantLightness: number`, and `isChromatic: boolean`, matching the proto `LogoColorProfile` message.

#### Scenario: LogoColorProfile round-trip
- **WHEN** a proto `LogoColorProfile` has `dominant_hue: 210.5`, `dominant_lightness: 0.7`, `is_chromatic: true`
- **THEN** the mapped entity SHALL have `dominantHue: 210.5`, `dominantLightness: 0.7`, `isChromatic: true`

### Requirement: Artist business logic functions
The `src/entities/artist.ts` file SHALL export standalone functions for artist business logic. Each function SHALL accept entity types (not proto types) as parameters.

#### Scenario: bestLogoUrl prefers HD logo
- **WHEN** `bestLogoUrl(artist)` is called with an artist having both `fanart.hdMusicLogo` and `fanart.musicLogo`
- **THEN** it SHALL return the `hdMusicLogo` value

#### Scenario: bestLogoUrl falls back to standard logo
- **WHEN** `bestLogoUrl(artist)` is called with an artist having only `fanart.musicLogo`
- **THEN** it SHALL return the `musicLogo` value

#### Scenario: bestBackgroundUrl extracts background
- **WHEN** `bestBackgroundUrl(artist)` is called with an artist having `fanart.artistBackground`
- **THEN** it SHALL return the `artistBackground` value

### Requirement: Adapter RPC mapper layer
The `src/adapter/rpc/mapper/` directory SHALL contain pure conversion functions that handle all Proto-to-Entity and Entity-to-Proto transformations. Proto imports (`@buf/liverty-music_schema`) SHALL NOT appear outside `src/adapter/rpc/`.

#### Scenario: artistFrom converts proto Artist to entity
- **WHEN** `artistFrom(protoArtist)` is called with a proto `Artist` message
- **THEN** it SHALL return an entity `Artist` with `id` extracted from `protoArtist.id?.value ?? ''`, `name` from `protoArtist.name?.value ?? ''`, `mbid` from `protoArtist.mbid?.value ?? ''`, and `fanart` mapped from proto `Fanart`

#### Scenario: artistFrom with nil fanart
- **WHEN** `artistFrom(protoArtist)` is called with a proto `Artist` where `fanart` is undefined
- **THEN** the returned entity SHALL have `fanart` as `undefined`

#### Scenario: concertFrom converts proto Concert to entity
- **WHEN** `concertFrom(protoConcert, artistName, hypeLevel, matched, artist?)` is called
- **THEN** it SHALL return a `Concert` entity with all VO wrappers unwrapped (`.value` extracted) and `localDate` converted to a JS `Date`

#### Scenario: concertFrom rejects concerts without localDate
- **WHEN** `concertFrom` is called with a proto `Concert` where `localDate` is undefined
- **THEN** it SHALL return `null`

#### Scenario: hypeFrom converts proto HypeType to entity Hype
- **WHEN** `hypeFrom(HypeType.AWAY)` is called
- **THEN** it SHALL return `'away'`

#### Scenario: hypeFrom defaults to watch for unspecified
- **WHEN** `hypeFrom(HypeType.HYPE_TYPE_UNSPECIFIED)` is called
- **THEN** it SHALL return `'watch'`

#### Scenario: hypeTo converts entity Hype to proto HypeType
- **WHEN** `hypeTo('nearby')` is called
- **THEN** it SHALL return `HypeType.NEARBY`

#### Scenario: journeyStatusFrom converts proto to entity
- **WHEN** `journeyStatusFrom(TicketJourneyStatus.PAID)` is called
- **THEN** it SHALL return `'paid'`

### Requirement: Adapter RPC client layer
The `src/adapter/rpc/client/` directory SHALL contain RPC client classes that encapsulate proto client creation, VO construction for requests, and mapper calls for responses. Each client SHALL accept and return entity types, not proto types.

#### Scenario: ArtistRpcClient.listTop returns entity artists
- **WHEN** `artistRpcClient.listTop(country, tag, limit)` is called
- **THEN** it SHALL call the proto `ArtistService.listTop` RPC, map each response artist through `artistFrom`, and return `Artist[]` (entity type)

#### Scenario: ArtistRpcClient.listSimilar constructs ArtistId VO
- **WHEN** `artistRpcClient.listSimilar(artistId, limit)` is called with a plain string `artistId`
- **THEN** it SHALL construct `new ArtistId({ value: artistId })` internally and pass it to the proto client

#### Scenario: FollowRpcClient.listFollowed returns entity FollowedArtist
- **WHEN** `followRpcClient.listFollowed(signal?)` is called
- **THEN** it SHALL map each proto `FollowedArtist` to entity `{ artist: artistFrom(fa.artist), hype: hypeFrom(fa.hype) }` and return `FollowedArtist[]`

#### Scenario: ConcertRpcClient.listByFollower returns ProximityGroup with entity types
- **WHEN** `concertRpcClient.listByFollower(signal?)` is called
- **THEN** it SHALL return proto `ProximityGroup[]` (the group structure is RPC-specific and mapped at the service level by DashboardService)

#### Scenario: TicketJourneyRpcClient.setStatus converts entity status to proto
- **WHEN** `ticketJourneyRpcClient.setStatus(eventId, 'paid', signal?)` is called
- **THEN** it SHALL construct `new EventId({ value: eventId })` and convert `'paid'` to `TicketJourneyStatus.PAID` via mapper before calling the proto client

### Requirement: Application services proto-free
Services in `src/services/` that contain application logic (onboarding branching, orchestration) SHALL NOT import from `@buf/liverty-music_schema`. They SHALL depend on adapter RPC client interfaces and entity types only.

#### Scenario: FollowService uses adapter client
- **WHEN** `FollowService.follow(artist)` is called during authenticated mode
- **THEN** it SHALL call `this.rpcClient.follow(artist.id)` passing a plain string ID, not constructing proto VO objects

#### Scenario: FollowService onboarding dispatches entity Artist
- **WHEN** `FollowService.follow(artist)` is called during onboarding
- **THEN** it SHALL dispatch `{ type: 'guest/follow', artist }` where `artist` is an entity `Artist` (not a proto class)

#### Scenario: DashboardService uses adapter mappers
- **WHEN** `DashboardService.loadDashboardEvents()` builds `DateGroup[]`
- **THEN** it SHALL receive entity `FollowedArtist[]` from the follow service (already converted) and work exclusively with entity types

#### Scenario: GuestDataMergeService proto-free
- **WHEN** `GuestDataMergeService.merge()` processes guest follows
- **THEN** it SHALL read `artist.id` (not `artist.id?.value`) from entity `Artist` and call `rpcClient.follow(artistId)` with a plain string

### Requirement: Storage adapter for guest state
The `src/adapter/storage/guest-storage.ts` file SHALL handle serialization and deserialization of `GuestFollow[]` to/from localStorage. It SHALL NOT import proto types.

#### Scenario: Serialize entity Artist to localStorage
- **WHEN** `serializeGuestFollows(follows)` is called with entity `GuestFollow[]`
- **THEN** it SHALL produce a JSON string using `JSON.stringify` with plain object structure

#### Scenario: Deserialize from new format
- **WHEN** `deserializeGuestFollows(json)` parses `[{ "artist": { "id": "abc", "name": "X" }, "home": null }]`
- **THEN** it SHALL return `GuestFollow[]` with entity `Artist` objects

#### Scenario: Backward-compatible deserialization from proto format
- **WHEN** `deserializeGuestFollows(json)` encounters legacy proto format `{ "artist": { "id": { "value": "abc" }, "name": { "value": "X" } } }`
- **THEN** it SHALL detect the nested VO structure and unwrap to produce entity `Artist` objects

#### Scenario: Corrupt data returns empty array
- **WHEN** `deserializeGuestFollows(json)` receives malformed JSON
- **THEN** it SHALL return an empty array without throwing

### Requirement: Proto import boundary
All imports from `@buf/liverty-music_schema` (both `bufbuild_es` and `connectrpc_es` packages) SHALL be confined to `src/adapter/rpc/`. No file outside `src/adapter/rpc/` SHALL contain proto imports.

#### Scenario: Entity files are proto-free
- **WHEN** any file in `src/entities/` is inspected
- **THEN** it SHALL NOT contain imports from `@buf/liverty-music_schema`

#### Scenario: State files are proto-free
- **WHEN** any file in `src/state/` is inspected
- **THEN** it SHALL NOT contain imports from `@buf/liverty-music_schema`

#### Scenario: Route and component files are proto-free
- **WHEN** any file in `src/routes/` or `src/components/` is inspected
- **THEN** it SHALL NOT contain imports from `@buf/liverty-music_schema`

#### Scenario: Service files are proto-free
- **WHEN** any file in `src/services/` is inspected
- **THEN** it SHALL NOT contain imports from `@buf/liverty-music_schema`

## MODIFIED Requirements

### Requirement: Artist entity
The `src/entities/artist.ts` file SHALL export an `Artist` interface with plain readonly fields (`id: string`, `name: string`, `mbid: string`, `fanart?: ArtistFanart`) and standalone business logic functions (`bestLogoUrl`, `bestBackgroundUrl`). It SHALL NOT re-export or import the proto `Artist` class. The `ArtistFanart` and `LogoColorProfile` interfaces SHALL also be exported from this file.

#### Scenario: Discovery service returns entity Artist
- **WHEN** `ArtistRpcClient.listTop()`, `search()`, or `listSimilar()` is called
- **THEN** the response SHALL return entity `Artist` objects with flat field access (no `.value` wrappers)

#### Scenario: Artist with fanart preserved through discovery
- **WHEN** an `Artist` proto is returned from ArtistService with `fanart.logoColorProfile` populated
- **THEN** the mapped entity `Artist` SHALL have `fanart.logoColorProfile` with `dominantHue`, `dominantLightness`, and `isChromatic` fields

#### Scenario: Physics bubble composition
- **WHEN** the discovery dna-orb needs physics properties (`x`, `y`, `radius`) for an artist
- **THEN** it SHALL use a `PhysicsBubble` composition type `{ artist: Artist, x: number, y: number, radius: number }` where `Artist` is the entity interface

### Requirement: FollowedArtist entity
The `src/entities/follow.ts` file SHALL export a `FollowedArtist` interface containing the entity `Artist` object and a `Hype` value. Components that need specific artist fields SHALL access them via `followedArtist.artist.name` (not `followedArtist.artist.name?.value`).

#### Scenario: FollowedArtist from ListFollowed RPC
- **WHEN** the follow RPC client receives a ListFollowed response
- **THEN** it SHALL map each proto `FollowedArtist` to `{ artist: artistFrom(fa.artist), hype: hypeFrom(fa.hype) }` returning entity types

#### Scenario: FollowedArtist during onboarding
- **WHEN** the follow service is called during onboarding (`isOnboarding === true`)
- **THEN** it SHALL return `FollowedArtist` objects with the entity `Artist` from the guest state

### Requirement: Concert entity
The `src/entities/concert.ts` file SHALL export a `Concert` interface with an `artist?: Artist` field (entity type). The `Concert` interface fields SHALL use plain types (`id: string`, `date: Date`, `startTime: string`) without VO wrappers.

#### Scenario: Concert with artist fanart
- **WHEN** a Concert is constructed from a proto concert via `concertFrom` mapper
- **THEN** `concert.artist` SHALL contain the entity `Artist` with `fanart` (including `logoColorProfile` when available)

#### Scenario: Concert template accesses logo URL
- **WHEN** an event-card template needs the logo URL
- **THEN** it SHALL derive it via `bestLogoUrl(concert.artist)` using the entity function (not proto `.value` access)

### Requirement: Guest state stores entity Artist
The guest state (`AppState.guest.follows`) SHALL store entity `Artist` objects (plain interfaces) instead of proto `Artist` class instances. The persistence layer SHALL use `adapter/storage/guest-storage.ts` for serialization, not proto `toJsonString()`/`fromJson()`.

#### Scenario: Follow during onboarding persists entity Artist
- **WHEN** a user follows an artist during onboarding discovery
- **THEN** the guest state SHALL store the entity `Artist` object (plain interface with flat fields)

#### Scenario: Guest state survives page reload
- **WHEN** the guest state is persisted to localStorage and the page is reloaded
- **THEN** `deserializeGuestFollows()` SHALL reconstruct entity `Artist` objects from plain JSON (no proto `fromJson` needed)

#### Scenario: Guest merge sends correct artist IDs
- **WHEN** `GuestDataMergeService.merge()` processes guest follows after login
- **THEN** it SHALL read `artist.id` (string) from the entity `Artist` objects

## REMOVED Requirements

### Requirement: Single mapping point
**Reason**: Replaced by the adapter boundary pattern. Instead of proto flowing through all layers with mapping only at templates, entity interfaces now provide the single canonical type, and adapter/rpc/mapper handles all proto conversion at the boundary.
**Migration**: Proto-to-entity conversion happens in `adapter/rpc/mapper/`. Entity types flow through services, state, and components. No mapping needed at template level — entity fields are directly usable.
