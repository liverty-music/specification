# IssuanceUseCase.IssueFromCapturedWin

## Purpose

IssuanceUseCase.IssueFromCapturedWin turns one Won TicketApplication into a Paid Order and its account-bound covered tickets, exactly once, and marks the buyer's ticket journey for the event as Paid.

## Requirements

### Requirement: Issue an order and its tickets from a won application

IssueFromCapturedWin SHALL take an application. When Order.GetByApplicationID finds an Order for it, it SHALL return that Order and issue nothing. Otherwise it SHALL read the application with TicketApplication.Get, failing with NotFound when it does not exist, and fail with FailedPrecondition, creating nothing, when the application is not Won. It SHALL read the phase with LotterySalesPhase.Get and the captured payment with Order.GetCapturedPayment, returning their failures unchanged; it never charges the card. It SHALL build a Paid Order for the applicant whose amount, currency, payment service and card facets are those of the captured payment and whose paid time is the time of issuance, and exactly as many Tickets as the requested ticket count, each bound to the applicant, for the phase's event, carrying the applicant's full name and phone number, Issued at the same time. It SHALL store them with Order.Issue; when Order.Issue fails with AlreadyExists it SHALL return the Order found by Order.GetByApplicationID.

#### Scenario: Won application issued

- **WHEN** IssueFromCapturedWin runs for a Won application for 2 tickets whose 16000 yen payment was captured
- **THEN** a Paid 16000 yen Order and 2 Issued Tickets bound to the applicant, for the phase's event, are created and the Order is returned

#### Scenario: Replayed issuance

- **WHEN** IssueFromCapturedWin runs again for an application that already has an Order
- **THEN** the existing Order is returned and no Order or Ticket is added

#### Scenario: Concurrent issuance

- **WHEN** Order.Issue fails with AlreadyExists because another run issued the application first
- **THEN** the Order created by the other run is returned

#### Scenario: Application not won

- **WHEN** the application is Applied, Lost or Withdrawn
- **THEN** IssueFromCapturedWin fails with FailedPrecondition and creates no Order or Ticket

#### Scenario: Payment not captured

- **WHEN** Order.GetCapturedPayment fails with FailedPrecondition
- **THEN** IssueFromCapturedWin fails with FailedPrecondition and creates nothing

### Requirement: Verified identity binding

When the phase requires verification, IssueFromCapturedWin SHALL bind every Ticket to the applicant's verified identity, read with VerifiedIdentity.GetByUserID whatever its status; the holder name on the Ticket stays the applicant's declared name. When the applicant has no verified identity, it SHALL fail with that error and create nothing.

#### Scenario: Phase required verification

- **WHEN** the phase requires JPKI-only and the applicant has a verified identity
- **THEN** every Ticket is bound to that verified identity and shows the applicant's declared name

#### Scenario: Verified identity missing

- **WHEN** the phase requires verification and VerifiedIdentity.GetByUserID fails with NotFound
- **THEN** IssueFromCapturedWin fails with NotFound and creates nothing

#### Scenario: No requirement

- **WHEN** the phase's requirement is None
- **THEN** the Tickets have no verified identity

### Requirement: Ticket journey becomes Paid

After the Order is stored, IssueFromCapturedWin SHALL set the buyer's TicketJourney for the phase's event to Paid with TicketJourney.Upsert, replacing whatever status the fan had set, and SHALL NOT announce the change as a ticket journey status change. When that fails, the Order and Tickets stay issued and the Order is still returned.

#### Scenario: Journey updated

- **WHEN** an Order is issued
- **THEN** the buyer's ticket journey for the event is Paid

#### Scenario: Journey update fails

- **WHEN** TicketJourney.Upsert fails
- **THEN** the Order and its Tickets remain and the Order is returned
