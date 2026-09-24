# Set Status

## Purpose

Records a fan's ticket journey status for one event at the fan's request, creating the journey or replacing its status, and reports every actual status change for product analytics.

## Requirements

### Requirement: SetStatus records the fan's status for the event

When a fan sets a status for an event, SetStatus SHALL first read the fan's current journey for the event through TicketJourney.Get, treating NotFound as "no journey yet", and SHALL then record the given status through TicketJourney.Upsert. It accepts any of the five journey statuses whatever the current status is. When the read fails with any error other than NotFound, SetStatus SHALL fail with that error and record nothing. When the write fails, SetStatus SHALL fail with that error.

#### Scenario: First status for an event

- **WHEN** the fan has no journey for the event and sets Tracking
- **THEN** the fan's journey for the event is recorded as Tracking

#### Scenario: Changing an existing status

- **WHEN** the fan's journey for the event is Applied and the fan sets Unpaid
- **THEN** the fan's journey for the event is recorded as Unpaid

#### Scenario: Reading the current journey fails

- **WHEN** reading the fan's current journey fails with an error other than NotFound
- **THEN** SetStatus fails with that error and nothing is recorded

#### Scenario: Recording the status fails

- **WHEN** TicketJourney.Upsert fails
- **THEN** SetStatus fails with that error and no status-change signal is sent

### Requirement: SetStatus reports each actual status change

After the status is recorded, SetStatus SHALL send a "ticket journey status changed" signal for product analytics carrying the fan, the event, the previous status ("none" when the fan had no journey) and the new status. It SHALL send no signal when the new status equals the recorded one. A failure to send the signal SHALL NOT fail SetStatus and SHALL NOT undo the recorded status.

#### Scenario: First status sends a signal from none

- **WHEN** the fan has no journey for the event and sets Tracking
- **THEN** a signal is sent with previous status none and new status Tracking

#### Scenario: A real change sends a signal

- **WHEN** the fan's journey is Applied and the fan sets Lost
- **THEN** a signal is sent with previous status Applied and new status Lost

#### Scenario: Setting the same status sends nothing

- **WHEN** the fan's journey is Paid and the fan sets Paid
- **THEN** SetStatus succeeds and no signal is sent

#### Scenario: Sending the signal fails

- **WHEN** the status is recorded but the signal cannot be sent
- **THEN** SetStatus still succeeds and the new status stays recorded
