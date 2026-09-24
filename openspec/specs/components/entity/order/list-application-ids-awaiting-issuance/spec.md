# Order.ListApplicationIDsAwaitingIssuance

## Purpose

Lists the Won TicketApplications that have no Order yet.

## Requirements

### Requirement: Won applications without an order

ListApplicationIDsAwaitingIssuance SHALL return the id of every Won application that has no Order, and no other id. It SHALL return an empty list when there is none.

#### Scenario: Won without order

- **WHEN** an application is Won and has no Order
- **THEN** its id is returned

#### Scenario: Already issued

- **WHEN** a Won application already has an Order
- **THEN** its id is not returned

#### Scenario: Not won

- **WHEN** an application is Applied, Lost or Withdrawn
- **THEN** its id is not returned
