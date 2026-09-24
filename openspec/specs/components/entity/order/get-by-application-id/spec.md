# Order.GetByApplicationID

## Purpose

Returns the Order created for a winning TicketApplication, which tells whether that application has already been issued.

## Requirements

### Requirement: Order of an application

GetByApplicationID SHALL return the Order created from the given application and SHALL fail with NotFound when the application has no Order.

#### Scenario: Issued application

- **WHEN** an Order exists for the application
- **THEN** that Order is returned

#### Scenario: Not yet issued

- **WHEN** no Order exists for the application
- **THEN** GetByApplicationID fails with NotFound
