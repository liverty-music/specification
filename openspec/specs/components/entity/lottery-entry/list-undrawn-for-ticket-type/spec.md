# components/entity/lottery-entry/list-undrawn-for-ticket-type Specification

## Purpose
Lists the entries of one TicketType that the draw has to settle: the Entered entries it draws and the Drafts it withdraws.

## Requirements

### Requirement: Entries the draw settles

ListUndrawnForTicketType SHALL return every entry of the TicketType whose state is Draft or Entered, in no particular order, and no entry in any other state or of any other TicketType. It SHALL return an empty list when the TicketType has none.

#### Scenario: Mixed states
- **WHEN** a TicketType has two Entered entries, one Draft and one Withdrawn entry
- **THEN** the two Entered entries and the Draft are returned

#### Scenario: No candidates
- **WHEN** the TicketType has no Draft and no Entered entry
- **THEN** an empty list is returned
