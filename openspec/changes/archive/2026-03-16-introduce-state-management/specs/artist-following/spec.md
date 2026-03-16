## MODIFIED Requirements

### Requirement: Follow Relationship Data Model

The system SHALL maintain a follow relationship between users and artists, stored in the followed_artists table. The use case layer SHALL resolve the authenticated user's external identity (Zitadel `sub` claim) to the internal user UUID before querying or writing to the `followed_artists` table.

For guest users during onboarding, follow state SHALL be managed via Store dispatch (`guest/follow`, `guest/unfollow`) instead of direct localStorage manipulation. The `ILocalArtistClient` service SHALL be removed and replaced by Store state access via `store.getState().guestArtists.follows`.

#### Scenario: Passion level stored on follow relationship

- **GIVEN** the followed_artists table
- **WHEN** a follow relationship exists
- **THEN** a passion_level column SHALL store the user's enthusiasm tier (must_go, local_only, keep_an_eye) with a default of local_only

#### Scenario: Successfully following an artist

- **WHEN** a user with a valid Zitadel identity requests to follow an artist with a valid MBID
- **THEN** the system SHALL resolve the Zitadel `sub` claim to the internal user UUID via `UserRepository.GetByExternalID`
- **AND** the system SHALL create a record in the `followed_artists` table linking the internal user UUID to the artist

#### Scenario: User record not found during follow

- **WHEN** `Follow` is called with a valid Zitadel identity but no corresponding user record exists
- **THEN** the system SHALL return `NOT_FOUND` error indicating the user must complete registration first

#### Scenario: Guest user follows an artist during onboarding

- **WHEN** a guest user follows an artist during the onboarding tutorial
- **THEN** the frontend SHALL dispatch `{ type: 'guest/follow', artistId, name }` to the Store
- **AND** the Store's persistence middleware SHALL write the updated follows to localStorage
- **AND** the system SHALL NOT call any backend RPC

#### Scenario: Guest user unfollows an artist during onboarding

- **WHEN** a guest user unfollows an artist during the onboarding tutorial
- **THEN** the frontend SHALL dispatch `{ type: 'guest/unfollow', artistId }` to the Store
- **AND** the Store's persistence middleware SHALL update localStorage accordingly

#### Scenario: Guest follow count is reactive

- **WHEN** the Store's `guestArtists.follows` array changes via dispatch
- **THEN** any component reading `store.getState().guestArtists.follows.length` SHALL reflect the updated count
