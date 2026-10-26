## REMOVED Requirements

### Requirement: Won entries without an order
**Reason**: Its only caller, OrderUseCase.IssueDueWins, is removed: OrderUseCase.Issue runs for each Won entry and resumes on its own.
**Migration**: None.
