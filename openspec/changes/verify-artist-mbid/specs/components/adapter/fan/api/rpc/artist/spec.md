## REMOVED Requirements

### Requirement: Browsing artists needs no sign-in
**Reason**: Create leaves the fan boundary: the fan app never calls it, and any signed-in fan could register an artist with an arbitrary MBID. Only the admin console registers artists, through the admin boundary.
**Migration**: See "Browsing artists needs no sign-in; listing needs it" below; Create is offered by the admin artist service (components/adapter/admin/api/rpc/artist).

### Requirement: Artist requests are validated at the boundary
**Reason**: Its Create rule moves to the admin boundary with Create.
**Migration**: See "Fan artist requests are validated at the boundary" below.

## ADDED Requirements

### Requirement: Browsing artists needs no sign-in; listing needs it

ListTop, ListSimilar and Search SHALL be callable without sign-in. List SHALL require a signed-in caller and SHALL fail with Unauthenticated, before any usecase runs, when the caller is not signed in. None of these calls acts for a particular fan, so no account is looked up.

#### Scenario: Guest searches

- **WHEN** a caller who is not signed in calls Search
- **THEN** ArtistUseCase.Search runs and its result is returned

#### Scenario: Guest lists artists

- **WHEN** a caller who is not signed in calls List
- **THEN** the call fails with Unauthenticated and no usecase runs

### Requirement: Fan artist requests are validated at the boundary
The boundary SHALL fail with InvalidArgument, before any usecase runs, when:
- Search has an empty query;
- ListSimilar has no artist id, an artist id that is not a UUID, or a limit outside 0 to 50;
- ListTop has a tag longer than 50 characters or a limit outside 0 to 100.

#### Scenario: Empty search query
- **WHEN** Search is called with an empty query
- **THEN** it fails with InvalidArgument and no catalog lookup is made

#### Scenario: Limit too large
- **WHEN** ListTop is called with a limit of 101
- **THEN** it fails with InvalidArgument

#### Scenario: Similar-artist limit too large
- **WHEN** ListSimilar is called with a limit of 51
- **THEN** it fails with InvalidArgument and no usecase runs
