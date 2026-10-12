# components/usecase/order/issue-from-checkout Specification

## Purpose
OrderUseCase.IssueFromCheckout finishes a fan's Checkout: it commits the held tickets, charges the card and issues the Order and its account-bound covered tickets, exactly once.

## Requirements

### Requirement: Only the fan's own checkout, committed while holding

IssueFromCheckout SHALL take a Checkout, the calling fan when a fan places the order, and the current time. Calls for the same Checkout SHALL be handled one after the other, so a second call waits for the first and then returns its outcome. The call proceeds as follows:
1. It SHALL read the Checkout with Checkout.Get and fail with PermissionDenied, without revealing whether it exists, when it does not exist or a calling fan is not its User.
2. When Order.GetByCheckoutID then finds an Order, it SHALL return that Order and do nothing else.
3. While the Checkout is Held, it SHALL fail with FailedPrecondition, changing nothing, when:
   - the Checkout is not holding at that time;
   - Event.IsEventPublished reports false for the TicketType's event, read with TicketType.Get, as for a 中止 (cancelled) concert;
   - the Checkout has no card authorization.
4. It SHALL then read the Checkout's card authorization with CardAuthorization.Get and check that it confirms the Checkout for its amount, leaving the Checkout Held so the fan can try again: it SHALL fail with FailedPrecondition when the card authorization is not Authorized, with InvalidArgument when its amount differs, and return a failure of CardAuthorization.Get unchanged.
5. It SHALL then call Checkout.Commit; when Commit reports NotHeld, or the Checkout is Expired or Released, it SHALL fail with FailedPrecondition.

The card authorization of a Checkout that is not committed is given back by CheckoutUseCase.ReleaseExpired. The fan learns which case applied from CheckoutUseCase.Get.

#### Scenario: Fan places the order within the hold
- **WHEN** a fan places the order for their holding Checkout for 2 tickets whose card authorization is Authorized
- **THEN** the tickets are committed, the card is charged and the Order is returned

#### Scenario: Hold lapsed before placing
- **WHEN** a fan places the order after their hold expired
- **THEN** IssueFromCheckout fails with FailedPrecondition, nothing is charged and the card is not checked

#### Scenario: Concert cancelled during the checkout
- **WHEN** the concert is cancelled while a fan's hold lasts and the fan then places the order
- **THEN** IssueFromCheckout fails with FailedPrecondition, the Checkout stays Held and nothing is charged

#### Scenario: Card not yet authenticated
- **WHEN** the fan places the order before completing card authentication
- **THEN** IssueFromCheckout fails with FailedPrecondition and the Checkout stays Held

#### Scenario: Double tap on the action
- **WHEN** the fan places the order twice at the same time
- **THEN** one Order is issued, the card is charged once, and both calls return that Order

#### Scenario: Fan and the stalled-checkout job at once
- **WHEN** a fan's slow placement and OrderUseCase.IssueDueCheckouts handle the same Checkout at the same time
- **THEN** the card is charged once and both end with the same Order

#### Scenario: Someone else's checkout
- **WHEN** a fan places the order for a Checkout of another User, whether or not it was paid
- **THEN** IssueFromCheckout fails with PermissionDenied and returns no Order

### Requirement: Charge once, then issue

For a Committed Checkout without a capture time, IssueFromCheckout SHALL charge the card with CardAuthorization.Capture and record the charge with Checkout.RecordCapture:
- When the capture fails with FailedPrecondition, meaning the card authorization can no longer be charged, it SHALL give the tickets back with Checkout.RevertCommit and fail with FailedPrecondition.
- When it fails with any other error, it SHALL leave the Checkout Committed and fail with that error; OrderUseCase.IssueDueCheckouts finishes the checkout later.

A Checkout that already has a capture time SHALL never be charged again.

It SHALL then read the captured payment with CardAuthorization.Get for the Checkout's card authorization, read the TicketType and its sale with TicketType.Get, resolve the TicketType's event's Organizer with Event.GetOrganizerID, and read the Organizer with Organizer.Get for its platform fee rate. It SHALL build:
- a Paid Order for the Checkout's user, whose source is the Checkout, with the Checkout's amount in yen, the captured payment's ID as its provider payment ID and the captured payment's card brand and last four digits, and a pay time of the time of issuance;
- exactly as many Tickets as the Checkout's count, each bound to that user, for the TicketType's event, and Issued at the same time; the Tickets carry no copy of the user's name or phone number;
- a Held Settlement for the event and its Organizer, with one split paying that Organizer the Order's amount minus the platform fee at the Organizer's rate.

It SHALL store them with Order.Issue. When Order.Issue fails with AlreadyExists, it SHALL return the Order found by Order.GetByCheckoutID. Any other failure leaves the charged Checkout Committed for OrderUseCase.IssueDueCheckouts.

#### Scenario: Checkout issued
- **WHEN** a Committed Checkout for 2 tickets of 3000 yen is charged for an Organizer at 8%
- **THEN** a Paid 6000 yen Order, 2 Issued Tickets bound to the fan, and a Held Settlement with one 5520 yen split are created, and the Checkout is Completed

#### Scenario: Card no longer chargeable
- **WHEN** the capture fails with FailedPrecondition
- **THEN** the Checkout is Released, its tickets go back on sale and IssueFromCheckout fails with FailedPrecondition

#### Scenario: Payment provider unavailable during capture
- **WHEN** the capture fails with Unavailable
- **THEN** the Checkout stays Committed without a capture time and IssueFromCheckout fails with Unavailable

#### Scenario: Issuance fails after the charge
- **WHEN** the card was charged and Order.Issue fails with Unavailable
- **THEN** the Checkout stays Committed with its capture time, and a later run issues the Order without charging again

### Requirement: IdentityVerification binding

When the Checkout's sale requires verification, IssueFromCheckout SHALL bind every Ticket to the user's IdentityVerification, read with IdentityVerification.GetByUserID whatever its status; the name on the Ticket's face stays the user's own full name. When the user has no IdentityVerification, it SHALL fail with that error, before the charge is captured, and create nothing. When the requirement is None, the Tickets carry no IdentityVerification.

#### Scenario: Verified sale issued
- **WHEN** a Checkout of a sale that requires verification is confirmed and the user has an IdentityVerification
- **THEN** every Ticket is bound to that IdentityVerification

#### Scenario: IdentityVerification gone before confirm
- **WHEN** the sale requires verification and IdentityVerification.GetByUserID fails with NotFound at confirm
- **THEN** IssueFromCheckout fails with NotFound, nothing is charged and nothing is created

#### Scenario: No requirement on a first-come sale
- **WHEN** the sale's requirement is None
- **THEN** the Tickets have no IdentityVerification
