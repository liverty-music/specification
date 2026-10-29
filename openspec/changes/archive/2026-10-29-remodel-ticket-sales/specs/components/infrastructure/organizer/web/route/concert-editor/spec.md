# Spec Delta

## ADDED Requirements

### Requirement: Each date's per-account limit

The editor SHALL show, for each event, 1アカウントの上限 (per-account limit): the most tickets one account may hold for that date across every sale, seat type and official resale, as a whole number from 1 to 10, starting at 4 for a new date. A value outside 1 to 10 SHALL be shown as an error next to the field, and nothing is saved. Once the event is PUBLISHED, the limit SHALL be shown read-only, with the note that it is fixed once the date is published, and saving SHALL leave it as it is.

#### Scenario: New date
- **WHEN** a member adds a date to a concert
- **THEN** its 1アカウントの上限 is 4

#### Scenario: Group tickets
- **WHEN** a member sets 1アカウントの上限 to 6 for a DRAFT date and saves
- **THEN** the date's per-account limit is 6

#### Scenario: Above one admission code
- **WHEN** a member enters 11
- **THEN** an error is shown next to the field and nothing is saved

#### Scenario: Published date
- **WHEN** the date is PUBLISHED
- **THEN** its 1アカウントの上限 is shown read-only with the note that it is fixed once the date is published
