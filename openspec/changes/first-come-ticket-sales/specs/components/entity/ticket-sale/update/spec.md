# Spec Delta

## Purpose

Changes a TicketSale's window, price, quantity or per-account limit, consistently with what has been sold and held.

## ADDED Requirements

### Requirement: Update keeps sold and held tickets covered

Update SHALL store the given sale start, sale end, price, quantity and per-account limit for the TicketSale. It SHALL fail with InvalidArgument when the result breaks the TicketSale rules, with FailedPrecondition when the price changes after a Reservation was created, and with FailedPrecondition when the new quantity is below the sold count plus the tickets held at that moment. The check and the change SHALL be one indivisible step, so a Reservation created meanwhile is counted. It SHALL fail with NotFound when no TicketSale has the id.

#### Scenario: More tickets

- **WHEN** a sale of 150 with 140 sold is updated to a quantity of 180
- **THEN** its quantity is 180

#### Scenario: Fewer than sold and held

- **WHEN** a sale with 100 sold and 6 held is updated to a quantity of 105
- **THEN** Update fails with FailedPrecondition and nothing changes

#### Scenario: Price after checkout started

- **WHEN** the price of a sale that has had a Reservation is changed
- **THEN** Update fails with FailedPrecondition and nothing changes
