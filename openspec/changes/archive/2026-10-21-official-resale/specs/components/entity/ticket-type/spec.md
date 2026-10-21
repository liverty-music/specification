## ADDED Requirements

### Requirement: Resale opens when the ticket type sells out

A FirstCome TicketType SHALL have a resale open time once its sold count has equalled its quantity: the time of the commit that sold its last ticket. Once set, the resale open time SHALL never change or be cleared, even when the quantity is raised or a commit is reverted afterwards. A TicketType whose sold count has never equalled its quantity SHALL have no resale open time.

#### Scenario: Last ticket sold
- **WHEN** a TicketType of 150 has sold 149 and a Checkout for 1 ticket is committed at 20:15
- **THEN** its resale open time is 20:15

#### Scenario: Quantity raised after selling out
- **WHEN** a TicketType that sold out at 20:15 has its quantity raised from 150 to 160
- **THEN** it is OnSale again and its resale open time stays 20:15

#### Scenario: Never sold out
- **WHEN** a TicketType of 150 has sold 149
- **THEN** it has no resale open time

### Requirement: Resale open at a time

A FirstCome TicketType's resale SHALL be open at a time, given its event's resale deadline, when it has a resale open time and the time is before the deadline.

#### Scenario: A week before the event
- **WHEN** a TicketType with a resale open time is checked a week before its event's resale deadline
- **THEN** its resale is open

#### Scenario: After the deadline
- **WHEN** it is checked at its event's resale deadline
- **THEN** its resale is not open

#### Scenario: Sale ended after selling out
- **WHEN** a TicketType that sold out is checked after its sale's end time and before the resale deadline
- **THEN** its state is Ended and its resale is open

### Requirement: Resale available at a time

A FirstCome TicketType SHALL have resale available at a time when its resale is open at that time and at least one of its ResaleListings is free at that time. The number of free listings is its free resale count.

#### Scenario: One listing free
- **WHEN** a TicketType whose resale is open has one free listing
- **THEN** resale is available

#### Scenario: Every listing held
- **WHEN** a TicketType whose resale is open has two listings, both held by holding Checkouts
- **THEN** resale is not available
