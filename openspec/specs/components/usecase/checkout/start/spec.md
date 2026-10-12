# components/usecase/checkout/start Specification

## Purpose
CheckoutUseCase.Start begins a fan's checkout on a TicketType of a FirstCome TicketSale, or resumes it: it holds the chosen number of tickets for 15 minutes and returns the holding Checkout.

## Requirements

### Requirement: Start a checkout while the ticket type is on sale

Start SHALL take the calling fan, a TicketType, a ticket count and the current time:
- It SHALL read the TicketType and its sale with TicketType.Get, failing with NotFound when it does not exist.
- It SHALL fail with FailedPrecondition when the sale's method is not FirstCome, when Event.IsEventPublished reports false for the TicketType's event, as for a 中止 (cancelled) concert, or when the TicketType's state is not OnSale or AllHeld.
- It SHALL fail with InvalidArgument when the count is below 1 or above the TicketType's per-account limit.
- It SHALL apply the verification gate.
- It SHALL then call Checkout.GetOrCreateHeld and return the Checkout it gives; its failures are returned unchanged.

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

### Requirement: Verification gate

When the sale requires verification, Start SHALL require the fan to hold an IdentityVerification whose status is Active, read with IdentityVerification.GetByUserID, and SHALL fail with FailedPrecondition otherwise, holding nothing. When the sale's requirement is None, no IdentityVerification is needed.

#### Scenario: First-come sale requires verification
- **WHEN** a FirstCome sale requires JPKI-only and the fan has never verified
- **THEN** Start fails with FailedPrecondition and nothing is held

#### Scenario: Verified fan starts a checkout
- **WHEN** a FirstCome sale requires verification and the fan's IdentityVerification is Active
- **THEN** Start continues with the other checks
