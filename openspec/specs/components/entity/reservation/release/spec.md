# components/entity/reservation/release Specification

## Purpose
Ends a Held Reservation whose hold has lapsed, so its tickets go back on sale.

## Requirements

### Requirement: Release ends only a lapsed Held reservation

Release SHALL take a Reservation and a time, and make it Expired only when it is still Held and its hold expired at or before that time. Checking and changing SHALL be one indivisible step, so a Reservation committed meanwhile is left Committed. A Reservation in any other status, or still holding, SHALL be left unchanged. Release SHALL report whether it changed the Reservation, and SHALL fail with NotFound when no Reservation has the id.

#### Scenario: Hold lapsed

- **WHEN** a Held Reservation expiring at 18:15 is released at 18:16
- **THEN** it is Expired and Release reports a change

#### Scenario: Still holding

- **WHEN** a Held Reservation expiring at 18:15 is released at 18:14
- **THEN** nothing changes

#### Scenario: Committed just before the sweep

- **WHEN** a Reservation was committed at 18:14 and is released at 18:16
- **THEN** it stays Committed and Release reports no change

#### Scenario: Paid checkout

- **WHEN** a Completed Reservation is released
- **THEN** nothing changes
