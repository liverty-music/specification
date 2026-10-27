## MODIFIED Requirements

### Requirement: Every Won entry is issued

Issue SHALL run once for each entry that LotteryEntry.PersistDrawOutcome records Won, and once for each Checkout whose order OrderUseCase.Place places. When Issue stops before it ends, it SHALL resume from the step it reached, without charging the card again. When it has not ended 24 hours after it started, it SHALL stop, leaving the entry or the Checkout as it is.

#### Scenario: Won entry
- **WHEN** a draw records an entry Won
- **THEN** Issue runs for it

#### Scenario: Stopped after the charge
- **WHEN** Issue stops after the card was charged and before the Order was stored
- **THEN** it resumes, the card is charged once, and one Order is issued

#### Scenario: Placed checkout
- **WHEN** a fan places the order for their Checkout twice
- **THEN** Issue runs once for the Checkout

### Requirement: A paid order is reported for product analytics

When Issue announces an Order as paid, an "order paid" signal for product analytics SHALL be sent for the fan, carrying the Order, its Event, the ticket count, the amount and currency, whether the Order came from a won LotteryEntry or a Checkout, and the Order's pay time as the time it happened. The signal SHALL be recorded once per Order. A failure to send it SHALL NOT fail or undo the payment.

#### Scenario: Paid lottery win
- **WHEN** the Order of a Won entry for 2 tickets is announced
- **THEN** one order-paid signal is sent with ticket count 2, the amount, the currency and the source LotteryEntry

#### Scenario: Paid checkout
- **WHEN** a fan's Checkout for 2 tickets is paid
- **THEN** one order-paid signal is sent with ticket count 2, the amount, the currency and the source Checkout

## ADDED Requirements

### Requirement: Commit a Checkout, charge it once, then issue

Issue SHALL also take a Checkout and the time its order was placed. When Order.GetByCheckoutID finds an Order for it, it SHALL return that Order and do nothing else. Otherwise, before it commits anything, it SHALL read the Checkout with Checkout.Get, its TicketType and sale with TicketType.Get, and the TicketType's event's Organizer with Event.GetOrganizerID and Organizer.Get for its platform fee rate, returning their failures unchanged with nothing committed or charged. It SHALL then:
1. commit the tickets with Checkout.Commit at the time the order was placed; when Commit reports NotHeld, Issue SHALL end without an Order;
2. for a Committed Checkout without a capture time, charge the card with CardAuthorization.Capture and record the charge with Checkout.RecordCapture. When the capture fails with FailedPrecondition, meaning the card authorization can no longer be charged, it SHALL give the tickets back with Checkout.RevertCommit and end without an Order. When it fails with Unavailable, it SHALL leave the Checkout Committed and try again. A Checkout that already has a capture time SHALL never be charged again;
3. read the captured payment with CardAuthorization.Get for the Checkout's card authorization and build:
   - a Paid Order for the Checkout's user, whose source is the Checkout, with the Checkout's amount in yen, the captured payment's ID as its provider payment ID and the captured payment's card brand and last four digits, and a pay time of the time of issuance;
   - exactly as many Tickets as the Checkout's count, each bound to that user, for the TicketType's event, and Issued at the same time; the Tickets carry no copy of the user's name or phone number;
   - a Held Settlement for the event and its Organizer, with one split paying that Organizer the Order's amount minus the platform fee at the Organizer's rate;
4. store them with Order.Issue. When Order.Issue fails with AlreadyExists, it SHALL return the Order found by Order.GetByCheckoutID. A failure of a read or of Order.Issue after the charge with Unavailable SHALL be tried again.

#### Scenario: Checkout issued
- **WHEN** Issue runs for a holding Checkout for 2 tickets of 3000 yen of an Organizer at 8%
- **THEN** the tickets are committed, 6000 yen is charged, a Paid 6000 yen Order, 2 Issued Tickets bound to the fan and a Held Settlement with one 5520 yen split are created, and the Checkout is Completed

#### Scenario: Hold lapsed in the queue
- **WHEN** the fan placed the order at 18:14:50 for a hold expiring at 18:15, and Issue commits at 18:15:02 while the Checkout is still Held
- **THEN** the tickets are committed with the commit time 18:14:50 and the Order is issued

#### Scenario: Hold already over
- **WHEN** Checkout.Commit reports NotHeld
- **THEN** Issue ends without an Order and nothing is charged

#### Scenario: Card no longer chargeable
- **WHEN** the capture fails with FailedPrecondition
- **THEN** the Checkout is Released, its tickets go back on sale, nothing is charged and Issue ends without an Order

#### Scenario: Payment provider unavailable during capture
- **WHEN** the capture fails with Unavailable for 5 minutes
- **THEN** the Checkout stays Committed, and once the provider answers the card is charged once and the Order is issued

#### Scenario: Charged but never issued
- **WHEN** the card was charged and Order.Issue keeps failing with Unavailable for 24 hours
- **THEN** Issue stops and the Checkout stays Committed with its capture time

### Requirement: IdentityVerification binding for a Checkout

When the Checkout's sale requires verification, Issue SHALL bind every Ticket to the user's IdentityVerification, read with IdentityVerification.GetByUserID whatever its status before the tickets are committed; the name on the Ticket's face stays the user's own full name. When the user has no IdentityVerification, it SHALL fail with that error, commit nothing and charge nothing. When the requirement is None, the Tickets carry no IdentityVerification.

#### Scenario: Verified sale issued
- **WHEN** a Checkout of a sale that requires verification is placed and the user has an IdentityVerification
- **THEN** every Ticket is bound to that IdentityVerification

#### Scenario: No requirement on a first-come sale
- **WHEN** the sale's requirement is None
- **THEN** the Tickets have no IdentityVerification
