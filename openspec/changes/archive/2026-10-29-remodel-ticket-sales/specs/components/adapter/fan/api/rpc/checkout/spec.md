# Spec Delta

## MODIFIED Requirements

### Requirement: Checkout calls are for the signed-in fan

Start, Get, AuthorizeCard and Confirm SHALL require a signed-in caller and fail with Unauthenticated otherwise. They SHALL resolve the caller to their stored User with User.GetByProviderUserID, failing with NotFound when the caller has no stored account. They SHALL pass that User to CheckoutUseCase.Start, CheckoutUseCase.Get, CheckoutUseCase.AuthorizeCard and OrderUseCase.IssueFromCheckout respectively; the request never names a user. AuthorizeCard SHALL return the card authorization secret (`card_authorization_secret`) the usecase returns. Errors from the usecase SHALL be returned unchanged.

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
- **THEN** OrderUseCase.IssueFromCheckout runs with that fan as the caller and the Order is returned

### Requirement: Requests are validated before any usecase runs

Before any usecase runs, the boundary SHALL fail with InvalidArgument when:
- Start's TicketStock is missing or malformed, or its ticket count is missing or not greater than 0;
- Start's referral code is given and is not a valid ReferralCode (1 to 32 lowercase ASCII letters, digits or hyphens); a Start without a referral code is valid;
- the Checkout of Get, AuthorizeCard or Confirm is missing or malformed;
- AuthorizeCard's full name or phone number is missing or breaks the User's personal details rule, including a phone number that is not in E.164 form.

#### Scenario: Missing name
- **WHEN** AuthorizeCard is called without a full name
- **THEN** it fails with InvalidArgument and no card authorization is opened

#### Scenario: Zero tickets
- **WHEN** Start is called with a ticket count of 0
- **THEN** it fails with InvalidArgument and nothing is held

#### Scenario: Domestic-format phone number
- **WHEN** AuthorizeCard is called with the phone number `090-1234-5678`
- **THEN** it fails with InvalidArgument and no card authorization is opened

#### Scenario: Malformed referral code
- **WHEN** Start is called with the referral code `member_a`
- **THEN** it fails with InvalidArgument, nothing is held and no referral code is stored

#### Scenario: Referral code passed on
- **WHEN** Start is called with a valid TicketStock, a ticket count of 2 and the referral code `member-a`
- **THEN** the request passes the boundary and CheckoutUseCase.Start runs with the code `member-a`

## REMOVED Requirements

### Requirement: A returned checkout says whether it is a resale checkout

**Reason**: A Checkout no longer buys resale tickets; official resale is bought through its own lottery, added by the change resell-tickets-by-lottery.
**Migration**: None; the resale flag leaves the Checkout message.
