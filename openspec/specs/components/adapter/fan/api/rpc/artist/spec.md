# Artist RPC

## Purpose

The fan-facing artist service boundary: which artist calls need a signed-in caller, and which requests the boundary rejects before ArtistUseCase runs.

## Requirements

### Requirement: Browsing artists needs no sign-in

ListTop, ListSimilar and Search SHALL be callable without sign-in. List, Create, CreateOfficialSite and DeleteOfficialSite SHALL require a signed-in caller and SHALL fail with Unauthenticated, before any usecase runs, when the caller is not signed in. None of these calls acts for a particular fan, so no account is looked up.

#### Scenario: Guest searches

- **WHEN** a caller who is not signed in calls Search
- **THEN** ArtistUseCase.Search runs and its result is returned

#### Scenario: Guest creates an artist

- **WHEN** a caller who is not signed in calls Create
- **THEN** the call fails with Unauthenticated and no usecase runs

### Requirement: Artist requests are validated at the boundary

The boundary SHALL fail with InvalidArgument, before any usecase runs, when:
- Create has no name, an empty name, or an MBID that is not a UUID;
- Search has an empty query;
- ListSimilar has no artist id, an artist id that is not a UUID, or a limit outside 0 to 100;
- ListTop has a tag longer than 50 characters or a limit outside 0 to 100;
- CreateOfficialSite has no artist id, an artist id that is not a UUID, or a URL that is not a valid URI of 1 to 2048 characters.

#### Scenario: Empty search query

- **WHEN** Search is called with an empty query
- **THEN** it fails with InvalidArgument and no catalog lookup is made

#### Scenario: Limit too large

- **WHEN** ListTop is called with a limit of 101
- **THEN** it fails with InvalidArgument

#### Scenario: Malformed MBID

- **WHEN** Create is called with an MBID that is not a UUID
- **THEN** it fails with InvalidArgument and no artist is created

### Requirement: Official sites are created through the boundary but never deleted

CreateOfficialSite SHALL hand the artist id and URL to ArtistUseCase.CreateOfficialSite. DeleteOfficialSite SHALL fail with Unimplemented for every signed-in caller; there is no usecase behind it.

Known defect: liverty-music/backend#470

#### Scenario: Create a site

- **WHEN** a signed-in caller calls CreateOfficialSite for an artist without a site with a valid URL
- **THEN** the site is stored for the artist

#### Scenario: Delete a site

- **WHEN** a signed-in caller calls DeleteOfficialSite
- **THEN** it fails with Unimplemented and nothing changes
