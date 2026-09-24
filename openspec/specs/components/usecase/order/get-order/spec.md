# TicketUseCase.GetOrder

## Purpose

TicketUseCase.GetOrder returns one of the calling buyer's own Orders.

## Requirements

### Requirement: Own order only

GetOrder SHALL read the Order with Order.Get and return it when the calling buyer is its buyer. It SHALL fail with NotFound when the Order does not exist and, in the same way, when it belongs to another account, so the existence of other buyers' Orders is not revealed.

#### Scenario: Own order

- **WHEN** a buyer asks for their own Order
- **THEN** the Order is returned

#### Scenario: Another buyer's order

- **WHEN** a buyer asks for an Order of another account
- **THEN** GetOrder fails with NotFound

#### Scenario: Unknown order

- **WHEN** the Order does not exist
- **THEN** GetOrder fails with NotFound
