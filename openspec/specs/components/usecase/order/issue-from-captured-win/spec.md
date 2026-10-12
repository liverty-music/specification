# OrderUseCase.IssueFromCapturedWin

## Purpose

OrderUseCase.IssueFromCapturedWin turns one Won TicketApplication into a Paid Order and its account-bound covered tickets, exactly once.

## Requirements

### Requirement: Issue an order and its tickets from a won application

IssueFromCapturedWin SHALL take a LotteryEntry. When Order.GetByLotteryEntryID finds an Order for it, it SHALL return that Order and issue nothing. Otherwise it SHALL read the entry with LotteryEntry.Get, failing with NotFound when it does not exist, and fail with FailedPrecondition, creating nothing, when the entry is not Won. It SHALL read the entry's TicketType and its sale with TicketType.Get and the entry's card authorization with CardAuthorization.Get, returning their failures unchanged, and fail with FailedPrecondition, creating nothing, when the card authorization is not Captured; it never charges the card. It SHALL resolve the TicketType's event's Organizer with Event.GetOrganizerID and read it with Organizer.Get for its platform fee rate, returning their failures unchanged and creating nothing. It SHALL build:
- a Paid Order for the entry's user, whose source is the entry, whose amount, currency, payment provider and card facets are those of the card authorization's captured payment, and whose pay time is the time of issuance;
- exactly as many Tickets as the entry's ticket count, each bound to the entry's user, for the TicketType's event, and Issued at the same time; the Tickets carry no copy of the user's full name or phone number;
- a Held Settlement for the TicketType's event and its Organizer, with one split paying that Organizer the Order's amount minus the platform fee at the Organizer's rate.

It SHALL store them with Order.Issue; when Order.Issue fails with AlreadyExists it SHALL return the Order found by Order.GetByLotteryEntryID.

#### Scenario: Won application issued

- **WHEN** IssueFromCapturedWin runs for a Won entry for 2 tickets whose 16000 yen payment was captured, for an Organizer at 5%
- **THEN** a Paid 16000 yen Order, 2 Issued Tickets bound to the entry's user for the TicketType's event, and a Held Settlement with one 15200 yen split for the event's Organizer are created, and the Order is returned

#### Scenario: Replayed issuance

- **WHEN** IssueFromCapturedWin runs again for an entry that already has an Order
- **THEN** the existing Order is returned and no Order, Ticket or Settlement is added

#### Scenario: Concurrent issuance

- **WHEN** Order.Issue fails with AlreadyExists because another run issued the entry first
- **THEN** the Order created by the other run is returned

#### Scenario: Application not won

- **WHEN** the entry is Draft, Entered, Lost or Withdrawn
- **THEN** IssueFromCapturedWin fails with FailedPrecondition and creates no Order, Ticket or Settlement

#### Scenario: Payment not captured

- **WHEN** CardAuthorization.Get returns the entry's card authorization Authorized or Released, not Captured
- **THEN** IssueFromCapturedWin fails with FailedPrecondition and creates nothing

#### Scenario: Organizer unresolved

- **WHEN** Event.GetOrganizerID fails with NotFound
- **THEN** IssueFromCapturedWin fails with NotFound and creates nothing

### Requirement: Identity verification binding

When the entry's sale requires verification, IssueFromCapturedWin SHALL bind every Ticket to the user's IdentityVerification, read with IdentityVerification.GetByUserID whatever its status; the name on the Ticket's face stays the user's own full name. When the user has no IdentityVerification, it SHALL fail with that error and create nothing.

#### Scenario: Phase required verification

- **WHEN** the sale requires JPKI-only and the user has an IdentityVerification
- **THEN** every Ticket is bound to that IdentityVerification and its face shows the user's full name

#### Scenario: Identity verification missing

- **WHEN** the sale requires verification and IdentityVerification.GetByUserID fails with NotFound
- **THEN** IssueFromCapturedWin fails with NotFound and creates nothing

#### Scenario: No requirement

- **WHEN** the sale's requirement is None
- **THEN** the Tickets have no IdentityVerification
