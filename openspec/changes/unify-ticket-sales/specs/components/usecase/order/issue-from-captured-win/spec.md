# Spec Delta

## MODIFIED Requirements

### Requirement: Issue an order and its tickets from a won application

IssueFromCapturedWin SHALL take a LotteryEntry. When Order.GetByLotteryEntryID finds an Order for it, it SHALL return that Order and issue nothing. Otherwise it SHALL read the entry with LotteryEntry.Get, failing with NotFound when it does not exist, and fail with FailedPrecondition, creating nothing, when the entry is not Won. It SHALL read the entry's TicketType and its sale with TicketType.Get and the captured payment with Order.GetCapturedPayment, returning their failures unchanged; it never charges the card. It SHALL resolve the TicketType's event's Organizer with Event.GetOrganizerID, returning its failure unchanged and creating nothing. It SHALL build a Paid Order for the entry's user whose amount, currency, payment service and card facets are those of the captured payment and whose paid time is the time of issuance, exactly as many Tickets as the requested ticket count, each bound to that user, for the TicketType's event, Issued at the same time, and a Held Settlement for that event and its Organizer with one split paying that Organizer the Order's amount minus the platform fee (a flat 5% of the Order's amount, rounded down). The Tickets carry no copy of the user's name or phone number. It SHALL store them with Order.Issue; when Order.Issue fails with AlreadyExists it SHALL return the Order found by Order.GetByLotteryEntryID.

#### Scenario: Won application issued
- **WHEN** IssueFromCapturedWin runs for a Won entry for 2 tickets whose 16000 yen payment was captured
- **THEN** a Paid 16000 yen Order, 2 Issued Tickets bound to the entry's user for the TicketType's event, and a Held Settlement with one 15200 yen split for the event's Organizer are created and the Order is returned

#### Scenario: Replayed issuance
- **WHEN** IssueFromCapturedWin runs again for an entry that already has an Order
- **THEN** the existing Order is returned and no Order, Ticket or Settlement is added

#### Scenario: Concurrent issuance
- **WHEN** Order.Issue fails with AlreadyExists because another run issued the entry first
- **THEN** the Order created by the other run is returned

#### Scenario: Application not won
- **WHEN** the entry is Entered, Lost or Withdrawn
- **THEN** IssueFromCapturedWin fails with FailedPrecondition and creates no Order, Ticket or Settlement

#### Scenario: Payment not captured
- **WHEN** Order.GetCapturedPayment fails with FailedPrecondition
- **THEN** IssueFromCapturedWin fails with FailedPrecondition and creates nothing

#### Scenario: Organizer unresolved
- **WHEN** Event.GetOrganizerID fails with NotFound
- **THEN** IssueFromCapturedWin fails with NotFound and creates nothing

### Requirement: Verified identity binding

When the entry's sale requires verification, IssueFromCapturedWin SHALL bind every Ticket to the user's verified identity, read with VerifiedIdentity.GetByUserID whatever its status; the name on the Ticket's face stays the user's own full name. When the user has no verified identity, it SHALL fail with that error and create nothing.

#### Scenario: Phase required verification
- **WHEN** the sale requires JPKI-only and the user has a verified identity
- **THEN** every Ticket is bound to that verified identity and its face shows the user's full name

#### Scenario: Verified identity missing
- **WHEN** the sale requires verification and VerifiedIdentity.GetByUserID fails with NotFound
- **THEN** IssueFromCapturedWin fails with NotFound and creates nothing

#### Scenario: No requirement
- **WHEN** the sale's requirement is None
- **THEN** the Tickets have no verified identity

### Requirement: Ticket journey becomes Paid

After the Order is stored, IssueFromCapturedWin SHALL set the user's TicketJourney for the TicketType's event to Paid with TicketJourney.Upsert, replacing whatever status the fan had set, and SHALL NOT announce the change as a ticket journey status change. When that fails, the Order and Tickets stay issued and the Order is still returned.

#### Scenario: Journey updated
- **WHEN** an Order is issued
- **THEN** the user's ticket journey for the event is Paid

#### Scenario: Journey update fails
- **WHEN** TicketJourney.Upsert fails
- **THEN** the Order and its Tickets remain and the Order is returned
