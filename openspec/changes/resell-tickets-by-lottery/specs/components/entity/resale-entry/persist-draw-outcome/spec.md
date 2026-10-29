# Spec Delta

## Purpose

Records the outcome of one resale draw of one TicketStock: the entries that won with their listings, the entries that lapsed and, at the last draw, the entries that lost.

## ADDED Requirements

### Requirement: Record a draw all together

PersistDrawOutcome SHALL take a TicketStock, a draw time, the winning entries each with the listings allocated to it, the lapsing entries and the losing entries. In one indivisible step it SHALL:
- make every winner Won with the draw time and allocate its listings to it;
- make every lapsing entry Lapsed and every loser Lost with the draw time and its lost reason (no ticket left at the last draw, or the concert cancelled), and make their Orders Void;
- do this only for entries that are still Entered and listings that are still free for a draw at the draw time.
When an entry is no longer Entered or a listing is no longer free, it SHALL fail with FailedPrecondition and record nothing.

#### Scenario: Outcome recorded
- **WHEN** a draw at 12:00 records one winner of 2 listings, one lapsed entry and no loser
- **THEN** the winner is Won with both listings allocated, the lapsed entry is Lapsed and its Order Void, and both have the draw time 12:00

#### Scenario: Listing withdrawn meanwhile
- **WHEN** one of the winner's listings was withdrawn after the draw read it
- **THEN** PersistDrawOutcome fails with FailedPrecondition and records nothing

#### Scenario: Last draw
- **WHEN** the last draw records the remaining Entered entries as losers
- **THEN** they are Lost with the lost reason "no ticket left" and their Orders Void

### Requirement: Each recorded entry is announced with the draw

PersistDrawOutcome SHALL announce each entry it makes Won, Lapsed or Lost, as it is after the draw, together with the outcome: the outcome and its announcements are stored together or not at all. When an announcement cannot be recorded, PersistDrawOutcome SHALL fail with Unavailable and record nothing.

#### Scenario: Three entries recorded
- **WHEN** a draw records one entry Won, one Lapsed and one Lost
- **THEN** three resale entry results are announced, one per entry

#### Scenario: Announcement cannot be recorded
- **WHEN** an entry's announcement cannot be recorded
- **THEN** PersistDrawOutcome fails with Unavailable and no entry, listing or Order changes
