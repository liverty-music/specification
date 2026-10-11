# Spec Delta

## MODIFIED Requirements

### Requirement: Admin artist requests are validated as on the fan boundary

After the role check, the admin boundary SHALL validate each request of a call the fan artist boundary also serves by the same rules as the fan artist boundary, and fail with InvalidArgument on the same requests.

#### Scenario: Empty query

- **WHEN** an admin calls Search with an empty query
- **THEN** it fails with InvalidArgument

## ADDED Requirements

### Requirement: ListByOrganizer returns an Organizer's roster

ListByOrganizer, which only the admin console offers, SHALL take an OrganizerId and fail with InvalidArgument, before any usecase runs, when it is missing or malformed. It SHALL run OrganizerUseCase.ListArtists for the named Organizer, whatever its status, and return the Artists it returns; errors from the usecase SHALL be returned unchanged.

#### Scenario: Admin inspects a roster

- **WHEN** an admin calls ListByOrganizer for an Organizer that represents two Artists
- **THEN** the two Artists are returned

#### Scenario: Missing OrganizerId

- **WHEN** ListByOrganizer is called without an OrganizerId
- **THEN** it fails with InvalidArgument and no usecase runs

#### Scenario: Unknown Organizer

- **WHEN** OrganizerUseCase.ListArtists fails with NotFound
- **THEN** ListByOrganizer fails with NotFound

#### Scenario: Non-admin reads a roster

- **WHEN** a signed-in caller without the admin role calls ListByOrganizer
- **THEN** it fails with PermissionDenied and no usecase runs
