# Spec Delta

## MODIFIED Requirements

### Requirement: Draw outcome is recorded together

PersistDrawOutcome SHALL set every given winner to Won and every given loser to Lost with their draw positions and make every loser's Order Void, across all TicketStocks of the sale's events, all together or not at all. A given entry that is no longer Entered SHALL be left unchanged, so recording the same outcome again changes nothing. Once no entry of the closed sale is Entered, the sale is drawn (components/entity/ticket-sale "Drawn lottery").

#### Scenario: Outcome recorded
- **WHEN** PersistDrawOutcome is called with winners and losers for two TicketStocks of a sale
- **THEN** the winners are Won, the losers are Lost with their Orders Void, each carries its draw position, and the sale is drawn

#### Scenario: Failure leaves nothing recorded
- **WHEN** recording any part of the outcome fails
- **THEN** no entry state, Order status or draw position is changed

#### Scenario: Empty draw
- **WHEN** PersistDrawOutcome is called with no winners and no losers
- **THEN** no entry changes

#### Scenario: Recorded again
- **WHEN** PersistDrawOutcome is called again with an outcome already recorded
- **THEN** it succeeds and no entry changes
