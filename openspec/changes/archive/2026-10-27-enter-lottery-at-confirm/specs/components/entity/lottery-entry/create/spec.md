## Purpose

LotteryEntry.Create stores a fan's new Entered entry with its card authorization and referral code: at most one per account and TicketType, and only before the sale's end time.

## ADDED Requirements

### Requirement: One entry per account and ticket type, before the end time

Create SHALL take a TicketType, a user, a ticket count, a card authorization and an optional ReferralCode, store a new Entered entry with them and return it. It SHALL fail with AlreadyExists, storing nothing, when the user already has an entry for the TicketType, and with FailedPrecondition, storing nothing, when the TicketType does not exist or its sale's end time has passed at the moment the entry is stored. When an entry already holds the given card authorization, Create SHALL return that entry and store nothing, also after the end time. Checking and storing SHALL be one indivisible step, so two concurrent calls for the same user and TicketType, or for the same card authorization, store one entry, and no entry is stored after the end time.

#### Scenario: Entry stored
- **WHEN** Create is called for a user with no entry for the TicketType, 2 tickets, a card authorization and the code `member-a`
- **THEN** an Entered entry for 2 tickets with that card authorization and the code `member-a` is stored and returned

#### Scenario: Second entry
- **WHEN** the user already has an Entered, Won or Lost entry for the TicketType
- **THEN** Create fails with AlreadyExists and stores nothing

#### Scenario: Double tap
- **WHEN** Create is called twice at the same time for the same user and TicketType
- **THEN** one entry is stored and the other call fails with AlreadyExists

#### Scenario: Same card authorization again
- **WHEN** Create is called with a card authorization an entry already holds, before or after the end time, or twice at the same time
- **THEN** that one entry is returned and nothing else is stored

#### Scenario: Entry for another event of the same sale
- **WHEN** the user has an entry for the sale's TicketType of another event
- **THEN** the entry for this TicketType is stored

#### Scenario: After the end time
- **WHEN** Create is called after the sale's end time
- **THEN** it fails with FailedPrecondition and stores nothing

#### Scenario: Unknown ticket type
- **WHEN** the TicketType does not exist
- **THEN** Create fails with FailedPrecondition and stores nothing
