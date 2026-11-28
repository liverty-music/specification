## ADDED Requirements

### Requirement: ListByMbidStatus lists the artists in one MBID status

ListByMbidStatus, which only the admin console offers, SHALL take an mbid_status and fail with InvalidArgument, before any usecase runs, when it is missing or unspecified. It SHALL run ArtistUseCase.ListByMBIDStatus and return the Artists it returns, each with its name and MBID; errors from the usecase SHALL be returned unchanged.

#### Scenario: Admin lists the ambiguous artists

- **WHEN** a signed-in admin calls ListByMbidStatus with Ambiguous while two artists are Ambiguous
- **THEN** the two Artists are returned with their names and MBIDs

#### Scenario: Missing status

- **WHEN** ListByMbidStatus is called without an mbid_status
- **THEN** it fails with InvalidArgument and no usecase runs

#### Scenario: Non-admin lists artists by status

- **WHEN** a signed-in caller without the admin role calls ListByMbidStatus
- **THEN** it fails with PermissionDenied and no usecase runs

### Requirement: CorrectMbid sets the MBID an admin chose

CorrectMbid, which only the admin console offers, SHALL take an ArtistId and an MBID and fail with InvalidArgument, before any usecase runs, when either is missing or malformed. It SHALL run ArtistUseCase.CorrectMBID and return the corrected Artist; errors from the usecase SHALL be returned unchanged.

#### Scenario: Admin chooses a namesake

- **WHEN** a signed-in admin calls CorrectMbid for an Ambiguous artist with the MBID of one of its namesakes
- **THEN** the Artist is returned with that MBID and the catalog's name

#### Scenario: MBID of another artist

- **WHEN** ArtistUseCase.CorrectMBID fails with AlreadyExists
- **THEN** CorrectMbid fails with AlreadyExists

#### Scenario: Malformed MBID

- **WHEN** CorrectMbid is called with an MBID that is not 36 characters long
- **THEN** it fails with InvalidArgument and no usecase runs

#### Scenario: Non-admin corrects an MBID

- **WHEN** a signed-in caller without the admin role calls CorrectMbid
- **THEN** it fails with PermissionDenied and no usecase runs

### Requirement: Create registers an artist an admin names

Create on the admin artist service SHALL take a name and an MBID and fail with InvalidArgument, before any usecase runs, when the name is missing or empty or the MBID is not a UUID. It SHALL run ArtistUseCase.Create and return the registered Artist; errors from the usecase SHALL be returned unchanged. It is the only way to register an artist directly; the fan boundary does not offer it.

#### Scenario: Admin registers a test artist

- **WHEN** a signed-in admin calls Create with the name "E2E Test Artist" and a generated MBID
- **THEN** ArtistUseCase.Create runs and the registered Artist is returned

#### Scenario: Malformed MBID

- **WHEN** Create is called with an MBID that is not a UUID
- **THEN** it fails with InvalidArgument and no artist is created

#### Scenario: Non-admin registers an artist

- **WHEN** a signed-in caller without the admin role calls Create
- **THEN** it fails with PermissionDenied and no usecase runs
