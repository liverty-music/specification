## Purpose

OrderUseCase.Issue charges a Won LotteryEntry's card authorization and makes its Pending Order Paid, with its account-bound covered tickets and its Settlement, exactly once.

## ADDED Requirements

### Requirement: Every Won entry is issued

Issue SHALL run once for each entry that LotteryEntry.PersistDrawOutcome records Won. When Issue stops before it ends, it SHALL resume from the step it reached, without charging the card again. When it has not ended 24 hours after it started, it SHALL stop, leaving the entry and its Order as they are, and an admin SHALL be told.

#### Scenario: Won entry
- **WHEN** a draw records an entry Won
- **THEN** Issue runs for it

#### Scenario: Stopped after the charge
- **WHEN** Issue stops after the card was charged and before the Order was made Paid
- **THEN** it resumes, the card is charged once, and the Order becomes Paid once

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
