# Admin Order RPC

## Purpose

The admin-facing order service boundary: only admins refund an Order from the admin console, and the boundary supplies the refund's time.

## Requirements

### Requirement: Only admins refund orders

RefundOrder SHALL require a signed-in caller holding the admin role. A caller who is not signed in SHALL fail with Unauthenticated; a signed-in caller without the admin role SHALL fail with PermissionDenied; in both cases nothing is refunded.

#### Scenario: Non-admin

- **WHEN** a signed-in caller without the admin role calls RefundOrder
- **THEN** the call fails with PermissionDenied and the Order is unchanged

### Requirement: RefundOrder passes the reason and the current time

RefundOrder SHALL fail with InvalidArgument, before any usecase runs, when no Order is given or the reason is unspecified. Otherwise it SHALL call RefundOrderUseCase.RefundOrder with the Order, the requested reason and the current time, and return the refunded Order. The usecase's NotFound, FailedPrecondition and InvalidArgument SHALL be returned with the same codes.

#### Scenario: Admin refunds a cancelled event's order

- **WHEN** an admin calls RefundOrder for a Paid Order with the reason 中止 (cancellation)
- **THEN** RefundOrderUseCase.RefundOrder runs with that reason and the current time and the refunded Order is returned

#### Scenario: Reason missing

- **WHEN** an admin calls RefundOrder without a reason
- **THEN** it fails with InvalidArgument and nothing is refunded

#### Scenario: Unknown order

- **WHEN** an admin calls RefundOrder for an Order that does not exist
- **THEN** it fails with NotFound
