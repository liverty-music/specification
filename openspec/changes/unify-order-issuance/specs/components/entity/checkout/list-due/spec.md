## REMOVED Requirements

### Requirement: Lapsed holds, card authorizations to give back and stalled commits
**Reason**: Its readers go: OrderUseCase.IssueDueCheckouts is removed, and CheckoutUseCase.ReleaseExpired is replaced by CheckoutUseCase.Expire and OrderUseCase.ReleaseCardAuthorization, started per Checkout.
**Migration**: None; the operation is removed.
