# Order.Issue

## Purpose

Stores a new Order together with the Tickets it issues.

## Requirements

### Requirement: Order and tickets together, once per application

Issue SHALL store the Order and all of its Tickets together or not at all, and SHALL fail with AlreadyExists when an Order already exists for the same application.

#### Scenario: Order issued

- **WHEN** Issue is called with an Order and its 3 Tickets
- **THEN** the Order and the 3 Tickets are stored

#### Scenario: Failure stores nothing

- **WHEN** storing any Ticket fails
- **THEN** neither the Order nor any Ticket is stored

#### Scenario: Second order for the application

- **WHEN** an Order already exists for the application
- **THEN** Issue fails with AlreadyExists and stores nothing
