# Spec Delta

## ADDED Requirements

### Requirement: Entry stats of a ticket stock's entries in a sale

GetStatsBySaleAndStock SHALL take a TicketSale and a TicketStock and return, over all of the sale's entries whose Order is of that TicketStock: the number of entries, the sum of their Orders' ticket counts, the number of Won entries, the sum of the Won entries' ticket counts and the number of Lost entries. A TicketStock with no entries in the sale SHALL yield all counts zero.

#### Scenario: After the draw
- **WHEN** a drawn sale has 3 entries for 2, 2 and 4 tickets of a TicketStock, of which the two 2-ticket entries won
- **THEN** there are 3 entries for 8 tickets, 2 winning entries for 4 tickets and 1 losing entry

#### Scenario: Before the draw
- **WHEN** a sale has two Entered entries for 2 and 3 tickets of a TicketStock
- **THEN** there are 2 entries for 5 tickets, and no winning or losing entry

#### Scenario: No entries
- **WHEN** the sale's only entries are for another TicketStock
- **THEN** every count is zero
