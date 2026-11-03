# components/usecase/ticket-journey/infer-tracking Specification

## Purpose
TicketJourneyUseCase.InferTracking starts tracking an event for a fan whose own action in the app, adding the event's concert to their calendar, shows interest in it, without replacing any journey that already exists.

## Requirements

### Requirement: InferTracking records Tracking only when the fan has no journey

When the fan adds an event's concert to their calendar, InferTracking SHALL store a journey for the fan and the event with status Tracking, set by inference, through TicketJourney.UpsertIfReplaceable, which stores it only when the fan has no journey for the event, and report whether tracking started. When the fan already has a journey, InferTracking SHALL succeed, change nothing and report that tracking did not start. InferTracking SHALL never raise a hype level. Failures of UpsertIfReplaceable SHALL be returned unchanged.

#### Scenario: No journey yet

- **WHEN** the fan has no journey for the event and InferTracking runs
- **THEN** the fan's journey for the event is Tracking set by inference and InferTracking reports that tracking started

#### Scenario: A journey exists

- **WHEN** the fan's journey for the event is Applied set by the fan and InferTracking runs
- **THEN** the journey stays Applied set by the fan and InferTracking reports that tracking did not start

#### Scenario: After the fan removed an inferred journey

- **WHEN** the fan removed the journey that InferTracking had started and InferTracking runs again for the event
- **THEN** the fan's journey for the event is Tracking set by inference again

#### Scenario: Unknown event

- **WHEN** InferTracking runs for an event that does not exist
- **THEN** it fails with FailedPrecondition
