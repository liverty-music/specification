# components/usecase/order/issue Specification

## Purpose
OrderUseCase.Issue charges a Won LotteryEntry's card authorization and makes its Pending Order Paid, with its account-bound covered tickets and its Settlement, exactly once.

## Requirements

### Requirement: Every Won entry is issued

Issue SHALL run once for each entry that LotteryEntry.PersistDrawOutcome records Won, and once for each Checkout whose order OrderUseCase.Place places. When Issue stops before it ends, it SHALL resume from the step it reached, without charging the card again. When it has not ended 24 hours after it started, it SHALL stop, leaving the entry or the Checkout and its Order as they are, and an admin SHALL be told.

#### Scenario: Won entry
- **WHEN** a draw records an entry Won
- **THEN** Issue runs for it

#### Scenario: Stopped after the charge
- **WHEN** Issue stops after the card was charged and before the Order was made Paid
- **THEN** it resumes, the card is charged once, and the Order becomes Paid once

#### Scenario: Placed checkout
- **WHEN** a fan places the order for their Checkout twice
- **THEN** Issue runs once for the Checkout

### Requirement: Charge, then issue

Issue SHALL take a LotteryEntry. It SHALL read the entry with LotteryEntry.Get, failing with NotFound when it does not exist, and its Order with Order.Get. When the Order is Paid, it SHALL return that Order and do nothing else. Otherwise, before it charges anything, it SHALL:
- fail with FailedPrecondition when the entry is not Won or its Order is not Pending;
- read the Order's TicketStock with TicketStock.Get and the entry's sale with TicketSale.Get;
- resolve the stock's event's Organizer with Event.GetOrganizerID and read it with Organizer.Get for its platform fee rate.

Any of these failures SHALL be returned unchanged, with nothing charged or changed. It SHALL then charge the Order's card authorization with CardAuthorization.Capture:
- When the capture fails with Unavailable, it SHALL try again.
- When the capture fails with FailedPrecondition, meaning the card authorization can no longer be charged, it SHALL make the entry Lost and its Order Void with LotteryEntry.RevertWin, which announces the entry Lost with the lost reason "card could not be charged", and end without a Paid Order. No loser is promoted (no 繰上げ, promotion of a loser).

After the capture it SHALL read the captured payment with CardAuthorization.Get and, with Order.Issue:
- make the Pending Order Paid, with the payment provider, provider payment ID and card facets of the captured payment, and a pay time of the time of issuance;
- issue exactly as many Tickets as the Order's ticket count, each bound to the Order's user, for the stock's event, and Issued at the same time; the Tickets carry no copy of the user's full name or phone number;
- create a Held Settlement for the event and its Organizer, with one split paying that Organizer the Order's amount minus the platform fee at the Organizer's rate.

When Order.Issue fails with AlreadyExists it SHALL return the Order, Paid by the other run. A failure of a read or of Order.Issue after the charge with Unavailable SHALL be tried again. Order.Issue announces the Order as paid together with making it Paid (components/entity/order/issue), so Issue announces nothing itself and an Issue run again after a stop announces nothing twice.

#### Scenario: Won entry issued
- **WHEN** Issue runs for a Won entry whose Order for 2 tickets has a 16000 yen card authorization, for an Organizer at 5%
- **THEN** the card is charged 16000 yen, the Order becomes Paid, and 2 Issued Tickets bound to the Order's user for the stock's event and a Held Settlement with one 15200 yen split for the event's Organizer are created

#### Scenario: Replayed issuance
- **WHEN** Issue runs again for an entry whose Order is Paid
- **THEN** the Order is returned, the card is not charged again, and no Ticket or Settlement is added

#### Scenario: Concurrent issuance
- **WHEN** Order.Issue fails with AlreadyExists because another run issued the Order first
- **THEN** the Order Paid by the other run is returned

#### Scenario: Entry not won
- **WHEN** the entry is Entered or Lost
- **THEN** Issue fails with FailedPrecondition, charges nothing and changes nothing

#### Scenario: Payment provider unavailable
- **WHEN** CardAuthorization.Capture fails with Unavailable and succeeds 10 minutes later
- **THEN** the card is charged once and the Order becomes Paid

#### Scenario: Payment provider unavailable for a day
- **WHEN** CardAuthorization.Capture fails with Unavailable for 24 hours
- **THEN** Issue stops, the entry stays Won with its Order Pending, nothing is charged, and an admin is told

#### Scenario: Card authorization no longer chargeable
- **WHEN** CardAuthorization.Capture fails with FailedPrecondition
- **THEN** the entry is Lost with the lost reason "card could not be charged", its Order is Void, nothing is charged, and the entry is announced Lost

#### Scenario: Organizer unresolved
- **WHEN** Event.GetOrganizerID fails with NotFound
- **THEN** Issue fails with NotFound, nothing is charged and nothing changes

### Requirement: Identity verification binding

When the entry's sale requires verification, Issue SHALL bind every Ticket to the user's IdentityVerification, read with IdentityVerification.GetByUserID whatever its status, before the charge; the name on the Ticket's face stays the user's own full name. When the user has no IdentityVerification, it SHALL fail with that error, charge nothing and change nothing.

#### Scenario: Sale required verification
- **WHEN** the sale requires JPKI-only and the user has an IdentityVerification
- **THEN** every Ticket is bound to that IdentityVerification and its face shows the user's full name

#### Scenario: Identity verification missing
- **WHEN** the sale requires verification and IdentityVerification.GetByUserID fails with NotFound
- **THEN** Issue fails with NotFound, charges nothing and changes nothing

#### Scenario: No requirement
- **WHEN** the sale's requirement is None
- **THEN** the Tickets have no IdentityVerification

### Requirement: Commit a Checkout, charge it once, then issue

Issue SHALL also take a Checkout. It SHALL read the Checkout with Checkout.Get and its Order with Order.Get; when the Order is Paid it SHALL return it and do nothing else. Otherwise, before it commits anything, it SHALL read the Order's TicketStock with TicketStock.Get, the Checkout's sale with TicketSale.Get, and the stock's event's Organizer with Event.GetOrganizerID and Organizer.Get for its platform fee rate, returning their failures unchanged with nothing committed or charged. It SHALL then:
1. commit the tickets with Checkout.Commit at the time it commits, never an earlier time, so a hold that lapsed meanwhile is not committed after its tickets went to another fan; when Commit reports NotHeld, Issue SHALL end without a Paid Order, the Order staying Pending until the Checkout's expiry makes it Void;
2. for a Committed Checkout without a capture time, charge the Order's card authorization with CardAuthorization.Capture and record the charge with Checkout.RecordCapture. When the capture fails with FailedPrecondition, meaning the card authorization can no longer be charged, it SHALL give the tickets back with Checkout.RevertCommit, which makes the Order Void, and end. When it fails with Unavailable, it SHALL leave the Checkout Committed and try again. A Checkout that already has a capture time SHALL never be charged again;
3. read the captured payment with CardAuthorization.Get and, with Order.Issue:
   - make the Pending Order Paid, with the captured payment's ID as its provider payment ID, the captured payment's card brand and last four digits, and a pay time of the time of issuance;
   - issue exactly as many Tickets as the Order's ticket count, each bound to the Order's user, for the stock's event, and Issued at the same time; the Tickets carry no copy of the user's name or phone number;
   - create a Held Settlement for the event and its Organizer, with one split paying that Organizer the Order's amount minus the platform fee at the Organizer's rate;
   When Order.Issue fails with AlreadyExists, it SHALL return the Order, Paid by an earlier step. A failure of a read or of Order.Issue after the charge with Unavailable SHALL be tried again.

Order.Issue announces the Order as paid together with making it Paid, as for a Won entry, so Issue announces nothing itself.

#### Scenario: Checkout issued
- **WHEN** Issue runs for a holding Checkout whose Order is for 2 tickets of a SeatType priced 3000 yen, of an Organizer at 8%
- **THEN** the tickets are committed, 6000 yen is charged, the 6000 yen Order becomes Paid, 2 Issued Tickets bound to the fan and a Held Settlement with one 5520 yen split are created, and the Checkout is Completed

#### Scenario: Hold already over
- **WHEN** the hold lapsed while Issue waited in the queue, so Checkout.Commit reports NotHeld
- **THEN** Issue ends, nothing is charged and the Order is not Paid

#### Scenario: Card no longer chargeable
- **WHEN** the capture fails with FailedPrecondition
- **THEN** the Checkout is Released, its Order is Void, its tickets go back on sale, nothing is charged and Issue ends

#### Scenario: Payment provider unavailable during capture
- **WHEN** the capture fails with Unavailable for 5 minutes
- **THEN** the Checkout stays Committed, and once the provider answers the card is charged once and the Order becomes Paid

#### Scenario: Charged but never issued
- **WHEN** the card was charged and Order.Issue keeps failing with Unavailable for 24 hours
- **THEN** Issue stops, the Checkout stays Committed with its capture time and the Order stays Pending

### Requirement: IdentityVerification binding for a Checkout

When the Checkout's sale requires verification, Issue SHALL bind every Ticket to the user's IdentityVerification, read with IdentityVerification.GetByUserID whatever its status before the tickets are committed; the name on the Ticket's face stays the user's own full name. When the user has no IdentityVerification, it SHALL fail with that error, commit nothing and charge nothing. When the requirement is None, the Tickets carry no IdentityVerification.

#### Scenario: Verified sale issued
- **WHEN** a Checkout of a sale that requires verification is placed and the user has an IdentityVerification
- **THEN** every Ticket is bound to that IdentityVerification

#### Scenario: No requirement on a first-come sale
- **WHEN** the sale's requirement is None
- **THEN** the Tickets have no IdentityVerification
