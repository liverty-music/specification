## ADDED Requirements

### Requirement: Each stage is anchored on one milestone

A reminder stage SHALL be anchored on exactly one milestone of the TicketSale, and only these stages SHALL apply, alike to a discovered sale and to an Organizer's sale:

- `APPLY_OPEN`: on a Lottery sale, at the start time. On a FirstCome sale, 30 minutes before the start time.
- `APPLY_CLOSE_24H`: on a Lottery sale only, 24 hours before the end time.

#### Scenario: Lottery stages
- **WHEN** a Lottery sale opens on 5 October 18:00 and closes on 22 October 23:59
- **THEN** `APPLY_OPEN` is anchored on 5 October 18:00 and `APPLY_CLOSE_24H` on 21 October 23:59

#### Scenario: First-come stage
- **WHEN** a FirstCome sale opens on 6 October 19:00
- **THEN** `APPLY_OPEN` is anchored on 6 October 18:30, and `APPLY_CLOSE_24H` does not apply

#### Scenario: Result date anchors nothing
- **WHEN** a discovered Lottery sale has the result date 3 November
- **THEN** no stage is anchored on 3 November

#### Scenario: Organizer's lottery
- **WHEN** the sale is an Organizer's lottery
- **THEN** only `APPLY_OPEN` and `APPLY_CLOSE_24H` apply

## MODIFIED Requirements

### Requirement: Stage values are closed

A ticket sale reminder's stage SHALL be one of `APPLY_OPEN` or `APPLY_CLOSE_24H`; any other value SHALL be invalid.

#### Scenario: Undefined stage
- **WHEN** a reminder carries a stage that is not one of the two defined stages
- **THEN** the reminder is invalid

#### Scenario: Result day stage
- **WHEN** a reminder carries the stage `RESULT_DAY`
- **THEN** the reminder is invalid

## REMOVED Requirements

### Requirement: Stages by method
**Reason**: Replaced by "Each stage is anchored on one milestone", which states the behavior without the scenarios of the removed behavior.
**Migration**: None.
