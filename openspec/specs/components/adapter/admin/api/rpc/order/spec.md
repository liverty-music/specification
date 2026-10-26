# Admin Order RPC

## Purpose

The admin-facing order service boundary: only admins refund an Order from the admin console, and the boundary supplies the refund's time.

## Requirements

### Requirement: Only admins refund orders

Refund SHALL require a signed-in caller holding the admin role. A caller who is not signed in SHALL fail with Unauthenticated; a signed-in caller without the admin role SHALL fail with PermissionDenied; in both cases nothing is refunded.

#### Scenario: Non-admin

- **WHEN** a signed-in caller without the admin role calls Refund
- **THEN** the call fails with PermissionDenied and the Order is unchanged

### Requirement: Refund passes the reason and the current time

Refund SHALL fail with InvalidArgument, before any usecase runs, when no Order is given or the reason is unspecified. Otherwise it SHALL call OrderUseCase.Refund with the Order, the requested reason and the current time, and return the refunded Order. The usecase's NotFound, FailedPrecondition and InvalidArgument SHALL be returned with the same codes.

#### Scenario: Admin refunds a cancelled event's order

- **WHEN** an admin calls Refund for a Paid Order with the reason 中止 (cancellation)
- **THEN** OrderUseCase.Refund runs with that reason and the current time and the refunded Order is returned

#### Scenario: Reason missing

- **WHEN** an admin calls Refund without a reason
- **THEN** it fails with InvalidArgument and nothing is refunded

#### Scenario: Unknown order

- **WHEN** an admin calls Refund for an Order that does not exist
- **THEN** it fails with NotFound

### Requirement: Admins read an order with its settlement

Get SHALL require a signed-in caller holding the admin role. A caller who is not signed in SHALL fail with Unauthenticated; a signed-in caller without the admin role SHALL fail with PermissionDenied; both checks come before anything is read. Get SHALL fail with InvalidArgument when no Order is given, and with NotFound when the Order does not exist. Otherwise it SHALL run OrderUseCase.GetWithSettlement and return the Order together with its Settlement and the Settlement's splits, or the Order alone when it has no Settlement; an Order without a Settlement is not an error.

#### Scenario: Paid order of a first-party concert

- **WHEN** an admin calls Get for a Paid Order whose payout is Held
- **THEN** the Order is returned with its Held Settlement and its splits

#### Scenario: Order without a settlement

- **WHEN** an admin calls Get for an Order that has no Settlement
- **THEN** the Order is returned without a Settlement

#### Scenario: Unknown order

- **WHEN** an admin calls Get for an Order that does not exist
- **THEN** it fails with NotFound

#### Scenario: Non-admin reads an order

- **WHEN** a signed-in caller without the admin role calls Get
- **THEN** the call fails with PermissionDenied and nothing is returned

### Requirement: Admins list the orders of an event

ListByEvent SHALL require a signed-in caller holding the admin role. A caller who is not signed in SHALL fail with Unauthenticated; a signed-in caller without the admin role SHALL fail with PermissionDenied; both checks come before anything is read. ListByEvent SHALL fail with InvalidArgument when no Event is given or its id is malformed. Otherwise it SHALL run OrderUseCase.ListByEvent and return the Orders, each with its id, user, status, amount, currency and pay time.

#### Scenario: Admin lists an event's orders

- **WHEN** a signed-in admin calls ListByEvent for an Event with one Paid Order
- **THEN** that Order is returned with its status Paid and its amount

#### Scenario: Event missing

- **WHEN** an admin calls ListByEvent without an Event id
- **THEN** it fails with InvalidArgument

#### Scenario: Non-admin lists orders

- **WHEN** a signed-in caller without the admin role calls ListByEvent
- **THEN** the call fails with PermissionDenied and nothing is returned
