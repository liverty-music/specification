# Spec Delta

## ADDED Requirements

### Requirement: Stages are anchored by method

A reminder stage SHALL be anchored on exactly one milestone of the sales phase, and only these stages SHALL apply:

- `APPLY_OPEN`: on a `LOTTERY` phase, at the apply start time. On a `FIRST_COME` phase, 30 minutes before the apply start time.
- `APPLY_CLOSE_24H`: on a `LOTTERY` phase only, 24 hours before the apply end time.
- `RESULT_DAY`: on a `LOTTERY` phase with a lottery result time only, on the calendar day of that time.

#### Scenario: Lottery stages

- **WHEN** a `LOTTERY` phase opens on 5 October 18:00, closes on 22 October 23:59 and announces results on 3 November 15:00
- **THEN** `APPLY_OPEN` is anchored on 5 October 18:00, `APPLY_CLOSE_24H` on 21 October 23:59 and `RESULT_DAY` on 3 November

#### Scenario: First-come stage

- **WHEN** a `FIRST_COME` phase opens on 6 October 19:00
- **THEN** `APPLY_OPEN` is anchored on 6 October 18:30, and neither `APPLY_CLOSE_24H` nor `RESULT_DAY` applies

#### Scenario: Lottery without a result time

- **WHEN** a `LOTTERY` phase has no lottery result time
- **THEN** `RESULT_DAY` does not apply to that phase

## MODIFIED Requirements

### Requirement: Stage values are closed

A sales phase reminder's stage SHALL be one of `APPLY_OPEN`, `APPLY_CLOSE_24H` or `RESULT_DAY`; any other value SHALL be invalid.

#### Scenario: Undefined stage

- **WHEN** a reminder carries a stage that is not one of the three defined stages
- **THEN** the reminder is invalid

## REMOVED Requirements

### Requirement: Each stage is anchored on one milestone of its sales phase

**Reason**: The stages now depend on the method; `APPLY_CLOSE_1H` and the payment deadline are gone.
**Migration**: Replaced by "Stages are anchored by method".
