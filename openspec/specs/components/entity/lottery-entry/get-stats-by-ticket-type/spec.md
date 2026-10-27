# components/entity/lottery-entry/get-stats-by-ticket-type Specification

## Purpose
LotteryEntry.GetStatsByTicketType counts the entries of one TicketType for the Organizer's view of its sale.

## Requirements

### Requirement: Entry stats of a ticket type's entries

GetStatsByTicketType SHALL return, over all of the TicketType's entries: the number of entries, the sum of their ticket counts, the number of Won entries, the sum of the Won entries' ticket counts and the number of Lost entries. A TicketType with no entries SHALL yield all counts zero.

#### Scenario: After the draw
- **WHEN** a drawn TicketType has 3 entries for 2, 2 and 4 tickets, of which the two 2-ticket entries won
- **THEN** there are 3 entries for 8 tickets, 2 winning entries for 4 tickets and 1 losing entry

#### Scenario: Before the draw
- **WHEN** a TicketType has two Entered entries for 2 and 3 tickets
- **THEN** there are 2 entries for 5 tickets, and no winning or losing entry

#### Scenario: No entries
- **WHEN** the TicketType has no entry
- **THEN** every count is zero
