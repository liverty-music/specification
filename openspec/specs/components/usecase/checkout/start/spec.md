# components/usecase/checkout/start Specification

## Purpose
CheckoutUseCase.Start begins a fan's checkout on a TicketType of a FirstCome TicketSale, or resumes it: it holds the chosen number of tickets for 15 minutes and returns the holding Checkout, and records the referral code it was started with.

## Requirements

### Requirement: Start a checkout while the ticket type is on sale

Start SHALL take the calling fan, a TicketType, a ticket count and the current time:
- It SHALL read the TicketType and its sale with TicketType.Get, failing with NotFound when it does not exist.
- It SHALL fail with FailedPrecondition when the sale's method is not FirstCome, or when Event.IsEventPublished reports false for the TicketType's event, as for a 中止 (cancelled) concert.
- When the TicketType's state is OnSale or AllHeld, the Checkout holds stock. Otherwise, it SHALL read the event with Event.Get, and when the TicketType's resale is open at the current time with the event's resale deadline, the Checkout holds resale listings; when it is not, Start SHALL fail with FailedPrecondition.
- It SHALL fail with InvalidArgument when the count is below 1 or above the TicketType's per-account limit.
- It SHALL apply the verification gate.
- It SHALL then call Checkout.GetOrCreateHeld, for stock or for resale listings as decided above, and return the Checkout it gives; its failures are returned unchanged.

Starting again with the same count while the hold lasts SHALL resume the same Checkout.

#### Scenario: Fan starts a checkout
- **WHEN** a signed-in fan starts a checkout for 2 tickets of an OnSale TicketType
- **THEN** 2 tickets are held for 15 minutes and the Checkout is returned

#### Scenario: Fan reloads mid-checkout
- **WHEN** the fan reloads the page and starts again with the same count within the hold
- **THEN** the same Checkout is returned with its original hold expiry

#### Scenario: Sale not open yet
- **WHEN** the TicketType is NotYetOnSale
- **THEN** Start fails with FailedPrecondition and nothing is held

#### Scenario: Concert cancelled
- **WHEN** the event's concert was cancelled after the sale opened
- **THEN** Start fails with FailedPrecondition and nothing is held

#### Scenario: Last tickets in other checkouts
- **WHEN** the TicketType is AllHeld
- **THEN** Start fails with ResourceExhausted and nothing is held

#### Scenario: Lottery ticket type
- **WHEN** the TicketType belongs to a Lottery sale
- **THEN** Start fails with FailedPrecondition and nothing is held

#### Scenario: Count over the limit
- **WHEN** the fan asks for 5 tickets of a TicketType limited to 4 per account
- **THEN** Start fails with InvalidArgument and nothing is held

#### Scenario: Sold out with a free listing
- **WHEN** a fan starts a checkout for 1 ticket of a SoldOut TicketType whose resale is open and has a free listing
- **THEN** a resale Checkout holding that listing is returned

#### Scenario: Sale ended, resale still open
- **WHEN** the TicketType is Ended after selling out and the resale deadline has not passed
- **THEN** a resale Checkout is returned when a listing is free

#### Scenario: Sold out, no free listing
- **WHEN** the TicketType's resale is open and every listing is held by others
- **THEN** Start fails with ResourceExhausted and nothing is held

#### Scenario: Ended without selling out
- **WHEN** the TicketType is Ended and never sold out
- **THEN** Start fails with FailedPrecondition and nothing is held

#### Scenario: After the resale deadline
- **WHEN** the TicketType sold out and the event's admission window has opened
- **THEN** Start fails with FailedPrecondition and nothing is held

### Requirement: Verification gate

When the sale requires verification, Start SHALL require the fan to hold an IdentityVerification whose status is Active, read with IdentityVerification.GetByUserID, and SHALL fail with FailedPrecondition otherwise, holding nothing. When the sale's requirement is None, no IdentityVerification is needed.

#### Scenario: First-come sale requires verification
- **WHEN** a FirstCome sale requires JPKI-only and the fan has never verified
- **THEN** Start fails with FailedPrecondition and nothing is held

#### Scenario: Verified fan starts a checkout
- **WHEN** a FirstCome sale requires verification and the fan's IdentityVerification is Active
- **THEN** Start continues with the other checks

### Requirement: Record the referral code the checkout started with

Start SHALL also take an optional ReferralCode. When a code is given and Checkout.GetOrCreateHeld returns a Checkout, Start SHALL set the code on that Checkout with Checkout.SetReferralCode before it returns the Checkout, and SHALL return a failure of Checkout.SetReferralCode unchanged; the hold stays, so starting again resumes the same Checkout and sets the code again. When no code is given, Start SHALL set nothing and an existing code of the Checkout stays as it is. When an earlier check fails, nothing is set. Start SHALL NOT check the code against any list or against the event's Series; any valid ReferralCode is set.

#### Scenario: Checkout from a referral link
- **WHEN** a fan starts a checkout for 2 tickets of an OnSale TicketType with the code `member-a`
- **THEN** the Checkout is returned with the referral code `member-a`

#### Scenario: Another link before confirming
- **WHEN** the fan's Held Checkout has the code `member-a` and the fan starts again with the same count and the code `member-b`
- **THEN** the same Checkout is returned with the referral code `member-b`

#### Scenario: Started again without a code
- **WHEN** the fan's Held Checkout has the code `member-a` and the fan starts again with the same count and no code
- **THEN** the same Checkout is returned and keeps `member-a`

#### Scenario: No code
- **WHEN** a fan starts a checkout without a code
- **THEN** the Checkout has no referral code

#### Scenario: Sale not open with a code
- **WHEN** a fan starts a checkout with the code `member-a` for a NotYetOnSale TicketType
- **THEN** Start fails with FailedPrecondition and no code is set
