# Cancel

## Purpose

Cancel lets the owning organizer operator mark a concert (Series) 中止 (cancelled): it disappears from every fan surface, is kept rather than deleted, and can never be published again.

## Requirements

### Requirement: Only the owner

Cancel SHALL fail with PermissionDenied, without revealing whether the Series exists, when the Series does not exist or is not owned by the caller's Organizer.

#### Scenario: Unknown series
- **WHEN** no Series has the id
- **THEN** Cancel fails with PermissionDenied

### Requirement: Draft or published can be cancelled once

Cancel SHALL mark a DRAFT or PUBLISHED Series CANCELLED (Series.MarkCancelled), keeping its Events, and SHALL fail with FailedPrecondition when it is already CANCELLED.

#### Scenario: Cancel a published concert
- **WHEN** the owner cancels a PUBLISHED Series
- **THEN** it is CANCELLED and its Events are no longer publicly visible

#### Scenario: Cancel a draft
- **WHEN** the owner cancels a DRAFT Series
- **THEN** it is CANCELLED

#### Scenario: Cancel twice
- **WHEN** the owner cancels a CANCELLED Series
- **THEN** Cancel fails with FailedPrecondition

### Requirement: Cancellation is announced

After cancelling, Cancel SHALL announce the cancellation of the Series with the ids of its performances (Series.GetAuthored). A failure to read them or to announce SHALL NOT fail Cancel.

#### Scenario: Cancelled tour
- **WHEN** a PUBLISHED Series with three Events is cancelled
- **THEN** one cancellation carrying the three Event ids is announced
