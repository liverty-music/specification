# Spec Delta

## Purpose

Stores a fan's ResaleEntry together with its Pending Order, so the fan takes part in the daily resale draws of a sold-out TicketStock.

## ADDED Requirements

### Requirement: Store an entry with its Order

Create SHALL take a user, a TicketStock, a ticket count, an optional referral code, an authorized CardAuthorization and a time, and store an Entered ResaleEntry with its Pending Order for them, both or neither. It SHALL fail with:
- FailedPrecondition when the TicketStock's resale is not open at the time;
- FailedPrecondition when the application does not fit the TicketStock's event at the time of storing (the per-account limit or the seat type rule), counting the user's Pending Orders;
- AlreadyExists when the user already has an Entered ResaleEntry for the TicketStock's event;
- NotFound when the TicketStock does not exist.
When an entry already exists for the same card authorization, Create SHALL return it and store nothing.

#### Scenario: Entry stored
- **WHEN** a fan holding no ticket for the event applies for 2 tickets of a sold-out stock with an authorized card authorization
- **THEN** an Entered entry and its Pending Order for 2 tickets are stored

#### Scenario: Resale not open
- **WHEN** the stock is not sold out
- **THEN** Create fails with FailedPrecondition and stores nothing

#### Scenario: Over the limit
- **WHEN** the event's limit is 4, the fan holds 3 tickets and applies for 2
- **THEN** Create fails with FailedPrecondition and stores nothing

#### Scenario: Second entry for the event
- **WHEN** the fan already has an Entered resale entry for the event
- **THEN** Create fails with AlreadyExists and stores nothing

#### Scenario: Same card authorization again
- **WHEN** Create runs twice for the same card authorization
- **THEN** one entry exists and the second call returns it

#### Scenario: Two applications at once
- **WHEN** the same fan applies for 2 tickets of the event twice at the same moment with two card authorizations
- **THEN** one entry is stored and the other call fails with AlreadyExists
