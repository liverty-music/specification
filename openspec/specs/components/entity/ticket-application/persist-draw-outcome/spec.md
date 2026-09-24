# TicketApplication.PersistDrawOutcome

## Purpose

Records the outcome of one phase's draw: each winner Won, each loser Lost, every one with its draw position, and the phase as drawn.

## Requirements

### Requirement: Draw outcome is recorded together

PersistDrawOutcome SHALL set every given winner to Won and every given loser to Lost with their draw positions, and set the phase's drawn time, all together or not at all. With no winners and no losers it SHALL only set the phase's drawn time.

#### Scenario: Outcome recorded

- **WHEN** PersistDrawOutcome is called with winners and losers for a phase
- **THEN** the winners are Won, the losers are Lost, each carries its draw position, and the phase is drawn

#### Scenario: Failure leaves nothing recorded

- **WHEN** recording any part of the outcome fails
- **THEN** no application state, draw position or drawn time is changed

#### Scenario: Empty draw

- **WHEN** PersistDrawOutcome is called with no winners and no losers
- **THEN** the phase is drawn and no application changes
