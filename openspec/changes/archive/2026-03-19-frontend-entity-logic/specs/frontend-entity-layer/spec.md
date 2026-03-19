## MODIFIED Requirements

### Requirement: Artist entity
The frontend SHALL use the BSR-generated proto `Artist` class from `@buf/liverty-music_schema.bufbuild_es/liverty_music/entity/v1/artist_pb.js` as the canonical artist representation across all layers (services, state, components). Custom interfaces (`ArtistBubble`, `GuestFollow`) that duplicate Artist fields SHALL be removed. The `src/entities/artist.ts` file SHALL re-export the proto `Artist` type and provide helper functions for common field access patterns (e.g., best logo URL extraction).

The `entities/artist.ts` file SHALL export `bestLogoUrl(artist)` and `bestBackgroundUrl(artist)` as pure functions. Artist color derivation functions (`artistHue`, `artistColor`, `artistHueFromColorProfile`) SHALL NOT be placed in `entities/artist.ts` but in `adapter/view/artist-color.ts`, as they are presentation-layer concerns.

#### Scenario: Discovery service returns proto Artist
- **WHEN** `ArtistServiceClient.listTop()`, `search()`, or `listSimilar()` is called
- **THEN** the response SHALL return proto `Artist` objects directly, not mapped `ArtistBubble` interfaces

#### Scenario: Artist with fanart preserved through discovery
- **WHEN** an `Artist` proto is returned from ArtistService with `fanart.logoColorProfile` populated
- **THEN** the `logoColorProfile` data SHALL be preserved on the `Artist` object without being stripped

#### Scenario: Physics bubble composition
- **WHEN** the discovery dna-orb needs physics properties (`x`, `y`, `radius`) for an artist
- **THEN** it SHALL use a `PhysicsBubble` composition type `{ artist: Artist, x: number, y: number, radius: number }` instead of flattening artist fields into the physics type

#### Scenario: Color functions not in entity
- **WHEN** a component needs an artist color or hue
- **THEN** it SHALL import from `adapter/view/artist-color` not from `entities/artist`

### Requirement: Concert entity
The `src/entities/concert.ts` file SHALL export a `Concert` interface that includes an `artist?: Artist` field (proto type) instead of separate `logoUrl`, `backgroundUrl`, and `logoColorProfile` fields. Components SHALL extract display-specific values from the `Artist` object.

The `entities/concert.ts` file SHALL additionally export `isHypeMatched(hype, lane)`, `HypeLevel`, `LaneType`, and the ordering constants `HYPE_ORDER` and `LANE_ORDER` as pure domain logic alongside the type definitions.

#### Scenario: Concert with artist fanart
- **WHEN** a Concert is constructed from a proto concert and an artist map entry
- **THEN** `concert.artist` SHALL contain the full proto `Artist` with `fanart` (including `logoColorProfile` when available)

#### Scenario: Concert template accesses logo URL
- **WHEN** an event-card template needs the logo URL
- **THEN** it SHALL derive it from `concert.artist.fanart.hdMusicLogo?.value ?? concert.artist.fanart.musicLogo?.value`

#### Scenario: Hype matching imported from entity
- **WHEN** `dashboard-service.ts` needs to check hype matching
- **THEN** it SHALL import `isHypeMatched` from `entities/concert` not define it locally

### Requirement: FollowedArtist entity
The `src/entities/follow.ts` file SHALL export a `FollowedArtist` interface containing the proto `Artist` object and a `Hype` value. The interface SHALL NOT flatten artist fields (`id`, `name`, `logoUrl`) into top-level properties. Components that need specific artist fields SHALL access them via `followedArtist.artist.name?.value` or equivalent accessors.

The `entities/follow.ts` file SHALL additionally export a `hasFollow(follows, artistId)` pure function for deduplication checks. The `Hype` type and `FollowedArtist` interface SHALL remain in this file.

#### Scenario: FollowedArtist from ListFollowed RPC
- **WHEN** the follow service client receives a ListFollowed response
- **THEN** it SHALL map each proto `FollowedArtist` to `{ artist: Artist, hype: Hype }` preserving the full `Artist` object including `fanart`

#### Scenario: FollowedArtist during onboarding
- **WHEN** the follow service client is called during onboarding (`isOnboarding === true`)
- **THEN** it SHALL return `FollowedArtist` objects with the proto `Artist` from the guest state, including any `fanart` data that was available at follow time

#### Scenario: Duplicate follow check uses entity function
- **WHEN** the Redux reducer handles a `guest/follow` action
- **THEN** it SHALL call `hasFollow()` from `entities/follow` to check for duplicates instead of inlining the check
