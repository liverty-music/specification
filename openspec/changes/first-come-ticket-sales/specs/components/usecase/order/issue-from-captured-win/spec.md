# Spec Delta

## MODIFIED Requirements

### Requirement: Issue an order and its tickets from a won application

IssueFromCapturedWin SHALL take an application. When Order.GetByApplicationID finds an Order for it, it SHALL return that Order and issue nothing. Otherwise it SHALL read the application with TicketApplication.Get, failing with NotFound when it does not exist, and fail with FailedPrecondition, creating nothing, when the application is not Won. It SHALL read the phase with LotterySalesPhase.Get and the captured payment with Order.GetCapturedPayment, returning their failures unchanged; it never charges the card. It SHALL resolve the phase's event's Organizer with Event.GetOrganizerID and read it with Organizer.Get for its platform fee rate, returning their failures unchanged and creating nothing. It SHALL build:
- a Paid Order for the applicant, whose source is the application, whose amount, currency, payment service and card facets are those of the captured payment, and whose paid time is the time of issuance;
- exactly as many Tickets as the requested ticket count, each bound to the applicant, for the phase's event, carrying the applicant's full name and phone number, and Issued at the same time;
- a Held Settlement for the phase's event and its Organizer, with one split paying that Organizer the Order's amount minus the platform fee at the Organizer's rate.

It SHALL store them with Order.Issue, which also records the purchase; when Order.Issue fails with AlreadyExists it SHALL return the Order found by Order.GetByApplicationID.

#### Scenario: Won application issued

- **WHEN** IssueFromCapturedWin runs for a Won application for 2 tickets whose 16000 yen payment was captured, for an Organizer at 5%
- **THEN** a Paid 16000 yen Order, 2 Issued Tickets bound to the applicant for the phase's event, and a Held Settlement with one 15200 yen split for the event's Organizer are created, the purchase is recorded, and the Order is returned

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

## REMOVED Requirements

### Requirement: Ticket journey becomes Paid

**Reason**: The ticket journey update now runs for every recorded purchase, whatever its source, in TicketJourneyUseCase.MarkPaid, so a failure there is retried on its own instead of being skipped.

**Migration**: TicketJourneyUseCase.MarkPaid runs for each Order announced as paid; a lottery win sets the buyer's journey to Paid as before.
