## MODIFIED Requirements

### Requirement: Draw outcome is recorded together

PersistDrawOutcome SHALL set every given winner to Won and every given loser to Lost with their draw positions, across all TicketTypes of the sale, and set the sale's draw time, all together or not at all. With no winners and no losers it SHALL only set the sale's draw time. When the sale already has a draw time, it SHALL succeed and change nothing, so recording the same draw again leaves the first record, including any entry made Lost since.

#### Scenario: Outcome recorded
- **WHEN** PersistDrawOutcome is called with winners and losers for two TicketTypes of a sale
- **THEN** the winners are Won, the losers are Lost, each carries its draw position, and the sale is drawn

#### Scenario: Failure leaves nothing recorded
- **WHEN** recording any part of the outcome fails
- **THEN** no entry state, draw position or draw time is changed

#### Scenario: Empty draw
- **WHEN** PersistDrawOutcome is called with no winners and no losers
- **THEN** the sale is drawn and no entry changes

#### Scenario: Recorded again
- **WHEN** PersistDrawOutcome is called for a sale that already has a draw time, after one of its winners was made Lost
- **THEN** it succeeds, the sale keeps its first draw time and no entry changes
