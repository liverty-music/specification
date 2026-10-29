## MODIFIED Requirements

### Requirement: Draw outcome is recorded together

PersistDrawOutcome SHALL set every given winner to Won and every given loser to Lost with their draw positions and, for a loser, its lost reason (not drawn, or card could not be charged), across all TicketTypes of the sale, and set the sale's draw time, all together or not at all. With no winners and no losers it SHALL only set the sale's draw time. When the sale already has a draw time, PersistDrawOutcome SHALL succeed and change nothing.

#### Scenario: Outcome recorded
- **WHEN** PersistDrawOutcome is called with winners and losers for two TicketTypes of a sale
- **THEN** the winners are Won, the losers are Lost with their lost reasons, each carries its draw position, and the sale is drawn

#### Scenario: Failure leaves nothing recorded
- **WHEN** recording any part of the outcome fails
- **THEN** no entry state, draw position, lost reason or draw time is changed

#### Scenario: Empty draw
- **WHEN** PersistDrawOutcome is called with no winners and no losers
- **THEN** the sale is drawn and no entry changes

#### Scenario: Recorded again
- **WHEN** PersistDrawOutcome is called for a sale that already has a draw time
- **THEN** it succeeds, and no entry and no draw time changes

## ADDED Requirements

### Requirement: Each drawn entry is announced with the outcome

PersistDrawOutcome SHALL announce each entry it sets Won or Lost, as it is after the draw, together with the outcome: the outcome and its announcements are stored together or not at all. When the sale already has a draw time it SHALL announce nothing. When an announcement cannot be recorded, PersistDrawOutcome SHALL fail with Unavailable and record nothing. Each announcement is what product analytics records as one "lottery result" signal for the entry's fan.

#### Scenario: Two entries, one place
- **WHEN** PersistDrawOutcome records one entry Won and one entry Lost
- **THEN** two lottery results are announced, one per entry

#### Scenario: Recorded again announces nothing
- **WHEN** PersistDrawOutcome is called for a sale that already has a draw time
- **THEN** nothing is announced

#### Scenario: Announcement cannot be recorded
- **WHEN** an entry's announcement cannot be recorded
- **THEN** PersistDrawOutcome fails with Unavailable and no entry, lost reason or draw time is changed
