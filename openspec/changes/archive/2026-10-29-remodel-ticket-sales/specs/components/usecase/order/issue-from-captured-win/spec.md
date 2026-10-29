# Spec Delta

## ADDED Requirements

### Requirement: Pay a won entry's order and issue its tickets

IssueFromCapturedWin SHALL take a LotteryEntry. It SHALL read the entry with LotteryEntry.Get and its Order with Order.Get, failing with NotFound when the entry does not exist. When the Order is Paid, it SHALL return that Order and issue nothing. Otherwise it SHALL fail with FailedPrecondition, changing nothing, when the entry is not Won. It SHALL read the Order's TicketStock with TicketStock.Get, the entry's sale with TicketSale.Get and the Order's card authorization with CardAuthorization.Get, returning their failures unchanged, and fail with FailedPrecondition, changing nothing, when the card authorization is not Captured; it never charges the card. It SHALL resolve the stock's event's Organizer with Event.GetOrganizerID and read it with Organizer.Get for its platform fee rate, returning their failures unchanged and changing nothing. It SHALL then, with Order.Issue:
- make the Pending Order Paid, with the payment provider, provider payment ID and card facets of the card authorization's captured payment, and a pay time of the time of issuance;
- issue exactly as many Tickets as the Order's ticket count, each bound to the Order's user, for the stock's event, and Issued at the same time; the Tickets carry no copy of the user's full name or phone number;
- create a Held Settlement for the event and its Organizer, with one split paying that Organizer the Order's amount minus the platform fee at the Organizer's rate.

When Order.Issue fails with AlreadyExists it SHALL return the Order, Paid by the other run.

#### Scenario: Won entry issued

- **WHEN** IssueFromCapturedWin runs for a Won entry whose Order for 2 tickets has a captured 16000 yen payment, for an Organizer at 5%
- **THEN** the Order becomes Paid, 2 Issued Tickets bound to the Order's user for the stock's event and a Held Settlement with one 15200 yen split for the event's Organizer are created, and the Order is returned

#### Scenario: Replayed issuance

- **WHEN** IssueFromCapturedWin runs again for an entry whose Order is Paid
- **THEN** the Order is returned and no Ticket or Settlement is added

#### Scenario: Concurrent issuance

- **WHEN** Order.Issue fails with AlreadyExists because another run issued the Order first
- **THEN** the Order Paid by the other run is returned

#### Scenario: Entry not won

- **WHEN** the entry is Entered or Lost
- **THEN** IssueFromCapturedWin fails with FailedPrecondition and changes nothing

#### Scenario: Payment not captured

- **WHEN** CardAuthorization.Get returns the Order's card authorization Authorized or Released, not Captured
- **THEN** IssueFromCapturedWin fails with FailedPrecondition and changes nothing

#### Scenario: Organizer unresolved

- **WHEN** Event.GetOrganizerID fails with NotFound
- **THEN** IssueFromCapturedWin fails with NotFound and changes nothing

## REMOVED Requirements

### Requirement: Issue an order and its tickets from a won entry

**Reason**: The entry's Order exists from the entry on, Pending; issuance makes it Paid instead of creating it.
**Migration**: See "Pay a won entry's order and issue its tickets".
