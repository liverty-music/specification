## REMOVED Requirements

### Requirement: Pay a won entry's order and issue its tickets
**Reason**: Replaced by OrderUseCase.Issue, which charges the Won entry's Order itself before it issues, because the draw no longer captures.
**Migration**: None; OrderUseCase.Issue runs for each Won entry.

### Requirement: Identity verification binding
**Reason**: Moved to OrderUseCase.Issue ("Identity verification binding"), which reads the IdentityVerification before the charge.
**Migration**: None.
