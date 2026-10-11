# components/entity/order/get-by-reservation-id Specification

## Purpose
Reads the Order paid for a Reservation, if there is one.

## Requirements

### Requirement: The reservation's order

GetByReservationID SHALL return the Order whose source is the given Reservation, and SHALL fail with NotFound when there is none.

#### Scenario: Paid checkout

- **WHEN** a Completed Reservation's Order is read
- **THEN** that Order is returned

#### Scenario: Checkout not paid

- **WHEN** the Reservation has no Order
- **THEN** GetByReservationID fails with NotFound
