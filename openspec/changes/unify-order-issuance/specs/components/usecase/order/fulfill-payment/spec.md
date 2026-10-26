## REMOVED Requirements

### Requirement: Each completed charge ends in an announced Order
**Reason**: OrderUseCase.Issue charges, issues and announces the Order of both sources; the completed-charge notice adds nothing.
**Migration**: The payment events endpoint acknowledges the notice without effect.

### Requirement: A paid order is reported for product analytics
**Reason**: Reported by OrderUseCase.Issue when it announces the Order.
**Migration**: None.
