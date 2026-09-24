<!-- spec: state-management | target: components/usecase/follow/follow | flags: CLASSNAME | new_name: Follow an artist -->

### Requirement: FollowServiceClient as follow state SSoT

The `FollowServiceClient` singleton SHALL own `followedArtists: Artist[]` as `@observable` state, serving as the single source of truth for followed artists across all pages. It SHALL expose `followedIds` (derived `ReadonlySet<string>`) and `followedCount` (derived `number`) getters. For guest users, mutations delegate to `GuestService` for localStorage persistence. For authenticated users, mutations call the backend RPC.

#### Scenario: Hydrate from guest state

- **WHEN** `FollowServiceClient` is asked to hydrate during onboarding
- **THEN** it SHALL set `followedArtists` from `GuestService.follows` mapped to `Artist[]`
- **AND** Aurelia templates bound to `followService.followedCount` SHALL update automatically

#### Scenario: Follow an artist (guest)

- **WHEN** `follow(artist)` is called and the user is not authenticated
- **THEN** the system SHALL optimistically append the artist to `followedArtists`
- **AND** the system SHALL call `GuestService.follow(artist)` for localStorage persistence
- **AND** `followedIds` and `followedCount` SHALL reflect the new state immediately

#### Scenario: Follow an artist (authenticated)

- **WHEN** `follow(artist)` is called and the user is authenticated
- **THEN** the system SHALL optimistically append the artist to `followedArtists`
- **AND** the system SHALL call the backend Follow RPC
- **AND** on RPC failure, the system SHALL rollback `followedArtists` to its previous state

#### Scenario: Duplicate follow is no-op

- **WHEN** `follow(artist)` is called with an artist whose `id` is already in `followedIds`
- **THEN** `followedArtists` SHALL remain unchanged

#### Scenario: followedIds derivation

- **WHEN** `followedIds` is accessed
- **THEN** it SHALL return a `ReadonlySet<string>` derived from current `followedArtists` IDs
