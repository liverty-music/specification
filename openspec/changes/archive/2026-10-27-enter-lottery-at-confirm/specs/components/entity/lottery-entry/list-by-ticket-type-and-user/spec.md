## ADDED Requirements

### Requirement: Entries of one user for one ticket type

ListByTicketTypeAndUser SHALL return every entry of the user for the TicketType, in every state, newest first, and no entry of another user or another TicketType. It SHALL return an empty list when there is none.

#### Scenario: Entry of the user
- **WHEN** the user has an Entered entry for the TicketType and another user has an entry for it
- **THEN** only the user's Entered entry is returned

#### Scenario: Never entered
- **WHEN** the user has no entry for the TicketType
- **THEN** an empty list is returned

## REMOVED Requirements

### Requirement: Entries of a user for a ticket type
**Reason**: Its first scenario described a Withdrawn entry next to a later entry, which can no longer exist.
**Migration**: Replaced by "Entries of one user for one ticket type" with the same result.
