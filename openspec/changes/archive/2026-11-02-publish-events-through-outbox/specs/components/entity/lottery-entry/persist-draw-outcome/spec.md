## MODIFIED Requirements

### Requirement: Draw outcome is recorded together

PersistDrawOutcome SHALL set every given winner to Won and every given loser to Lost with their draw positions and, for a loser, its lost reason (not drawn, or card could not be charged), and make every loser's Order Void, across all TicketStocks of the sale's events, all together or not at all. A given entry that is no longer Entered SHALL be left unchanged, so recording the same outcome again changes nothing. Once no entry of the closed sale is Entered, the sale is drawn (components/entity/ticket-sale "Drawn lottery").

#### Scenario: Outcome recorded
- **WHEN** PersistDrawOutcome is called with winners and losers for two TicketStocks of a sale
- **THEN** the winners are Won, the losers are Lost with their lost reasons and their Orders Void, each carries its draw position, and the sale is drawn

#### Scenario: Failure leaves nothing recorded
- **WHEN** recording any part of the outcome fails
- **THEN** no entry state, lost reason, Order status or draw position is changed

#### Scenario: Empty draw
- **WHEN** PersistDrawOutcome is called with no winners and no losers
- **THEN** no entry changes

#### Scenario: Recorded again
- **WHEN** PersistDrawOutcome is called again with an outcome already recorded
- **THEN** it succeeds and no entry changes

## ADDED Requirements

### Requirement: Each drawn entry is announced with the outcome

PersistDrawOutcome SHALL announce each entry it sets Won or Lost, as it is after the draw, together with the outcome: the outcome and its announcements are stored together or not at all. An entry it leaves unchanged SHALL NOT be announced. When an announcement cannot be recorded, PersistDrawOutcome SHALL fail with Unavailable and record nothing. Each announcement is what product analytics records as one "lottery result" signal for the fan of the entry's Order.

#### Scenario: Two entries, one place
- **WHEN** PersistDrawOutcome records one entry Won and one entry Lost
- **THEN** two lottery results are announced, one per entry

#### Scenario: Recorded again announces nothing
- **WHEN** PersistDrawOutcome is called again with an outcome already recorded
- **THEN** nothing is announced

#### Scenario: Announcement cannot be recorded
- **WHEN** an entry's announcement cannot be recorded
- **THEN** PersistDrawOutcome fails with Unavailable and no entry, lost reason or Order status is changed
