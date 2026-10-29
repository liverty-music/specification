## Purpose

OrderUseCase.Place places a fan's order for their Checkout: it checks what the fan can still fix, then has OrderUseCase.Issue commit, charge and issue the Checkout's Order, and returns the Order.

## ADDED Requirements

### Requirement: Only the fan's own Checkout, placed while holding

Place SHALL take a Checkout, the calling fan and the current time, and proceed as follows:
1. It SHALL read the Checkout with Checkout.Get and its Order with Order.Get, and fail with PermissionDenied, without revealing whether it exists, when the Checkout does not exist or the calling fan is not its Order's user.
2. When the Order is Paid, it SHALL return that Order and do nothing else. When the Checkout is neither Held nor Committed (it Expired or was Released), it SHALL fail with FailedPrecondition and change nothing.
3. While the Checkout is Held, it SHALL fail with FailedPrecondition, changing nothing, when:
   - the Checkout is not holding at the current time;
   - Event.IsEventPublished reports false for the event of the Order's TicketStock, read with TicketStock.Get, as for a 中止 (cancelled) concert;
   - the Order has no card authorization;
   - the Order's card authorization, read with CardAuthorization.Get, is not Authorized; it SHALL fail with InvalidArgument instead when the card authorization's amount differs from the Order's;
   - the Checkout's sale, read with TicketSale.Get, requires verification and the user has no IdentityVerification (IdentityVerification.GetByUserID), failing with that error.
   A failure of a read SHALL be returned unchanged. In each of these cases the Checkout stays Held and its Order Pending, so the fan can fix it and place the order again.
4. It SHALL then run OrderUseCase.Issue for the Checkout and return its Order. Every Place for the same Checkout SHALL share one run of Issue and get its outcome. When Issue ends without a Paid Order, Place SHALL fail with FailedPrecondition. When Issue has not ended 30 seconds after Place started it, Place SHALL fail with Unavailable while Issue goes on.

The card authorization of a Checkout that is never committed is given back by CheckoutUseCase.ReleaseExpired. The fan learns which case applied from CheckoutUseCase.Get.

#### Scenario: Fan places the order within the hold
- **WHEN** a fan places the order for their holding Checkout whose Order for 2 tickets has an Authorized card authorization
- **THEN** the tickets are committed, the card is charged and the Order is returned Paid

#### Scenario: Hold lapsed before placing
- **WHEN** a fan places the order after their hold expired
- **THEN** Place fails with FailedPrecondition, nothing is charged and the card is not checked

#### Scenario: Checkout already expired
- **WHEN** a fan places the order for a Checkout that ReleaseExpired already made Expired
- **THEN** Place fails with FailedPrecondition, Issue does not run and nothing is charged

#### Scenario: Concert cancelled during the checkout
- **WHEN** the concert is cancelled while a fan's hold lasts and the fan then places the order
- **THEN** Place fails with FailedPrecondition, the Checkout stays Held and nothing is charged

#### Scenario: Card not yet authenticated
- **WHEN** the fan places the order before completing card authentication, completes it and places the order again
- **THEN** the first Place fails with FailedPrecondition and the Checkout stays Held, and the second returns the Paid Order

#### Scenario: IdentityVerification gone before placing
- **WHEN** the sale requires verification and IdentityVerification.GetByUserID fails with NotFound
- **THEN** Place fails with NotFound, nothing is charged and the Order stays Pending

#### Scenario: Double tap on the action
- **WHEN** the fan places the order twice at the same time
- **THEN** the Order is issued once, the card is charged once, and both calls return that Order

#### Scenario: Someone else's checkout
- **WHEN** a fan places the order for a Checkout whose Order is another User's, whether or not it was paid
- **THEN** Place fails with PermissionDenied and returns no Order

#### Scenario: Card no longer chargeable
- **WHEN** Issue ends with the Order Void because the card authorization can no longer be charged
- **THEN** Place fails with FailedPrecondition

#### Scenario: Charge still completing
- **WHEN** the payment provider cannot be reached and Issue has not ended 30 seconds after it started
- **THEN** Place fails with Unavailable, and the Order becomes Paid once the provider answers
