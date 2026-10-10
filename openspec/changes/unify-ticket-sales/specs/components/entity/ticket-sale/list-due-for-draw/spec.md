# Spec Delta

## Purpose

Lists the Lottery sales whose draw is due at an instant: the window has closed and the sale is not yet drawn.

## ADDED Requirements

### Requirement: Sales due for draw

ListDueForDraw SHALL return every sale whose method is Lottery, whose end time is at or before the given instant and that is not drawn, and no other sale. It SHALL return an empty list when none is due.

#### Scenario: Closed and undrawn
- **WHEN** a Lottery sale ended before the instant and has no drawn time
- **THEN** it is returned

#### Scenario: Still open
- **WHEN** a Lottery sale's end time is after the instant
- **THEN** it is not returned

#### Scenario: Already drawn
- **WHEN** a closed Lottery sale has a drawn time
- **THEN** it is not returned
