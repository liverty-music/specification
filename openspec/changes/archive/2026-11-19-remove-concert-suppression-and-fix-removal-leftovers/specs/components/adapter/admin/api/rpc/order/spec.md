## REMOVED Requirements

### Requirement: Refund passes the reason and the current time
**Reason**: The time of a refund is the usecase's own current time; the boundary no longer passes it.
**Migration**: See "Refund passes the reason".

## ADDED Requirements

### Requirement: Refund passes the reason

Refund SHALL fail with InvalidArgument, before any usecase runs, when no Order is given or the reason is unspecified. Otherwise it SHALL call OrderUseCase.Refund with the Order and the requested reason, and return the refunded Order. The usecase's NotFound, FailedPrecondition and InvalidArgument SHALL be returned with the same codes.

#### Scenario: Admin refunds a cancelled event's order

- **WHEN** an admin calls Refund for a Paid Order with the reason 中止 (cancellation)
- **THEN** OrderUseCase.Refund runs with that reason and the refunded Order is returned

#### Scenario: Reason missing

- **WHEN** an admin calls Refund without a reason
- **THEN** it fails with InvalidArgument and nothing is refunded

#### Scenario: Unknown order

- **WHEN** an admin calls Refund for an Order that does not exist
- **THEN** it fails with NotFound
