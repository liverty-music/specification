## REMOVED Requirements

### Requirement: Each completed charge ends in an issued Order
**Reason**: OrderUseCase.Issue charges the Order of both sources and makes it Paid with Order.Issue, which announces it, so the completed-charge notice adds nothing.
**Migration**: The payment events endpoint acknowledges the notice without effect.
