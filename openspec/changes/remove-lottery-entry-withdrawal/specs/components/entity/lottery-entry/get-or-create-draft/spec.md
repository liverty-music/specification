## ADDED Requirements

### Requirement: At most one entry per account per ticket type

GetOrCreateDraft SHALL take a TicketType, a user and a ticket count:
- When the user has a Draft for the TicketType with the same count, it SHALL return it and change nothing.
- When the user has a Draft for the TicketType with another count, it SHALL set that Draft's ticket count to the given count and remove its card authorization, in one step, and return the Draft together with the card authorization it removed, if any. The Draft's id and its Referral stay.
- When the user has no entry for the TicketType, it SHALL create a new Draft.
- When the user has an Entered, Won or Lost entry for the TicketType, it SHALL fail with AlreadyExists and change nothing.

Checking and creating or changing SHALL be one indivisible step, so two concurrent calls for the same user and TicketType leave at most one entry. It SHALL fail with FailedPrecondition when the TicketType does not exist.

#### Scenario: First start
- **WHEN** GetOrCreateDraft is called for a user with no entry for the TicketType
- **THEN** a Draft is stored and returned

#### Scenario: Reload with the same count
- **WHEN** the user has a Draft for 2 tickets and GetOrCreateDraft is called again for 2
- **THEN** the same Draft is returned unchanged

#### Scenario: Count changed
- **WHEN** the user has a Draft for 2 tickets with a card authorization and GetOrCreateDraft is called for 3
- **THEN** the same Draft is returned with a ticket count of 3 and no card authorization, together with the card authorization it had

#### Scenario: Double tap
- **WHEN** the same user calls GetOrCreateDraft twice at the same time for a TicketType
- **THEN** one Draft exists afterwards

#### Scenario: Already entered
- **WHEN** the user has an Entered, Won or Lost entry for the TicketType
- **THEN** GetOrCreateDraft fails with AlreadyExists and changes nothing

#### Scenario: Entry for another event of the same sale
- **WHEN** the user has an entry for the sale's TicketType of another event
- **THEN** a Draft is created for this TicketType

#### Scenario: Unknown ticket type
- **WHEN** the TicketType does not exist
- **THEN** GetOrCreateDraft fails with FailedPrecondition

## REMOVED Requirements

### Requirement: At most one active entry per account per ticket type
**Reason**: Withdrawn is removed, so every entry counts, and a Draft with another count is changed in place instead of replaced.
**Migration**: Replaced by "At most one entry per account per ticket type". The schema migration deletes the Withdrawn entries, so no account has two entries for one TicketType.
