## ADDED Requirements

### Requirement: ListByArtist returns one artist's concerts

ListByArtist SHALL take an ArtistId and fail with InvalidArgument, before any usecase runs, when it is missing or malformed. It SHALL run ConcertUseCase.ListCatalogByArtist and return the Concerts with each Series and Artist they refer to once, as List does.

#### Scenario: Admin lists one artist's concerts

- **WHEN** a signed-in admin calls ListByArtist with the id of an Artist who performs in one CANCELLED Concert
- **THEN** only that Concert is returned, with its Series and its Artists

#### Scenario: Malformed artist id

- **WHEN** an admin calls ListByArtist with an Artist id that is not a UUID
- **THEN** it fails with InvalidArgument and nothing is read

#### Scenario: Missing artist id

- **WHEN** an admin calls ListByArtist without an Artist id
- **THEN** it fails with InvalidArgument and nothing is read

#### Scenario: Non-admin lists an artist's concerts

- **WHEN** a signed-in caller without the admin role calls ListByArtist
- **THEN** it fails with PermissionDenied and nothing is read
