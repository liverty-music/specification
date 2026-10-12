# components/entity/ticket-type/update Specification

## Purpose
Changes one TicketType's price, quantity and per-account limit, consistently with what a first-come TicketType has sold and held.

## Requirements

### Requirement: Update keeps sold and held tickets covered

Update SHALL store the given price, quantity and per-account limit for the TicketType and return it with its TicketSale. It SHALL fail with InvalidArgument when the result breaks the TicketType rules, and with NotFound when no TicketType has the id. For a TicketType of a FirstCome sale it SHALL also fail with FailedPrecondition when the price changes while any ticket is sold or held at that moment, and with FailedPrecondition when the new quantity is below the sold count plus the tickets held at that moment; the check and the change SHALL be one indivisible step, so a Checkout created meanwhile is counted.

#### Scenario: More tickets

- **WHEN** a first-come TicketType of 150 with 140 sold is updated to a quantity of 180
- **THEN** its quantity is 180

#### Scenario: Fewer than sold and held

- **WHEN** a first-come TicketType with 100 sold and 6 held is updated to a quantity of 105
- **THEN** Update fails with FailedPrecondition and nothing changes

#### Scenario: Price while tickets are held

- **WHEN** the price of a first-come TicketType whose Checkouts hold 2 tickets is changed
- **THEN** Update fails with FailedPrecondition and nothing changes

#### Scenario: Lottery ticket type resized

- **WHEN** a Lottery TicketType of 100 at 8000 yen is updated to 120 tickets at 9000 yen
- **THEN** its quantity is 120 and its price 9000 yen

#### Scenario: Limit above the quantity

- **WHEN** a TicketType is updated to a quantity of 3 with a per-account limit of 4
- **THEN** Update fails with InvalidArgument and nothing changes

#### Scenario: Unknown ticket type

- **WHEN** no TicketType has the id
- **THEN** Update fails with NotFound
