## REMOVED Requirements

### Requirement: Only the fan's own checkout, committed while holding
**Reason**: Split by when it can be decided. The checks a fan can fix are made by OrderUseCase.Place before anything is committed, and the commit is the first step of OrderUseCase.Issue, which issues the Orders of both sources.
**Migration**: CheckoutService.Confirm runs OrderUseCase.Place with the same request.

### Requirement: Charge once, then issue
**Reason**: Moved to OrderUseCase.Issue ("Commit a Checkout, charge it once, then issue"); an unavailable payment provider is tried again by Issue itself instead of a sweeper.
**Migration**: None.

### Requirement: IdentityVerification binding
**Reason**: Moved to OrderUseCase.Issue ("IdentityVerification binding for a Checkout"); a missing IdentityVerification is also reported to the fan by OrderUseCase.Place before anything is committed.
**Migration**: None.
