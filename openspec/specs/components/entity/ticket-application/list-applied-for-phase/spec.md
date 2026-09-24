# TicketApplication.ListAppliedForPhase

## Purpose

Lists the applications of one phase that take part in its draw.

## Requirements

### Requirement: Draw candidates

ListAppliedForPhase SHALL return every application of the phase whose state is Applied, in no particular order, and no application in any other state. It SHALL return an empty list when the phase has none.

#### Scenario: Mixed states

- **WHEN** a phase has two Applied applications and one Withdrawn application
- **THEN** only the two Applied applications are returned

#### Scenario: No candidates

- **WHEN** the phase has no Applied application
- **THEN** an empty list is returned
