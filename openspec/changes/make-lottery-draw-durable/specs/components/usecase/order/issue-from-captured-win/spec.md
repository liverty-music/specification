## REMOVED Requirements

### Requirement: Issue an order and its tickets from a won entry
**Reason**: Replaced by OrderUseCase.Issue, which charges the Won entry itself before it issues, because the draw no longer captures.
**Migration**: Callers use OrderUseCase.Issue.

### Requirement: Identity verification binding
**Reason**: Moved unchanged to OrderUseCase.Issue.
**Migration**: None.
