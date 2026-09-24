# LotterySalesPhase.ListPhasesDueForDraw

## Purpose

Lists the phases whose draw is due at an instant: the window has closed and the phase is not yet drawn.

## Requirements

### Requirement: Phases due for draw

ListPhasesDueForDraw SHALL return every phase whose close time is at or before the given instant and that is not drawn, and no other phase. It SHALL return an empty list when none is due.

#### Scenario: Closed and undrawn

- **WHEN** a phase closed before the instant and has no drawn time
- **THEN** it is returned

#### Scenario: Still open

- **WHEN** a phase's close time is after the instant
- **THEN** it is not returned

#### Scenario: Already drawn

- **WHEN** a closed phase has a drawn time
- **THEN** it is not returned
