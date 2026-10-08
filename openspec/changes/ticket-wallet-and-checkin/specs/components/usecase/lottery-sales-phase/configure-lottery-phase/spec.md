# Spec Delta

## MODIFIED Requirements

### Requirement: Configure a phase for a published event

ConfigureLotteryPhase SHALL take an event, an open time, a close time, a ticket capacity, a max tickets per application, a ticket price and an optional verification requirement. It SHALL fail with InvalidArgument when the event is not given, when the open or close time is missing, or when the values break the LotterySalesPhase rules for the window, capacity, group size or price. It SHALL then check the event with Event.IsEventPublished, requiring it to exist, failing with NotFound otherwise, and its series to be published, failing with FailedPrecondition when the series is draft or cancelled. It SHALL read the event with Event.Get and fail with FailedPrecondition when the event has no start time, because a ticket names it on its face and venue reception opens from it when the event's doors-open time is not announced; the event's doors-open time stays optional. It SHALL create the phase with LotterySalesPhase.Create, with the verification requirement None when none is given, and return it.

#### Scenario: Organizer configures a phase

- **WHEN** an Organizer configures a 10-day window, capacity 100, 4 tickets per application and 8000 yen per ticket for a published event that starts at 19:00
- **THEN** the phase is created, not drawn, with the requirement None, and returned

#### Scenario: Event not published

- **WHEN** the event's series is still draft
- **THEN** ConfigureLotteryPhase fails with FailedPrecondition and creates nothing

#### Scenario: Start time not yet announced

- **WHEN** the published event has a date but no start time
- **THEN** ConfigureLotteryPhase fails with FailedPrecondition and creates nothing

#### Scenario: Doors-open time not announced

- **WHEN** the published event starts at 19:00 and has no doors-open time
- **THEN** the phase is created

#### Scenario: Unknown event

- **WHEN** the event does not exist
- **THEN** ConfigureLotteryPhase fails with NotFound

#### Scenario: Invalid configuration

- **WHEN** the window lasts 15 days, or the group size exceeds the capacity, or the price is 0
- **THEN** ConfigureLotteryPhase fails with InvalidArgument and creates nothing
