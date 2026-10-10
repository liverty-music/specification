# Spec Delta

## Purpose

Lists the entries of one TicketType that take part in its draw.

## ADDED Requirements

### Requirement: Draw candidates

ListEnteredForTicketType SHALL return every entry of the TicketType whose state is Entered, in no particular order, and no entry in any other state or of any other TicketType. It SHALL return an empty list when the TicketType has none.

#### Scenario: Mixed states
- **WHEN** a TicketType has two Entered entries and one Withdrawn entry
- **THEN** only the two Entered entries are returned

#### Scenario: No candidates
- **WHEN** the TicketType has no Entered entry
- **THEN** an empty list is returned
