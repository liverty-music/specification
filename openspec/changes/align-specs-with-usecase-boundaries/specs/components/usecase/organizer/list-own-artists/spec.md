# Spec Delta

## Purpose

OrganizerUseCase.ListOwnArtists returns the roster of the caller's own Organizer to its operators and refuses a request that names any other Organizer, so an operator never reads another Organizer's roster.

## ADDED Requirements

### Requirement: Only the caller's own roster is listed

ListOwnArtists SHALL take the caller's own Organizer, as OrganizerUseCase.ResolveCaller returned it, and the Organizer the request names. When the named Organizer is not the caller's own, ListOwnArtists SHALL fail with PermissionDenied and list nothing. Otherwise it SHALL return what OrganizerUseCase.ListArtists returns for the caller's own Organizer, including NotFound when that Organizer no longer exists.

#### Scenario: Own roster

- **WHEN** the request names the caller's own Organizer, which represents two Artists
- **THEN** ListOwnArtists returns the two Artists

#### Scenario: Another Organizer's roster

- **WHEN** the request names an Organizer that is not the caller's own
- **THEN** ListOwnArtists fails with PermissionDenied and nothing is listed

#### Scenario: Own Organizer gone

- **WHEN** the request names the caller's own Organizer and that Organizer no longer exists
- **THEN** ListOwnArtists fails with NotFound
