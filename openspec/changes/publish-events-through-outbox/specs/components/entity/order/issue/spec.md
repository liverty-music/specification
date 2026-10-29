## ADDED Requirements

### Requirement: An issued Order is announced as paid

Issue SHALL announce the stored Order as paid together with what it stores: all of it is stored and announced, or nothing is. An Issue that fails, including with AlreadyExists, SHALL announce nothing. When the announcement cannot be recorded, Issue SHALL fail with Unavailable and store nothing. The paid announcement is what product analytics records as one "order paid" signal for the Order, at its pay time.

#### Scenario: Order paid

- **WHEN** Issue stores an Order for a fan's Checkout of 2 tickets
- **THEN** the Order is announced as paid once

#### Scenario: Second order for the source

- **WHEN** Issue fails with AlreadyExists because the Checkout already has an Order
- **THEN** nothing is announced

#### Scenario: Announcement cannot be recorded

- **WHEN** the paid announcement of a new Order cannot be recorded
- **THEN** Issue fails with Unavailable, no Order or Ticket is stored and the Checkout stays Committed
