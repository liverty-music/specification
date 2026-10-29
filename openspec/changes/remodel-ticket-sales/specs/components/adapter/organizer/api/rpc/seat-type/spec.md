# Spec Delta

## Purpose

The organizer-facing seat type service boundary (`SeatTypeService`): how a member's sign-in is turned into their own Organizer before a Series' seat types are created, deleted or listed.

## ADDED Requirements

### Requirement: Every call acts for the caller's own active Organizer

Create, Delete and ListBySeries SHALL pass the same organizer-console sign-in checks as the organizer Organizer service, and SHALL then resolve the caller's own Organizer through OrganizerUseCase.ResolveCaller with the caller's Organization. When the caller has no Organization, the call SHALL fail with PermissionDenied. A failure of ResolveCaller SHALL be returned unchanged and nothing else runs. Only then SHALL the boundary run, for the resolved Organizer, SeatTypeUseCase.Create, Delete or ListBySeries; errors from the usecase SHALL be returned unchanged. That the Series or seat type belongs to the caller's Organizer is a precondition of the usecase, not of the boundary.

#### Scenario: Member adds a seat type
- **WHEN** a member of an active Organizer calls Create for S席 at 8000 yen on their Series
- **THEN** SeatTypeUseCase.Create runs for their Organizer and the SeatType is returned

#### Scenario: Deactivated Organizer
- **WHEN** the caller's Organizer is deactivated
- **THEN** every call fails with FailedPrecondition and nothing changes

### Requirement: Calls name their values

Each call SHALL fail with InvalidArgument, before any usecase runs, when a value it needs is missing or malformed: Create, when no Series, name or price is given; Delete, when no SeatType is given; ListBySeries, when no Series is given.

#### Scenario: Missing price
- **WHEN** a member calls Create without a price
- **THEN** it fails with InvalidArgument and nothing is stored

#### Scenario: Delete without a seat type
- **WHEN** Delete is called without a SeatType
- **THEN** it fails with InvalidArgument and nothing changes
