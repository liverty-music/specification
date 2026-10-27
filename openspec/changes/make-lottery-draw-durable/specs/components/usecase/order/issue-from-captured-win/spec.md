## REMOVED Requirements

### Requirement: Issue an order and its tickets from a won entry
**Reason**: Replaced by OrderUseCase.Issue, which charges the Won entry itself before it issues, because the draw no longer captures.
**Migration**: None; OrderUseCase.Issue runs for each Won entry.

### Requirement: Identity verification binding
**Reason**: Moved to OrderUseCase.Issue ("Identity verification binding"), which reads the IdentityVerification before the charge.
**Migration**: None.
