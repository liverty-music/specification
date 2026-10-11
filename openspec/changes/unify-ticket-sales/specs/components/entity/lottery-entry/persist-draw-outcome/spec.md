# Spec Delta

## Purpose

Records the outcome of one TicketSale's draw: each winner Won, each loser Lost, every one with its draw position, each Draft left unconfirmed Withdrawn, and the sale as drawn.

## ADDED Requirements

### Requirement: Draw outcome is recorded together

PersistDrawOutcome SHALL set every given winner to Won and every given loser to Lost with their draw positions, and every given unconfirmed Draft to Withdrawn, across all TicketTypes of the sale, and set the sale's draw time, all together or not at all. With no winners, losers or Drafts it SHALL only set the sale's draw time.

#### Scenario: Outcome recorded
- **WHEN** PersistDrawOutcome is called with winners, losers and one Draft for two TicketTypes of a sale
- **THEN** the winners are Won, the losers are Lost, each carries its draw position, the Draft is Withdrawn, and the sale is drawn

#### Scenario: Failure leaves nothing recorded
- **WHEN** recording any part of the outcome fails
- **THEN** no entry state, draw position or draw time is changed

#### Scenario: Empty draw
- **WHEN** PersistDrawOutcome is called with no winners and no losers
- **THEN** the sale is drawn and no entry changes
