### Requirement: Artist entity
The frontend SHALL use the BSR-generated proto `Artist` class from `@buf/liverty-music_schema.bufbuild_es/liverty_music/entity/v1/artist_pb.js` as the canonical artist representation across all layers (services, state, components). Custom interfaces (`ArtistBubble`, `GuestFollow`) that duplicate Artist fields SHALL be removed. The `src/entities/artist.ts` file SHALL re-export the proto `Artist` type and provide helper functions for common field access patterns (e.g., best logo URL extraction).

#### Scenario: Discovery service returns proto Artist
- **WHEN** `ArtistServiceClient.listTop()`, `search()`, or `listSimilar()` is called
- **THEN** the response SHALL return proto `Artist` objects directly, not mapped `ArtistBubble` interfaces

#### Scenario: Artist with fanart preserved through discovery
- **WHEN** an `Artist` proto is returned from ArtistService with `fanart.logoColorProfile` populated
- **THEN** the `logoColorProfile` data SHALL be preserved on the `Artist` object without being stripped

#### Scenario: Physics bubble composition
- **WHEN** the discovery dna-orb needs physics properties (`x`, `y`, `radius`) for an artist
- **THEN** it SHALL use a `PhysicsBubble` composition type `{ artist: Artist, x: number, y: number, radius: number }` instead of flattening artist fields into the physics type

### Requirement: FollowedArtist entity
The `src/entities/follow.ts` file SHALL export a `FollowedArtist` interface containing the proto `Artist` object and a `Hype` value. The interface SHALL NOT flatten artist fields (`id`, `name`, `logoUrl`) into top-level properties. Components that need specific artist fields SHALL access them via `followedArtist.artist.name?.value` or equivalent accessors.

#### Scenario: FollowedArtist from ListFollowed RPC
- **WHEN** the follow service client receives a ListFollowed response
- **THEN** it SHALL map each proto `FollowedArtist` to `{ artist: Artist, hype: Hype }` preserving the full `Artist` object including `fanart`

#### Scenario: FollowedArtist during onboarding
- **WHEN** the follow service client is called during onboarding (`isOnboarding === true`)
- **THEN** it SHALL return `FollowedArtist` objects with the proto `Artist` from the guest state, including any `fanart` data that was available at follow time

### Requirement: Concert entity
The `src/entities/concert.ts` file SHALL export a `Concert` interface that includes an `artist?: Artist` field (proto type) instead of separate `logoUrl`, `backgroundUrl`, and `logoColorProfile` fields. Components SHALL extract display-specific values from the `Artist` object.

#### Scenario: Concert with artist fanart
- **WHEN** a Concert is constructed from a proto concert and an artist map entry
- **THEN** `concert.artist` SHALL contain the full proto `Artist` with `fanart` (including `logoColorProfile` when available)

#### Scenario: Concert template accesses logo URL
- **WHEN** an event-card template needs the logo URL
- **THEN** it SHALL derive it from `concert.artist.fanart.hdMusicLogo?.value ?? concert.artist.fanart.musicLogo?.value`

### Requirement: Single mapping point
Proto `Artist` objects SHALL flow through service clients, state, and into components without intermediate mapping. Service clients SHALL NOT extract or flatten proto fields into custom interfaces. The only mapping boundary is at the template/component level where proto accessor syntax (`artist.name?.value`) is used for display.

#### Scenario: Service returns proto types
- **WHEN** `FollowServiceClient.listFollowed()` is called
- **THEN** it SHALL return objects containing proto `Artist` instances, not manually extracted fields

#### Scenario: Dashboard service passes Artist through
- **WHEN** `DashboardService` builds `DateGroup[]`
- **THEN** each `Concert` SHALL contain the proto `Artist` from the follow data, with no intermediate extraction of fanart fields

### Requirement: Guest state stores proto Artist
The guest state (`AppState.guest.follows`) SHALL store proto `Artist` objects instead of `{ artistId, name }` tuples. The persistence middleware SHALL serialize `Artist` objects using proto-ES `toJsonString()` and deserialize using `fromJson()` to ensure all fields (including nested `Fanart` and `LogoColorProfile`) survive localStorage round-trips.

#### Scenario: Follow during onboarding persists full Artist
- **WHEN** a user follows an artist during onboarding discovery
- **THEN** the guest state SHALL store the full proto `Artist` object (including `fanart` if present) not just `{ artistId, name }`

#### Scenario: Guest state survives page reload
- **WHEN** the guest state is persisted to localStorage and the page is reloaded
- **THEN** `fromJson()` SHALL reconstruct proto `Artist` instances with all nested messages (`Fanart`, `LogoColorProfile`) intact

#### Scenario: Guest merge sends correct artist IDs
- **WHEN** `GuestDataMergeService.merge()` processes guest follows after login
- **THEN** it SHALL read `artist.id?.value` from the stored proto `Artist` objects

### Requirement: Grid view removal
The My Artists route SHALL display artists in list view only. The grid toggle button, grid layout, context menu dialog, and all grid-specific interaction handlers SHALL be removed.

#### Scenario: My Artists page loads
- **WHEN** a user navigates to My Artists
- **THEN** artists are displayed in list view with no toggle button to switch views

#### Scenario: No grid-related CSS
- **WHEN** the My Artists stylesheet is loaded
- **THEN** it SHALL NOT contain `.artist-grid`, `.grid-tile`, or related grid layout rules

### Requirement: Concert region is presentation-ready

The presentation `Concert` entity SHALL expose the venue's administrative area only as a human-readable, localized display label (`locationLabel`). It SHALL NOT carry the raw ISO 3166-2 subdivision code. The adapter layer (`concert-mapper.ts`) is the single point that translates the proto `venue.admin_area` code into the display label; presentation code SHALL consume `locationLabel` and SHALL NOT re-derive the label from a raw code.

#### Scenario: Mapper produces only the display label

- **WHEN** the RPC mapper maps a proto `Concert` whose `venue.admin_area` is a known code (e.g. `JP-13`)
- **THEN** the resulting entity SHALL set `locationLabel` to the localized name (e.g. `東京都`)
- **AND** the entity SHALL NOT expose the raw `JP-13` code

#### Scenario: Missing admin area yields empty label

- **WHEN** the proto `Concert` has no `venue.admin_area`
- **THEN** the entity's `locationLabel` SHALL be an empty string
- **AND** consumers SHALL treat the empty string as "no administrative area to display"

#### Scenario: Presentation consumes the label, not a code

- **WHEN** a component needs the administrative area for display or for composing a derived value (e.g. a Google Maps query)
- **THEN** it SHALL read `locationLabel`
- **AND** it SHALL NOT call the code-to-name normalization helper to re-derive the label
