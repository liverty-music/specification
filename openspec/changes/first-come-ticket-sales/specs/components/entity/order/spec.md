# Spec Delta

## ADDED Requirements

### Requirement: An Order has exactly one source

An Order SHALL come from exactly one source: a won TicketApplication, or a Reservation that was Committed and charged and is Completed by the Order's issuance. An Order that names both, or neither, SHALL be invalid. At most one Order SHALL exist per source.

#### Scenario: Order from a checkout

- **WHEN** an Order names a Reservation and no TicketApplication
- **THEN** its source is valid

#### Scenario: Two sources

- **WHEN** an Order names both a TicketApplication and a Reservation
- **THEN** the Order is invalid
