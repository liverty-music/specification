# Spec Delta

## MODIFIED Requirements

### Requirement: Draft or published can be cancelled once

Cancel SHALL take a Series and, optionally, some of its Events; when no Event is named it SHALL take every PUBLISHED and DRAFT Event of the Series (Series.GetAuthored). It SHALL cancel them with Series.CancelEvents: a PUBLISHED Event becomes CANCELLED and is kept, a DRAFT Event is removed, and a Series left with no Event is removed. Cancel SHALL fail with FailedPrecondition when a named Event is already CANCELLED, or when no Event is named and the Series has no PUBLISHED or DRAFT Event.

#### Scenario: Cancel a published concert
- **WHEN** the owner cancels a Series whose Events are PUBLISHED
- **THEN** every Event is CANCELLED and no longer publicly visible

#### Scenario: Cancel a draft
- **WHEN** the owner cancels a Series whose Events are all DRAFT
- **THEN** the Events and the Series are removed

#### Scenario: Cancel twice
- **WHEN** the owner cancels a Series whose Events are all CANCELLED
- **THEN** Cancel fails with FailedPrecondition

#### Scenario: Cancel one date
- **WHEN** the owner names one of three PUBLISHED Events of a Series
- **THEN** that Event is CANCELLED and the other two stay PUBLISHED and visible

### Requirement: Cancellation is announced

After cancelling, Cancel SHALL announce the cancellation of the Series with the ids of the Events that became CANCELLED, and SHALL announce nothing when none did. A failure to announce SHALL NOT fail Cancel.

#### Scenario: Cancelled tour
- **WHEN** a Series with three PUBLISHED Events is cancelled
- **THEN** one cancellation carrying the three Event ids is announced

#### Scenario: Draft discarded silently
- **WHEN** a Series whose Events are all DRAFT is cancelled
- **THEN** no cancellation is announced
