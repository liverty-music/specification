# Spec Delta

## MODIFIED Requirements

### Requirement: Capacity, group size and price

The ticket capacity, the max tickets per application and the ticket price SHALL each be greater than 0, the max tickets per application SHALL NOT exceed the ticket capacity, and it SHALL be at most 10, because one entry QR code presents at most 10 tickets and a companion group enters together with one code. Capacity is counted in tickets, not applications.

#### Scenario: Valid sizing

- **WHEN** capacity is 100, max tickets per application is 4 and the price is 8000 yen
- **THEN** the phase is valid

#### Scenario: Group larger than capacity

- **WHEN** capacity is 3 and max tickets per application is 4
- **THEN** the phase is invalid

#### Scenario: Group larger than one entry code

- **WHEN** capacity is 100 and max tickets per application is 11
- **THEN** the phase is invalid

#### Scenario: Non-positive value

- **WHEN** capacity, max tickets per application or price is 0 or less
- **THEN** the phase is invalid
