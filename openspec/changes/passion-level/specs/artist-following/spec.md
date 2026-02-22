# Artist Following (Delta)

## New Requirements

### Requirement: Passion Level on Follow Relationship
The system SHALL associate a passion level with each followed artist, representing the user's enthusiasm tier.

#### Scenario: Default passion level on follow
- **WHEN** a user follows an artist via `ArtistService.Follow`
- **THEN** the `followed_artists` record SHALL be created with `passion_level` set to `local_only` by default
- **AND** the user SHALL NOT be required to specify a passion level at follow time

#### Scenario: Passion level persisted in database
- **WHEN** a follow record exists
- **THEN** the `followed_artists` table SHALL include a `passion_level` column of type `TEXT`
- **AND** valid values SHALL be: `must_go`, `local_only`, `keep_an_eye`

---

### Requirement: Followed Artist Response Enrichment
The system SHALL return passion level metadata alongside each followed artist in `ListFollowed` responses.

#### Scenario: ListFollowed includes passion level
- **WHEN** `ArtistService.ListFollowed` is called
- **THEN** each entry in the response SHALL include the artist entity AND their current passion level
- **AND** the response SHALL use a `FollowedArtist` wrapper message (not raw `Artist`)

#### Scenario: Backward compatibility
- **WHEN** the `ListFollowedResponse` schema changes from `repeated Artist` to `repeated FollowedArtist`
- **THEN** this SHALL be treated as a coordinated breaking change requiring simultaneous frontend and backend deployment
