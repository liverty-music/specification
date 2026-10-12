# components/entity/lottery-entry/list-by-ticket-type-and-user Specification

## Purpose
Lists a user's LotteryEntries for one TicketType.

## Requirements

### Requirement: Entries of a user for a ticket type

ListByTicketTypeAndUser SHALL return every entry of the user for the TicketType, in every state, newest first, and no entry of another user or another TicketType. It SHALL return an empty list when there is none.

#### Scenario: Active entry after a withdrawal
- **WHEN** the user has a Withdrawn entry and a later Entered entry for the TicketType
- **THEN** both are returned, the Entered entry first

#### Scenario: Never entered
- **WHEN** the user has no entry for the TicketType
- **THEN** an empty list is returned
