# Spec Delta

## Purpose

Returns a user's Draft LotteryEntry for a TicketType, or creates one, so a repeated or concurrent start never makes two active entries.

## ADDED Requirements

### Requirement: At most one active entry per account per ticket type

GetOrCreateDraft SHALL take a TicketType, a user and a requested ticket count:
- When the user has a Draft for the TicketType with the same count, it SHALL return it and change nothing.
- When the user has a Draft for the TicketType with another count, it SHALL make that Draft Withdrawn and create a new Draft in the same step.
- When the user has no active entry for the TicketType, it SHALL create a new Draft.
- When the user has an Entered, Won or Lost entry for the TicketType, it SHALL fail with AlreadyExists and change nothing.

Checking and creating SHALL be one indivisible step, so two concurrent calls for the same user and TicketType leave at most one active entry. It SHALL fail with FailedPrecondition when the TicketType does not exist.

#### Scenario: First start
- **WHEN** GetOrCreateDraft is called for a user with no entry for the TicketType
- **THEN** a Draft is stored and returned

#### Scenario: Reload with the same count
- **WHEN** the user has a Draft for 2 tickets and GetOrCreateDraft is called again for 2
- **THEN** the same Draft is returned unchanged

#### Scenario: Count changed
- **WHEN** the user has a Draft for 2 tickets and GetOrCreateDraft is called for 3
- **THEN** the old Draft is Withdrawn and a new Draft for 3 tickets is returned

#### Scenario: Double tap
- **WHEN** the same user calls GetOrCreateDraft twice at the same time for a TicketType
- **THEN** one active Draft exists afterwards

#### Scenario: Already entered
- **WHEN** the user has an Entered, Won or Lost entry for the TicketType
- **THEN** GetOrCreateDraft fails with AlreadyExists and changes nothing

#### Scenario: Entry for another event of the same sale
- **WHEN** the user has an active entry for the sale's TicketType of another event
- **THEN** a Draft is created for this TicketType

#### Scenario: Re-entry after withdrawal
- **WHEN** the user's only earlier entry for the TicketType is Withdrawn
- **THEN** a new Draft is created alongside the withdrawn one

#### Scenario: Unknown ticket type
- **WHEN** the TicketType does not exist
- **THEN** GetOrCreateDraft fails with FailedPrecondition
