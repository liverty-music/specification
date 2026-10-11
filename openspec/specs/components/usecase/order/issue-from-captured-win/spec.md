# IssuanceUseCase.IssueFromCapturedWin

## Purpose

IssuanceUseCase.IssueFromCapturedWin turns one Won TicketApplication into a Paid Order and its account-bound covered tickets, exactly once.

## Requirements

### Requirement: Issue an order and its tickets from a won application

IssueFromCapturedWin SHALL take an application. When Order.GetByApplicationID finds an Order for it, it SHALL return that Order and issue nothing. Otherwise it SHALL read the application with TicketApplication.Get, failing with NotFound when it does not exist, and fail with FailedPrecondition, creating nothing, when the application is not Won. It SHALL read the phase with LotterySalesPhase.Get and the captured payment with Order.GetCapturedPayment, returning their failures unchanged; it never charges the card. It SHALL resolve the phase's event's Organizer with Event.GetOrganizerID and read it with Organizer.Get for its platform fee rate, returning their failures unchanged and creating nothing. It SHALL build:
- a Paid Order for the applicant, whose source is the application, whose amount, currency, payment service and card facets are those of the captured payment, and whose paid time is the time of issuance;
- exactly as many Tickets as the requested ticket count, each bound to the applicant, for the phase's event, carrying the applicant's full name and phone number, and Issued at the same time;
- a Held Settlement for the phase's event and its Organizer, with one split paying that Organizer the Order's amount minus the platform fee at the Organizer's rate.

It SHALL store them with Order.Issue; when Order.Issue fails with AlreadyExists it SHALL return the Order found by Order.GetByApplicationID.

#### Scenario: Won application issued

- **WHEN** IssueFromCapturedWin runs for a Won application for 2 tickets whose 16000 yen payment was captured, for an Organizer at 5%
- **THEN** a Paid 16000 yen Order, 2 Issued Tickets bound to the applicant for the phase's event, and a Held Settlement with one 15200 yen split for the event's Organizer are created, and the Order is returned

#### Scenario: Replayed issuance

- **WHEN** IssueFromCapturedWin runs again for an application that already has an Order
- **THEN** the existing Order is returned and no Order, Ticket or Settlement is added

#### Scenario: Concurrent issuance

- **WHEN** Order.Issue fails with AlreadyExists because another run issued the application first
- **THEN** the Order created by the other run is returned

#### Scenario: Application not won

- **WHEN** the application is Applied, Lost or Withdrawn
- **THEN** IssueFromCapturedWin fails with FailedPrecondition and creates no Order, Ticket or Settlement

#### Scenario: Payment not captured

- **WHEN** Order.GetCapturedPayment fails with FailedPrecondition
- **THEN** IssueFromCapturedWin fails with FailedPrecondition and creates nothing

#### Scenario: Organizer unresolved

- **WHEN** Event.GetOrganizerID fails with NotFound
- **THEN** IssueFromCapturedWin fails with NotFound and creates nothing

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
