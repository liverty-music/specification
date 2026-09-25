# Spec Delta

## REMOVED Requirements

### Requirement: One settlement per order

**Reason**: `Upsert`'s only caller, `PayoutSweeperUseCase.EnsureSettlementExists`, is removed in this change; `Order.Issue` now inserts the Settlement directly in the issuance transaction.
**Migration**: None. `Upsert` was never called in production.
