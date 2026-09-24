# Update Draft

## Purpose

UpdateDraft lets the owning organizer operator replace the content of a DRAFT concert — title, type, source page, description, visibility, events and performers.

## Requirements

### Requirement: Only the owner

UpdateDraft SHALL fail with PermissionDenied, without revealing whether the Series exists, when the Series does not exist or is not owned by the caller's Organizer.

#### Scenario: Another organizer's series
- **WHEN** an operator updates a Series owned by another Organizer
- **THEN** UpdateDraft fails with PermissionDenied

#### Scenario: Unknown series
- **WHEN** no Series has the id
- **THEN** UpdateDraft fails with PermissionDenied

### Requirement: Only a draft

UpdateDraft SHALL fail with FailedPrecondition when the Series is CANCELLED or PUBLISHED.

#### Scenario: Published series
- **WHEN** the owner updates a PUBLISHED Series
- **THEN** UpdateDraft fails with FailedPrecondition and nothing changes

#### Scenario: Cancelled series
- **WHEN** the owner updates a CANCELLED Series
- **THEN** UpdateDraft fails with FailedPrecondition

### Requirement: Same validation as a new draft

UpdateDraft SHALL reject unrepresented performers with PermissionDenied and invalid input with InvalidArgument exactly as CreateDraft does, and SHALL find or create each event's Venue as CreateDraft does.

#### Scenario: Doors after start
- **WHEN** an updated event opens after it starts
- **THEN** UpdateDraft fails with InvalidArgument

### Requirement: Content replaced

UpdateDraft SHALL replace the draft's content (Series.UpdateDraft), keeping its id, Organizer and cover image, and return the updated Series with its DraftEvents and performers. Nothing SHALL be announced.

#### Scenario: Event removed
- **WHEN** a draft with two events is updated with one
- **THEN** the returned Series has one DraftEvent
