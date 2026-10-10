# Spec Delta

## Purpose

Records the outcome of one TicketSale's draw: each winner Won, each loser Lost, every one with its draw position, and the sale as drawn.

## ADDED Requirements

### Requirement: Draw outcome is recorded together

PersistDrawOutcome SHALL set every given winner to Won and every given loser to Lost with their draw positions, across all TicketTypes of the sale, and set the sale's drawn time, all together or not at all. With no winners and no losers it SHALL only set the sale's drawn time.

#### Scenario: Outcome recorded
- **WHEN** PersistDrawOutcome is called with winners and losers for two TicketTypes of a sale
- **THEN** the winners are Won, the losers are Lost, each carries its draw position, and the sale is drawn

#### Scenario: Failure leaves nothing recorded
- **WHEN** recording any part of the outcome fails
- **THEN** no entry state, draw position or drawn time is changed

#### Scenario: Empty draw
- **WHEN** PersistDrawOutcome is called with no winners and no losers
- **THEN** the sale is drawn and no entry changes
