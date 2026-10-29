## REMOVED Requirements

### Requirement: SetStatus records the fan's status for the event
**Reason**: The current journey was read first only to tell whether the status changed, for the signal. TicketJourney.Upsert now tells that itself (components/entity/ticket-journey/upsert), so the read goes.
**Migration**: Replaced by "SetStatus records the fan's status". A failure to read the current journey can no longer fail SetStatus.

### Requirement: SetStatus reports each actual status change
**Reason**: TicketJourney.Upsert announces a status change together with the change, and only when the status changed (components/entity/ticket-journey/upsert), so the usecase no longer sends a signal.
**Migration**: Product analytics receives the "ticket journey status changed" signal from TicketJourney.Upsert's announcement, for changes only, which now includes the change to Paid made by TicketJourneyUseCase.MarkPaid. The previous status is not part of the signal: it is the status of the fan's previous signal for the event, or none. A failure to announce now fails SetStatus and leaves the journey unchanged.

## ADDED Requirements

### Requirement: SetStatus records the fan's status

When a fan sets a status for an event, SetStatus SHALL record the given status through TicketJourney.Upsert. It accepts any of the five journey statuses whatever the current status is. When TicketJourney.Upsert fails, SetStatus SHALL fail with that error.

#### Scenario: First status for an event

- **WHEN** the fan has no journey for the event and sets Tracking
- **THEN** the fan's journey for the event is recorded as Tracking

#### Scenario: Changing an existing status

- **WHEN** the fan's journey for the event is Applied and the fan sets Unpaid
- **THEN** the fan's journey for the event is recorded as Unpaid

#### Scenario: Recording the status fails

- **WHEN** TicketJourney.Upsert fails with Unavailable
- **THEN** SetStatus fails with Unavailable and the journey stays as it was
