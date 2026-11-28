# Spec Delta

## MODIFIED Requirements

### Requirement: Draft or published can be cancelled once

Cancel SHALL take a Series and, optionally, some of its Events, and act at the current time. When no Event is named it SHALL take every DRAFT Event and every PUBLISHED Event still cancellable of the Series (Series.GetAuthored), leaving out the PUBLISHED Events past their cancellation limit (24 hours after their start). It SHALL cancel them with Series.CancelEvents: a PUBLISHED Event becomes CANCELLED and is kept, a DRAFT Event is removed, and a Series left with no Event is removed. Cancel SHALL fail with FailedPrecondition when a named Event is already CANCELLED or is PUBLISHED and no longer cancellable, or when no Event is named and the Series has no DRAFT Event and no cancellable PUBLISHED Event.

#### Scenario: Cancel a published concert
- **WHEN** the owner cancels a Series whose Events are PUBLISHED and in the future
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

#### Scenario: Rest of a tour
- **WHEN** the owner cancels, without naming Events, a Series with one PUBLISHED Event held last week and two in the future
- **THEN** the two future Events are CANCELLED and the held one stays PUBLISHED

#### Scenario: Held concert named
- **WHEN** the owner names a PUBLISHED Event that started 30 hours ago
- **THEN** Cancel fails with FailedPrecondition and nothing changes
