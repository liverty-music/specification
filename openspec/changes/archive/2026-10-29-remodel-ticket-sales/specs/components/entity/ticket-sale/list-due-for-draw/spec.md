# Spec Delta

## ADDED Requirements

### Requirement: Closed lotteries with entries still Entered are due

ListDueForDraw SHALL return every Organizer's sale whose method is Lottery, whose end time is at least 1 minute before the given instant and that still has an Entered LotteryEntry, and no other sale. A discovered sale SHALL never be returned, because the platform takes no entries for it. It SHALL return an empty list when none is due.

#### Scenario: Closed and undrawn
- **WHEN** an Organizer's Lottery sale ended 2 minutes before the instant and has an Entered entry
- **THEN** it is returned

#### Scenario: Just closed
- **WHEN** a Lottery sale with an Entered entry ended 30 seconds before the instant
- **THEN** it is not returned

#### Scenario: Still open
- **WHEN** a Lottery sale's end time is after the instant
- **THEN** it is not returned

#### Scenario: Already drawn
- **WHEN** a closed Lottery sale's entries are all Won or Lost
- **THEN** it is not returned

#### Scenario: Closed without entries
- **WHEN** a closed Lottery sale has no entries
- **THEN** it is not returned

#### Scenario: Discovered lottery has closed
- **WHEN** a discovered Lottery sale ended before the instant
- **THEN** it is not returned

## REMOVED Requirements

### Requirement: Sales due for draw

**Reason**: The draw time is removed; a lottery is due while it has closed and still has an Entered entry.
**Migration**: See "Closed lotteries with entries still Entered are due".
