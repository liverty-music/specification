# Spec Delta

## Purpose

The fan-facing checkout service boundary (`CheckoutService`): starting, reading, authorizing and confirming a Checkout is for the signed-in fan, who is always the caller.

## ADDED Requirements

### Requirement: Checkout calls are for the signed-in fan

Start, Get, Authorize and Confirm SHALL require a signed-in caller and fail with Unauthenticated otherwise. They SHALL resolve the caller to their stored User with User.GetByExternalID, failing with NotFound when the caller has no stored account. They SHALL pass that User to CheckoutUseCase.Start, CheckoutUseCase.Get, CheckoutUseCase.Authorize and IssuanceUseCase.IssueFromCheckout respectively; the request never names a user. Errors from the usecase SHALL be returned unchanged.

#### Scenario: Fan starts a checkout
- **WHEN** a signed-in fan calls Start for 2 tickets of a TicketType
- **THEN** CheckoutUseCase.Start runs for that fan and the Checkout is returned

#### Scenario: Guest tries to buy
- **WHEN** a caller who is not signed in calls Start
- **THEN** the call fails with Unauthenticated and nothing is held

#### Scenario: Caller without an account
- **WHEN** a signed-in caller with no stored account calls Start
- **THEN** the call fails with NotFound and nothing is held

#### Scenario: Fan confirms
- **WHEN** a signed-in fan calls Confirm for their Checkout
- **THEN** IssuanceUseCase.IssueFromCheckout runs with that fan as the caller and the Order is returned

### Requirement: Requests are validated before any usecase runs

Before any usecase runs, the boundary SHALL fail with InvalidArgument when:
- Start's TicketType is missing or malformed, or its ticket count is missing or not greater than 0;
- the Checkout of Get, Authorize or Confirm is missing or malformed;
- Authorize's full name or phone number is missing or breaks the User's personal details rule, including a phone number that is not in E.164 form.

#### Scenario: Missing name
- **WHEN** Authorize is called without a full name
- **THEN** it fails with InvalidArgument and no hold is opened

#### Scenario: Zero tickets
- **WHEN** Start is called with a ticket count of 0
- **THEN** it fails with InvalidArgument and nothing is held

#### Scenario: Domestic-format phone number
- **WHEN** Authorize is called with the phone number `090-1234-5678`
- **THEN** it fails with InvalidArgument and no hold is opened
