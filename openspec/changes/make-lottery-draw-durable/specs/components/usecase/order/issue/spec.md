## Purpose

OrderUseCase.Issue charges a Won LotteryEntry's card authorization and turns the entry into a Paid Order with its account-bound covered tickets and its Settlement, exactly once.

## ADDED Requirements

### Requirement: Every Won entry is issued

Issue SHALL run for each entry that LotteryEntry.RecordDrawOutcome records Won, starting within 1 minute after it is recorded. When Issue stops before it ends, it SHALL resume from the step it reached, without charging the card again.

#### Scenario: Won entry
- **WHEN** a draw records an entry Won
- **THEN** within 1 minute Issue runs for it

#### Scenario: Stopped after the charge
- **WHEN** Issue stops after the card was charged and before the Order was stored
- **THEN** it resumes, the card is charged once, and one Order is issued

### Requirement: Charge, then issue

Issue SHALL take a LotteryEntry. When Order.GetByLotteryEntryID finds an Order for it, it SHALL return that Order and do nothing else. Otherwise it SHALL read the entry with LotteryEntry.Get, failing with NotFound when it does not exist, and fail with FailedPrecondition, charging and creating nothing, when the entry is not Won. It SHALL then charge the entry's card authorization with CardAuthorization.Capture:
- When the capture fails with Unavailable, it SHALL try again at growing intervals for up to 24 hours; when it still fails, it SHALL stop, leave the entry Won and report the entry for an admin.
- When the capture fails with FailedPrecondition, meaning the card authorization can no longer be charged, it SHALL make the entry Lost with LotteryEntry.RevertWin, release the card authorization with CardAuthorization.Release, send a "lottery result" signal for product analytics with the result Lost from a failed capture, and fail with FailedPrecondition. No loser is promoted (no 繰上げ, promotion of a loser).

After the capture it SHALL read the card authorization's captured payment with CardAuthorization.Get, read the entry's TicketType and its sale with TicketType.Get, and resolve the TicketType's event's Organizer with Event.GetOrganizerID and Organizer.Get for its platform fee rate, returning their failures unchanged and creating nothing. It SHALL build:
- a Paid Order for the entry's user, whose source is the entry, whose amount, currency, payment provider and card facets are those of the captured payment, and whose pay time is the time of issuance;
- exactly as many Tickets as the entry's ticket count, each bound to the entry's user, for the TicketType's event, and Issued at the same time; the Tickets carry no copy of the user's full name or phone number;
- a Held Settlement for the TicketType's event and its Organizer, with one split paying that Organizer the Order's amount minus the platform fee at the Organizer's rate.

It SHALL store them with Order.Issue; when Order.Issue fails with AlreadyExists it SHALL return the Order found by Order.GetByLotteryEntryID.

#### Scenario: Won entry issued
- **WHEN** Issue runs for a Won entry for 2 tickets with a 16000 yen card authorization, for an Organizer at 5%
- **THEN** the card is charged 16000 yen, and a Paid 16000 yen Order, 2 Issued Tickets bound to the entry's user for the TicketType's event, and a Held Settlement with one 15200 yen split for the event's Organizer are created

#### Scenario: Replayed issuance
- **WHEN** Issue runs again for an entry that already has an Order
- **THEN** the existing Order is returned, the card is not charged again, and no Order, Ticket or Settlement is added

#### Scenario: Concurrent issuance
- **WHEN** Order.Issue fails with AlreadyExists because another run issued the entry first
- **THEN** the Order created by the other run is returned

#### Scenario: Entry not won
- **WHEN** the entry is Draft, Entered or Lost
- **THEN** Issue fails with FailedPrecondition, charges nothing and creates no Order, Ticket or Settlement

#### Scenario: Payment provider unavailable
- **WHEN** CardAuthorization.Capture fails with Unavailable and succeeds 10 minutes later
- **THEN** the card is charged once and the Order is issued

#### Scenario: Payment provider unavailable for a day
- **WHEN** CardAuthorization.Capture fails with Unavailable for 24 hours
- **THEN** Issue stops, the entry stays Won with no Order, and the entry is reported for an admin

#### Scenario: Card authorization no longer chargeable
- **WHEN** CardAuthorization.Capture fails with FailedPrecondition
- **THEN** the entry is Lost, its card authorization is released, nothing is charged, no Order is created, and a Lost signal from a failed capture is sent

#### Scenario: Organizer unresolved
- **WHEN** Event.GetOrganizerID fails with NotFound
- **THEN** Issue fails with NotFound and creates nothing

### Requirement: Identity verification binding

When the entry's sale requires verification, Issue SHALL bind every Ticket to the user's IdentityVerification, read with IdentityVerification.GetByUserID whatever its status; the name on the Ticket's face stays the user's own full name. When the user has no IdentityVerification, it SHALL fail with that error and create nothing.

#### Scenario: Sale required verification
- **WHEN** the sale requires JPKI-only and the user has an IdentityVerification
- **THEN** every Ticket is bound to that IdentityVerification and its face shows the user's full name

#### Scenario: Identity verification missing
- **WHEN** the sale requires verification and IdentityVerification.GetByUserID fails with NotFound
- **THEN** Issue fails with NotFound and creates nothing

### Requirement: The paid Order is announced

After Order.Issue stores the Order, or when Issue finds it stored by an earlier run that had not announced it, Issue SHALL announce that the Order is paid, carrying the Order, its user, its event, its number of Tickets, its amount and its source. When announcing fails, Issue SHALL try again until it succeeds. A run that resumes can announce the same Order again; consumers that act on the Order SHALL treat a repeated announcement of an Order as one.

#### Scenario: Order announced
- **WHEN** Issue stores the Order of a Won entry
- **THEN** the Order is announced as paid once

#### Scenario: Messaging unavailable
- **WHEN** announcing the Order fails
- **THEN** Issue tries again and the Order is announced when messaging is back, with no second Order

### Requirement: A paid order is reported for product analytics

When Issue announces an Order as paid, an "order paid" signal for product analytics SHALL be sent for the fan, carrying the Order, its Event, the ticket count, the amount and currency, that the Order came from a won LotteryEntry, and the Order's pay time as the time it happened. A redelivery of the same announcement SHALL be recorded once. A failure to send it SHALL NOT fail or undo the payment.

#### Scenario: Paid lottery win
- **WHEN** the Order of a Won entry for 2 tickets is announced
- **THEN** one order-paid signal is sent with ticket count 2, the amount, the currency and the source LotteryEntry
