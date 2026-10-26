## REMOVED Requirements

### Requirement: Only the fan's own checkout, committed while holding
**Reason**: Moved to OrderUseCase.Issue, which issues the Orders of both sources.
**Migration**: CheckoutService.Confirm runs OrderUseCase.Issue with the same request.

### Requirement: Charge once, then issue
**Reason**: Moved to OrderUseCase.Issue ("Charge a Checkout once, then issue"); an unavailable payment provider is retried by Issue itself instead of a sweeper.
**Migration**: None.

### Requirement: IdentityVerification binding
**Reason**: Moved unchanged to OrderUseCase.Issue ("IdentityVerification binding for a Checkout").
**Migration**: None.
