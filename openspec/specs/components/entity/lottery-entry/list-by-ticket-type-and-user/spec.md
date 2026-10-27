# components/entity/lottery-entry/list-by-ticket-type-and-user Specification

## Purpose
Lists a user's LotteryEntries for one TicketType.

## Requirements

### Requirement: Entries of one user for one ticket type

ListByTicketTypeAndUser SHALL return every entry of the user for the TicketType, in every state, newest first, and no entry of another user or another TicketType. It SHALL return an empty list when there is none.

#### Scenario: Entry of the user
- **WHEN** the user has an Entered entry for the TicketType and another user has an entry for it
- **THEN** only the user's Entered entry is returned

#### Scenario: Never entered
- **WHEN** the user has no entry for the TicketType
- **THEN** an empty list is returned
