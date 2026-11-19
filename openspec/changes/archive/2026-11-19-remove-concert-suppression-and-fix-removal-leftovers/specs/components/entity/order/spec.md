## ADDED Requirements

### Requirement: An Order leaves with its Event only when ended

An Order SHALL be removable together with the Event it admits to only when it is Void or Refunded. A Pending or Paid Order SHALL NOT be removed with its Event.

#### Scenario: Void order
- **WHEN** the status is Void
- **THEN** the Order can be removed with its Event

#### Scenario: Refunded order
- **WHEN** the status is Refunded
- **THEN** the Order can be removed with its Event

#### Scenario: Paid order
- **WHEN** the status is Paid
- **THEN** the Order cannot be removed with its Event

#### Scenario: Pending order
- **WHEN** the status is Pending
- **THEN** the Order cannot be removed with its Event
