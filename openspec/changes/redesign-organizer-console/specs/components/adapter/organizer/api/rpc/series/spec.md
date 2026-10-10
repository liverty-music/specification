# Spec Delta

## MODIFIED Requirements

### Requirement: Every authoring call acts for the caller's own active Organizer

Every call of the organizer Series service — Create, Update, Publish, Cancel, List, RegenerateToken, CreateMediaUploadURL, AttachMedia and SearchVenues — SHALL pass the same organizer-console sign-in checks as the organizer Organizer service, and SHALL then resolve the caller's own Organizer through OrganizerUseCase.ResolveCaller with the caller's tenant. A failure of ResolveCaller SHALL be returned unchanged and nothing is stored: PermissionDenied when no Organizer is linked to the tenant or the Organizer is provisioning, without revealing whether an Organizer exists, and FailedPrecondition when the Organizer is deactivated. Ownership of the Series named in a request is checked by the usecase, not here. SearchVenues SHALL then call ConcertAuthoringUseCase.SearchPlaces.

#### Scenario: Operator of an active Organizer lists concerts

- **WHEN** an operator of an active Organizer calls List
- **THEN** the Organizer's own concerts are returned

#### Scenario: Provisioning Organizer

- **WHEN** the caller's Organizer is provisioning
- **THEN** every authoring call fails with PermissionDenied and nothing is stored

#### Scenario: Deactivated Organizer

- **WHEN** the caller's Organizer is deactivated
- **THEN** every authoring call fails with FailedPrecondition

#### Scenario: Venue search for an active Organizer

- **WHEN** an operator of an active Organizer calls SearchVenues with "Zepp Haneda"
- **THEN** the candidate places are returned

#### Scenario: Venue search without an Organizer

- **WHEN** no Organizer is linked to the caller's tenant and the caller calls SearchVenues
- **THEN** it fails with PermissionDenied and the map catalog is not called
