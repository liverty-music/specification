# Spec Delta

## Purpose

Stores a new LotteryEntry for a TicketType and returns it as stored.

## ADDED Requirements

### Requirement: One active entry per account per ticket type

Create SHALL store the entry and return it. It SHALL fail with AlreadyExists when the user already has an active entry for the same TicketType, and with FailedPrecondition when the TicketType does not exist.

#### Scenario: First entry
- **WHEN** Create is called for a user with no active entry for the TicketType
- **THEN** the entry is stored and returned

#### Scenario: Active entry exists
- **WHEN** the user already has an Entered, Won or Lost entry for the TicketType
- **THEN** Create fails with AlreadyExists and stores nothing

#### Scenario: Entry for another event of the same sale
- **WHEN** the user has an active entry for the sale's TicketType of another event
- **THEN** Create stores the new entry

#### Scenario: Re-entry after withdrawal
- **WHEN** the user's only earlier entry for the TicketType is Withdrawn
- **THEN** Create stores the new entry alongside the withdrawn one

#### Scenario: Unknown ticket type
- **WHEN** the TicketType does not exist
- **THEN** Create fails with FailedPrecondition
