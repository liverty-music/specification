# Admin Artist RPC

## Purpose

The artist service as the admin console reaches it: the admin console uses Search to pick an artist to associate with an Organizer, through the same calls the fan boundary offers but only for admins.

## Requirements

### Requirement: Every artist call on the admin console needs the admin role

Every artist call reached through the admin console SHALL require a signed-in caller holding the admin role. A caller who is not signed in SHALL fail with Unauthenticated; a signed-in caller without the admin role SHALL fail with PermissionDenied. Both checks come before the request is validated and before any usecase runs. The browsing calls that the fan boundary serves without sign-in (ListTop, ListSimilar, Search) are not open here — the admin console requires sign-in and the admin role for every artist call, browsing included.

#### Scenario: Admin searches for an artist

- **WHEN** a signed-in admin calls Search with a query
- **THEN** ArtistUseCase.Search runs and the matching artists are returned

#### Scenario: Signed-in caller without the admin role

- **WHEN** a signed-in caller without the admin role calls Search
- **THEN** the call fails with PermissionDenied and no usecase runs

#### Scenario: Guest browses

- **WHEN** a caller who is not signed in calls ListTop
- **THEN** the call fails with Unauthenticated and no usecase runs

#### Scenario: Guest creates

- **WHEN** a caller who is not signed in calls Create
- **THEN** the call fails with Unauthenticated

### Requirement: Admin artist requests are validated as on the fan boundary

After the role check, the admin boundary SHALL validate each request of a call the fan artist boundary also serves by the same rules as the fan artist boundary, and fail with InvalidArgument on the same requests.

#### Scenario: Empty query

- **WHEN** an admin calls Search with an empty query
- **THEN** it fails with InvalidArgument

### Requirement: ListByOrganizer returns an Organizer's roster

ListByOrganizer, which only the admin console offers, SHALL take an OrganizerId and fail with InvalidArgument, before any usecase runs, when it is missing or malformed. It SHALL run ArtistUseCase.ListByOrganizer for the named Organizer, whatever its status, and return the Artists it returns; errors from the usecase SHALL be returned unchanged.

#### Scenario: Admin inspects a roster

- **WHEN** an admin calls ListByOrganizer for an Organizer that represents two Artists
- **THEN** the two Artists are returned

#### Scenario: Missing OrganizerId

- **WHEN** ListByOrganizer is called without an OrganizerId
- **THEN** it fails with InvalidArgument and no usecase runs

#### Scenario: Unknown Organizer

- **WHEN** ArtistUseCase.ListByOrganizer fails with NotFound
- **THEN** ListByOrganizer fails with NotFound

#### Scenario: Non-admin reads a roster

- **WHEN** a signed-in caller without the admin role calls ListByOrganizer
- **THEN** it fails with PermissionDenied and no usecase runs

### Requirement: Get returns one Artist

Get, which only the admin console offers, SHALL take an ArtistId and fail with InvalidArgument, before any usecase runs, when it is missing or malformed. It SHALL run ArtistUseCase.Get and return the Artist; errors from the usecase SHALL be returned unchanged.

#### Scenario: Admin reads an artist

- **WHEN** a signed-in admin calls Get with the id of a registered Artist
- **THEN** that Artist is returned with its name

#### Scenario: Missing ArtistId

- **WHEN** Get is called without an ArtistId
- **THEN** it fails with InvalidArgument and no usecase runs

#### Scenario: Unknown artist

- **WHEN** ArtistUseCase.Get fails with NotFound
- **THEN** Get fails with NotFound

#### Scenario: Non-admin reads an artist

- **WHEN** a signed-in caller without the admin role calls Get
- **THEN** it fails with PermissionDenied and no usecase runs
