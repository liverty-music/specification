## Purpose

OrderUseCase.Issue charges a Won LotteryEntry's card authorization and turns the entry into a Paid Order with its account-bound covered tickets and its Settlement, exactly once.

## ADDED Requirements

### Requirement: Every Won entry is issued

Issue SHALL run once for each entry that LotteryEntry.PersistDrawOutcome records Won. When Issue stops before it ends, it SHALL resume from the step it reached, without charging the card again. When it has not ended 24 hours after it started, it SHALL stop, leaving the entry as it is.

#### Scenario: Won entry
- **WHEN** a draw records an entry Won
- **THEN** Issue runs for it

#### Scenario: Stopped after the charge
- **WHEN** Issue stops after the card was charged and before the Order was stored
- **THEN** it resumes, the card is charged once, and one Order is issued

### Requirement: Charge, then issue

Issue SHALL take a LotteryEntry. When Order.GetByLotteryEntryID finds an Order for it, it SHALL return that Order and do nothing else. Otherwise, before it charges anything, it SHALL:
- read the entry with LotteryEntry.Get, failing with NotFound when it does not exist, and fail with FailedPrecondition when the entry is not Won;
- read the entry's TicketType and its sale with TicketType.Get;
- resolve the TicketType's event's Organizer with Event.GetOrganizerID and read it with Organizer.Get for its platform fee rate.

Any of these failures SHALL be returned unchanged, with nothing charged or created. It SHALL then charge the entry's card authorization with CardAuthorization.Capture:
- When the capture fails with Unavailable, it SHALL try again.
- When the capture fails with FailedPrecondition, meaning the card authorization can no longer be charged, it SHALL make the entry Lost with LotteryEntry.RevertWin, announce the entry's lottery result Lost from a failed capture, and end without an Order. No loser is promoted (no 繰上げ, promotion of a loser).

After the capture it SHALL read the captured payment with CardAuthorization.Get for the entry's card authorization and build:
- a Paid Order for the entry's user, whose source is the entry, whose amount, currency, payment provider and card facets are those of the captured payment, and whose pay time is the time of issuance;
- exactly as many Tickets as the entry's ticket count, each bound to the entry's user, for the TicketType's event, and Issued at the same time; the Tickets carry no copy of the user's full name or phone number;
- a Held Settlement for the TicketType's event and its Organizer, with one split paying that Organizer the Order's amount minus the platform fee at the Organizer's rate.

It SHALL store them with Order.Issue; when Order.Issue fails with AlreadyExists it SHALL return the Order found by Order.GetByLotteryEntryID. A failure of a read or of Order.Issue after the charge with Unavailable SHALL be tried again.

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
- **WHEN** the entry is Entered or Lost
- **THEN** Issue fails with FailedPrecondition, charges nothing and creates no Order, Ticket or Settlement

#### Scenario: Payment provider unavailable
- **WHEN** CardAuthorization.Capture fails with Unavailable and succeeds 10 minutes later
- **THEN** the card is charged once and the Order is issued

#### Scenario: Payment provider unavailable for a day
- **WHEN** CardAuthorization.Capture fails with Unavailable for 24 hours
- **THEN** Issue stops, the entry stays Won with no Order, and nothing is charged

#### Scenario: Card authorization no longer chargeable
- **WHEN** CardAuthorization.Capture fails with FailedPrecondition
- **THEN** the entry is Lost, nothing is charged, no Order is created, and a Lost result from a failed capture is announced

#### Scenario: Organizer unresolved
- **WHEN** Event.GetOrganizerID fails with NotFound
- **THEN** Issue fails with NotFound, nothing is charged and nothing is created

### Requirement: Identity verification binding

When the entry's sale requires verification, Issue SHALL bind every Ticket to the user's IdentityVerification, read with IdentityVerification.GetByUserID whatever its status, before the charge; the name on the Ticket's face stays the user's own full name. When the user has no IdentityVerification, it SHALL fail with that error, charge nothing and create nothing.

#### Scenario: Sale required verification
- **WHEN** the sale requires JPKI-only and the user has an IdentityVerification
- **THEN** every Ticket is bound to that IdentityVerification and its face shows the user's full name

#### Scenario: Identity verification missing
- **WHEN** the sale requires verification and IdentityVerification.GetByUserID fails with NotFound
- **THEN** Issue fails with NotFound, charges nothing and creates nothing

#### Scenario: No requirement
- **WHEN** the sale's requirement is None
- **THEN** the Tickets have no IdentityVerification

### Requirement: The paid Order is announced

After Order.Issue stores the Order, Issue SHALL announce that the Order is paid, carrying the Order, its user, its event, its number of Tickets, its amount and its source. When announcing fails, Issue SHALL try again. An announcement made again after a stop is the same announcement, so the Order is announced once.

#### Scenario: Order announced
- **WHEN** Issue stores the Order of a Won entry
- **THEN** the Order is announced as paid once

#### Scenario: Messaging unavailable
- **WHEN** announcing the Order fails
- **THEN** Issue tries again and the Order is announced when messaging is back, with no second Order

### Requirement: A paid order is reported for product analytics

When Issue announces an Order as paid, an "order paid" signal for product analytics SHALL be sent for the fan, carrying the Order, its Event, the ticket count, the amount and currency, that the Order came from a won LotteryEntry, and the Order's pay time as the time it happened. The signal SHALL be recorded once per Order. A failure to send it SHALL NOT fail or undo the payment.

#### Scenario: Paid lottery win
- **WHEN** the Order of a Won entry for 2 tickets is announced
- **THEN** one order-paid signal is sent with ticket count 2, the amount, the currency and the source LotteryEntry
