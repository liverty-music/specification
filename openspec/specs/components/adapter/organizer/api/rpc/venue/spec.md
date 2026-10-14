# components/adapter/organizer/api/rpc/venue Specification

## Purpose
The organizer-facing Venue service boundary: an operator who is authoring a concert searches the map catalog for a venue, acting for their own Organizer.

## Requirements

### Requirement: Search acts for the caller's own active Organizer

Search SHALL pass the same organizer-console sign-in checks as the organizer Organizer service, and SHALL then resolve the caller's own Organizer through OrganizerUseCase.ResolveCaller with the caller's tenant. A failure of ResolveCaller SHALL be returned unchanged and the map catalog is not called: PermissionDenied when no Organizer is linked to the tenant or the Organizer is provisioning, without revealing whether an Organizer exists, and FailedPrecondition when the Organizer is deactivated. Search SHALL then call VenueUseCase.Search.

#### Scenario: Venue search for an active Organizer

- **WHEN** an operator of an active Organizer calls Search with "Zepp Haneda"
- **THEN** the candidate places are returned

#### Scenario: Venue search without an Organizer

- **WHEN** no Organizer is linked to the caller's tenant and the caller calls Search
- **THEN** it fails with PermissionDenied and the map catalog is not called
