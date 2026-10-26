## ADDED Requirements

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
