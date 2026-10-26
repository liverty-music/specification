## Purpose

Records the outcome of one TicketType's draw: each admitted entry Won and each other entry Lost, every one with its draw position, once.

## ADDED Requirements

### Requirement: One ticket type's outcome is recorded together and once

RecordDrawOutcome SHALL take a TicketType, the entries the draw admitted and the entries it did not admit, each with its draw position. It SHALL set every admitted entry to Won and every other given entry to Lost, with their draw positions, all together or not at all. It SHALL change only entries that are Entered. When every given entry already has the given state and draw position, it SHALL succeed and change nothing. When any given entry is Won or Lost with another state or draw position than given, it SHALL fail with FailedPrecondition and change nothing.

#### Scenario: Outcome recorded
- **WHEN** RecordDrawOutcome is called for a TicketType with two admitted entries and one not admitted, all Entered
- **THEN** the two are Won, the third is Lost, and each carries its draw position

#### Scenario: Recorded again
- **WHEN** RecordDrawOutcome is called again with the same outcome
- **THEN** it succeeds and no entry changes

#### Scenario: Another outcome
- **WHEN** RecordDrawOutcome is called for a TicketType whose entries are already recorded, with another entry admitted
- **THEN** it fails with FailedPrecondition and no entry changes

#### Scenario: Failure leaves nothing recorded
- **WHEN** recording any entry of the outcome fails
- **THEN** no entry's state or draw position changes
