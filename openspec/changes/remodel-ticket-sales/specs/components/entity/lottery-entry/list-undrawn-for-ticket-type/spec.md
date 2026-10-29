# Spec Delta

## MODIFIED Requirements

### Requirement: Entries the draw settles

ListUndrawnForTicketType SHALL take a TicketSale and a TicketStock and return every entry of the sale whose state is Entered and whose Order is of that TicketStock, with its Order, in no particular order, and no entry in any other state, of another sale or of another TicketStock. It SHALL return an empty list when there is none.

#### Scenario: Mixed states
- **WHEN** a sale has two Entered entries, one Won and one Lost entry for a TicketStock
- **THEN** the two Entered entries are returned

#### Scenario: No candidates
- **WHEN** the sale has no Entered entry for the TicketStock
- **THEN** an empty list is returned
