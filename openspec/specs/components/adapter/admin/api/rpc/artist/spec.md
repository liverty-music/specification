# Admin Artist RPC

## Purpose

The artist service as the admin console reaches it: the admin console uses Search to pick an artist to associate with an Organizer, through the same calls the fan boundary offers but only for admins.

## Requirements

### Requirement: Every artist call on the admin console needs the admin role

Every artist call reached through the admin console SHALL require a signed-in caller holding the admin role, and SHALL fail with PermissionDenied otherwise. The one exception is List, Create, CreateOfficialSite and DeleteOfficialSite without any sign-in, which fail with Unauthenticated as on the fan boundary. These checks come before the request is validated and before any usecase runs. The browsing calls that the fan boundary serves without sign-in (ListTop, ListSimilar, Search) are not open here.

#### Scenario: Admin searches for an artist

- **WHEN** a signed-in admin calls Search with a query
- **THEN** ArtistUseCase.Search runs and the matching artists are returned

#### Scenario: Signed-in caller without the admin role

- **WHEN** a signed-in caller without the admin role calls Search
- **THEN** the call fails with PermissionDenied and no usecase runs

#### Scenario: Guest browses

- **WHEN** a caller who is not signed in calls ListTop
- **THEN** the call fails with PermissionDenied and no usecase runs

#### Scenario: Guest creates

- **WHEN** a caller who is not signed in calls Create
- **THEN** the call fails with Unauthenticated

### Requirement: Admin artist requests are validated as on the fan boundary

After the role check, the admin boundary SHALL validate each request by the same rules as the fan artist boundary and fail with InvalidArgument on the same requests.

#### Scenario: Empty query

- **WHEN** an admin calls Search with an empty query
- **THEN** it fails with InvalidArgument
