# Spec Delta

## Purpose

Tallies the entries of one TicketType for the Organizer's view of its sale.

## ADDED Requirements

### Requirement: Ticket type tallies

GetTicketTypeStats SHALL return, over the TicketType's active entries: the number of entries, the sum of their requested ticket counts, the number of Won entries, the sum of the Won entries' ticket counts and the number of Lost entries. A TicketType with no entries SHALL yield all counts zero.

#### Scenario: After the draw
- **WHEN** a drawn TicketType has 3 active entries for 2, 2 and 4 tickets, of which the two 2-ticket entries won
- **THEN** there are 3 entries for 8 tickets, 2 winning entries for 4 tickets and 1 waitlisted entry

#### Scenario: Withdrawn entries excluded
- **WHEN** a TicketType has one Entered and one Withdrawn entry
- **THEN** the entry count is 1

#### Scenario: No entries
- **WHEN** the TicketType has no entry
- **THEN** every count is zero
