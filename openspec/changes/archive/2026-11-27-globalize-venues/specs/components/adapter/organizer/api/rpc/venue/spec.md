## ADDED Requirements

### Requirement: ResolvePlace acts for the caller's own active Organizer

ResolvePlace SHALL pass the same organizer-console sign-in checks as Search and resolve the caller's own Organizer the same way; a failure of OrganizerUseCase.ResolveCaller SHALL be returned unchanged and neither the Venues nor the map catalog are read. ResolvePlace SHALL then call VenueUseCase.ResolvePlace with the place id and return its result: either the Venue that holds the place, with its name, admin area and time zone, or the place draft, with the place's name, country, suggested admin area and time zone when it has them.

#### Scenario: New place for an active Organizer

- **WHEN** a member of an active Organizer calls ResolvePlace with the place id of Gocheok Sky Dome, which no Venue holds
- **THEN** a place draft with the country KR, the suggested admin area KR-11 and the time zone Asia/Seoul is returned

#### Scenario: Place already a Venue

- **WHEN** a member of an active Organizer calls ResolvePlace with a place id a Venue holds
- **THEN** that Venue is returned with its name, admin area and time zone

#### Scenario: Picked place without an Organizer

- **WHEN** no Organizer is linked to the caller's Organization and the caller calls ResolvePlace
- **THEN** it fails with PermissionDenied and the map catalog is not called
