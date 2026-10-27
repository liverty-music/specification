## MODIFIED Requirements

### Requirement: Entries the draw settles

ListUndrawnForTicketType SHALL return every entry of the TicketType whose state is Entered, in no particular order, and no entry in any other state or of any other TicketType. It SHALL return an empty list when the TicketType has none.

#### Scenario: Mixed states
- **WHEN** a TicketType has two Entered entries, one Won and one Lost entry
- **THEN** the two Entered entries are returned

#### Scenario: No candidates
- **WHEN** the TicketType has no Entered entry
- **THEN** an empty list is returned
