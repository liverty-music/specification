# Spec Delta

## MODIFIED Requirements

### Requirement: Requests are validated before any usecase runs

The boundary SHALL fail with InvalidArgument, before any usecase runs, when a required OrganizerId or ArtistId is missing or malformed, when Create's name is not 1 to 200 characters, or when Create's operator email is not an email address.

#### Scenario: Name too long

- **WHEN** Create is called with a 201-character name
- **THEN** it fails with InvalidArgument and no Organizer is created

#### Scenario: Malformed operator email

- **WHEN** Create is called with an operator email that is not an email address
- **THEN** it fails with InvalidArgument

#### Scenario: Missing OrganizerId

- **WHEN** Get, ListArtists, AssociateArtist, DisassociateArtist, Deactivate or Delete is called without an OrganizerId
- **THEN** it fails with InvalidArgument

### Requirement: Each call runs one OrganizerUseCase method

Create SHALL run OrganizerUseCase.Create and return the created Organizer; Get, List and ListArtists SHALL run OrganizerUseCase.Get, OrganizerUseCase.List and OrganizerUseCase.ListArtists for any Organizer the admin names; AssociateArtist, DisassociateArtist, Deactivate and Delete SHALL run the usecase method of the same name. Errors from the usecase SHALL be returned unchanged. An Organizer is returned with its id and name only.

#### Scenario: Admin lists Organizers and inspects a roster

- **WHEN** an admin lists Organizers and then requests one Organizer's Artists
- **THEN** it returns every Organizer, and then the Artists that Organizer represents

#### Scenario: Admin reads any Organizer

- **WHEN** an admin calls Get for a deactivated Organizer
- **THEN** it returns that Organizer's id and name

#### Scenario: Admin deletes a deactivated Organizer

- **WHEN** an admin calls Delete for a deactivated Organizer
- **THEN** OrganizerUseCase.Delete runs and the call succeeds with an empty response

#### Scenario: Delete refused

- **WHEN** OrganizerUseCase.Delete fails with FailedPrecondition
- **THEN** Delete fails with FailedPrecondition
