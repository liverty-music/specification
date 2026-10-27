# components/entity/lottery-entry/list-by-user Specification

## Purpose
Lists every LotteryEntry one User has made, across all TicketTypes, so a caller can tell whether any of them is still awaiting its draw.

## Requirements

### Requirement: Entries of one user

ListByUser SHALL return every LotteryEntry whose user is the given User, for every TicketType and in every state, newest first, and no entry of another User. It SHALL return an empty list when there is none.

#### Scenario: Entries for two ticket types

- **WHEN** the User has an Entered entry for one TicketType and a Lost entry for another, and another User has an entry
- **THEN** both of the User's entries are returned and the other User's is not

#### Scenario: Never entered

- **WHEN** the User has no entry
- **THEN** an empty list is returned
