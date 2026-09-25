# Spec Delta

## MODIFIED Requirements

### Requirement: Issue an order and its tickets from a won application

IssueFromCapturedWin SHALL take an application. When Order.GetByApplicationID finds an Order for it, it SHALL return that Order and issue nothing. Otherwise it SHALL read the application with TicketApplication.Get, failing with NotFound when it does not exist, and fail with FailedPrecondition, creating nothing, when the application is not Won. It SHALL read the phase with LotterySalesPhase.Get and the captured payment with Order.GetCapturedPayment, returning their failures unchanged; it never charges the card. It SHALL resolve the phase's event's Organizer with Event.GetOrganizerID, returning its failure unchanged and creating nothing. It SHALL build a Paid Order for the applicant whose amount, currency, payment service and card facets are those of the captured payment and whose paid time is the time of issuance, exactly as many Tickets as the requested ticket count, each bound to the applicant, for the phase's event, carrying the applicant's full name and phone number, Issued at the same time, and a Held Settlement for the phase's event and its Organizer with one split paying that Organizer the Order's amount. It SHALL store them with Order.Issue; when Order.Issue fails with AlreadyExists it SHALL return the Order found by Order.GetByApplicationID.

#### Scenario: Won application issued

- **WHEN** IssueFromCapturedWin runs for a Won application for 2 tickets whose 16000 yen payment was captured
- **THEN** a Paid 16000 yen Order, 2 Issued Tickets bound to the applicant for the phase's event, and a Held Settlement with one 16000 yen split for the event's Organizer are created and the Order is returned

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
