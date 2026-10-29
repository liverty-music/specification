# Spec Delta

## ADDED Requirements

### Requirement: Per-account limit

An Event's per-account limit SHALL be 1 to 10, because one AdmissionCode presents at most 10 tickets and a companion group enters together with one code. An Event created without a per-account limit SHALL have a limit of 4. The limit counts every TicketSale, every SeatType and the official resale of the Event.

#### Scenario: No limit given
- **WHEN** an Event is created without a per-account limit
- **THEN** its per-account limit is 4

#### Scenario: Limit larger than one admission code
- **WHEN** an Event's per-account limit is 11
- **THEN** the Event is invalid

#### Scenario: Limit of zero
- **WHEN** an Event's per-account limit is 0
- **THEN** the Event is invalid

### Requirement: An account's application fits the event

An application by an account for a ticket count of one SeatType SHALL fit the Event when the tickets the account holds for the Event plus the ticket count are at most the per-account limit, and every ticket the account holds for the Event is of that SeatType. An account that holds no ticket for the Event may apply for any SeatType.

#### Scenario: Presale winner in a general sale
- **WHEN** the per-account limit is 4, the account holds 4 S席 tickets for the event and applies for 1 more S席
- **THEN** the application does not fit

#### Scenario: Topping up
- **WHEN** the per-account limit is 4, the account holds 2 S席 tickets for the event and applies for 2 S席
- **THEN** the application fits

#### Scenario: Another seat type
- **WHEN** the account holds 2 S席 tickets for the event and applies for 1 A席
- **THEN** the application does not fit

#### Scenario: First application
- **WHEN** the account holds no ticket for the event and applies for 2 A席
- **THEN** the application fits
