## ADDED Requirements

### Requirement: Ticket sales require complete event info

The system SHALL only accept ticket sales — primary and resale — for an event
whose **mandatory event information, including `start_time`, is set**. Because the
resale deadline is derived as `start_time − 1h`, an event missing `start_time`
MUST NOT be sellable/resellable (the deadline is otherwise uncomputable).

#### Scenario: Event missing start_time is not sellable

- **WHEN** an event is published without its mandatory info (e.g. no `start_time`)
- **THEN** the system does not accept ticket sales or resale listings for it until the required info is set
