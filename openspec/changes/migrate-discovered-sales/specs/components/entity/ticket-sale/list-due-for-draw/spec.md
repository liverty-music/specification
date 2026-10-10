# Spec Delta

## MODIFIED Requirements

### Requirement: Sales due for draw

ListDueForDraw SHALL return every Organizer's sale whose method is Lottery, whose end time is at or before the given instant and that is not drawn, and no other sale. A discovered sale SHALL never be returned, because the platform takes no entries for it. It SHALL return an empty list when none is due.

#### Scenario: Closed and undrawn
- **WHEN** an Organizer's Lottery sale ended before the instant and has no drawn time
- **THEN** it is returned

#### Scenario: Still open
- **WHEN** a Lottery sale's end time is after the instant
- **THEN** it is not returned

#### Scenario: Already drawn
- **WHEN** a closed Lottery sale has a drawn time
- **THEN** it is not returned

#### Scenario: Discovered lottery has closed
- **WHEN** a discovered Lottery sale ended before the instant
- **THEN** it is not returned
