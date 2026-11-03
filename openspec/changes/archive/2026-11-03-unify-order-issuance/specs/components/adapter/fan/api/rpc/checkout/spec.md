## MODIFIED Requirements

### Requirement: Checkout calls are for the signed-in fan

Start, Get, AuthorizeCard and Confirm SHALL require a signed-in caller and fail with Unauthenticated otherwise. They SHALL resolve the caller to their stored User with User.GetByProviderUserID, failing with NotFound when the caller has no stored account. They SHALL pass that User to CheckoutUseCase.Start, CheckoutUseCase.Get, CheckoutUseCase.AuthorizeCard and OrderUseCase.Place respectively; the request never names a user. AuthorizeCard SHALL return the card authorization secret (`card_authorization_secret`) the usecase returns. Errors from the usecase SHALL be returned unchanged.

#### Scenario: Fan starts a checkout
- **WHEN** a signed-in fan calls Start for 2 tickets of a TicketStock
- **THEN** CheckoutUseCase.Start runs for that fan and the Checkout is returned

#### Scenario: Guest tries to buy
- **WHEN** a caller who is not signed in calls Start
- **THEN** the call fails with Unauthenticated and nothing is held

#### Scenario: Caller without an account
- **WHEN** a signed-in caller with no stored account calls Start
- **THEN** the call fails with NotFound and nothing is held

#### Scenario: Fan confirms
- **WHEN** a signed-in fan calls Confirm for their Checkout
- **THEN** OrderUseCase.Place runs with that fan as the caller and the Paid Order is returned
