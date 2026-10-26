## ADDED Requirements

### Requirement: Entry stats of a ticket type's entered and drawn entries

GetStatsByTicketType SHALL return, over the TicketType's Entered, Won and Lost entries: the number of entries, the sum of their ticket counts, the number of Won entries, the sum of the Won entries' ticket counts and the number of Lost entries. A TicketType with no entries SHALL yield all counts zero.

#### Scenario: After the draw
- **WHEN** a drawn TicketType has 3 entries for 2, 2 and 4 tickets, of which the two 2-ticket entries won
- **THEN** there are 3 entries for 8 tickets, 2 winning entries for 4 tickets and 1 losing entry

#### Scenario: Draft entries excluded
- **WHEN** a TicketType has one Entered and one Draft entry
- **THEN** the entry count is 1

#### Scenario: No entries
- **WHEN** the TicketType has no entry
- **THEN** every count is zero

## REMOVED Requirements

### Requirement: Entry stats of a ticket type
**Reason**: The exclusion scenario named the removed Withdrawn state.
**Migration**: Replaced by "Entry stats of a ticket type's entered and drawn entries" with the same counts.
