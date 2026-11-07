## MODIFIED Requirements

### Requirement: Charge, then issue

Issue SHALL take a LotteryEntry. It SHALL read the entry with LotteryEntry.Get, failing with NotFound when it does not exist, and its Order with Order.Get. When the Order is Paid, it SHALL return that Order and do nothing else. Otherwise, before it charges anything, it SHALL:
- fail with FailedPrecondition when the entry is not Won or its Order is not Pending;
- read the Order's TicketStock with TicketStock.Get and the entry's sale with TicketSale.Get;
- resolve the stock's event's Organizer with Event.GetOrganizerID and read it with Organizer.Get for its platform fee rate.

Any of these failures SHALL be returned unchanged, with nothing charged or changed. It SHALL then charge the Order's card authorization with CardAuthorization.Capture, first checking with Event.IsEventPublished, before every attempt, that the stock's event is PUBLISHED:
- When it is not, as for a 中止 (cancelled) concert, it SHALL read the card authorization with CardAuthorization.Get, since an earlier attempt that failed with Unavailable may have charged it; a failure of that read with Unavailable SHALL be tried again. When it is Captured, Issue SHALL go on as after a successful charge, so the Order is Paid and a cancellation refund reaches it. Otherwise it SHALL charge nothing, make the entry Lost and its Order Void with LotteryEntry.RevertWin and the lost reason "concert cancelled", and end without a Paid Order; the card authorization is then released and the fan told from that announcement. Issue SHALL never make the entry Lost while a charge of its Order stands, so no fan is charged without tickets.
- When the capture fails with Unavailable, it SHALL try again.
- When the capture fails with FailedPrecondition, meaning the card authorization can no longer be charged, it SHALL make the entry Lost and its Order Void with LotteryEntry.RevertWin and the lost reason "card could not be charged", which announces the entry Lost with that reason, and end without a Paid Order. No loser is promoted (no 繰上げ, promotion of a loser).

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

#### Scenario: Lottery concert cancelled before the charge
- **WHEN** a Won lottery entry is issued after its concert was cancelled
- **THEN** nothing is charged, the entry is Lost with the lost reason "concert cancelled", its Order is Void and its card authorization is released

#### Scenario: Concert cancelled while the payment provider is unavailable
- **WHEN** CardAuthorization.Capture fails with Unavailable, charging nothing, and the concert is cancelled before the next attempt
- **THEN** nothing is charged and the entry is Lost with the lost reason "concert cancelled"

#### Scenario: Earlier attempt charged, then concert cancelled
- **WHEN** CardAuthorization.Capture fails with Unavailable although the card was charged, and the concert is cancelled before the next attempt
- **THEN** the card is not charged again, the Order becomes Paid with its Tickets, and the entry stays Won

#### Scenario: Organizer unresolved
- **WHEN** Event.GetOrganizerID fails with NotFound
- **THEN** Issue fails with NotFound, nothing is charged and nothing changes
