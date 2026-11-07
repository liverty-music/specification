## MODIFIED Requirements

### Requirement: Stage values are closed

A ticket sale reminder's stage SHALL be one of `APPLY_OPEN` or `APPLY_CLOSE_24H`; any other value SHALL be invalid.

#### Scenario: Undefined stage
- **WHEN** a reminder carries a stage that is not one of the two defined stages
- **THEN** the reminder is invalid

#### Scenario: Result day stage
- **WHEN** a reminder carries the stage `RESULT_DAY`
- **THEN** the reminder is invalid

### Requirement: Stages by method

A reminder stage SHALL be anchored on exactly one milestone of the TicketSale, and only these stages SHALL apply, alike to a discovered sale and to an Organizer's sale:

- `APPLY_OPEN`: on a Lottery sale, at the start time. On a FirstCome sale, 30 minutes before the start time.
- `APPLY_CLOSE_24H`: on a Lottery sale only, 24 hours before the end time.

#### Scenario: Lottery stages
- **WHEN** a Lottery sale opens on 5 October 18:00 and closes on 22 October 23:59
- **THEN** `APPLY_OPEN` is anchored on 5 October 18:00 and `APPLY_CLOSE_24H` on 21 October 23:59

#### Scenario: First-come stage
- **WHEN** a FirstCome sale opens on 6 October 19:00
- **THEN** `APPLY_OPEN` is anchored on 6 October 18:30, and `APPLY_CLOSE_24H` does not apply

#### Scenario: Result day stage
- **WHEN** a discovered Lottery sale has the result date 3 November
- **THEN** no stage is anchored on 3 November

#### Scenario: Lottery without a result date
- **WHEN** a discovered Lottery sale has no result date, or the sale is an Organizer's lottery
- **THEN** only `APPLY_OPEN` and `APPLY_CLOSE_24H` apply
