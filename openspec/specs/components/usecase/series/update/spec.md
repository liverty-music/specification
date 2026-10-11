# Update

## Purpose

Update lets the owning organizer operator replace the content of a DRAFT concert — title, type, source page, description, visibility, events and performers.

## Requirements

### Requirement: Only the owner

Update SHALL fail with PermissionDenied, without revealing whether the Series exists, when the Series does not exist or is not owned by the caller's Organizer.

#### Scenario: Another organizer's series
- **WHEN** an operator updates a Series owned by another Organizer
- **THEN** Update fails with PermissionDenied

#### Scenario: Unknown series
- **WHEN** no Series has the id
- **THEN** Update fails with PermissionDenied

### Requirement: Only a draft

Update SHALL fail with FailedPrecondition when the Series is CANCELLED or PUBLISHED.

#### Scenario: Published series
- **WHEN** the owner updates a PUBLISHED Series
- **THEN** Update fails with FailedPrecondition and nothing changes

#### Scenario: Cancelled series
- **WHEN** the owner updates a CANCELLED Series
- **THEN** Update fails with FailedPrecondition

### Requirement: Same validation as a new draft

Update SHALL reject unrepresented performers with PermissionDenied and invalid input with InvalidArgument exactly as Create does, and SHALL find or create each event's Venue as Create does.

#### Scenario: Doors after start
- **WHEN** an updated event opens after it starts
- **THEN** Update fails with InvalidArgument

### Requirement: Content replaced

Update SHALL replace the draft's content (Series.UpdateDraft), keeping its id, Organizer and cover image, and return the updated Series with its DraftEvents and performers. Nothing SHALL be announced.

#### Scenario: Event removed
- **WHEN** a draft with two events is updated with one
- **THEN** the returned Series has one DraftEvent
