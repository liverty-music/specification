# Series.UpdateDraft

## Purpose

Replaces the authored content of a DRAFT Series: its title, type, source page, description, visibility, DraftEvents and draft performers.

## Requirements

### Requirement: Replace the draft whole

UpdateDraft SHALL replace the Series' title, type, source page, description and visibility and replace all of its DraftEvents and draft performers with the given ones, all together or none of them. Its cover image and organizer SHALL be unchanged.

#### Scenario: Event removed
- **WHEN** a draft with two DraftEvents is updated with one
- **THEN** the Series has only the one DraftEvent

### Requirement: Only a draft can be updated

UpdateDraft SHALL fail with FailedPrecondition, changing nothing, when the Series does not exist, is not first-party, or is not DRAFT.

#### Scenario: Published series
- **WHEN** a PUBLISHED Series is updated
- **THEN** UpdateDraft fails with FailedPrecondition
