# components/usecase/order/issue-from-reservation Specification

## Purpose
IssuanceUseCase.IssueFromReservation finishes a fan's checkout: it commits the held tickets, charges the card and issues the Order and its account-bound covered tickets, exactly once.

## Requirements

### Requirement: Only the fan's own checkout, committed while holding

IssueFromReservation SHALL take a Reservation, the calling fan when a fan places the order, and the current time. Calls for the same Reservation SHALL be handled one after the other, so a second call waits for the first and then returns its outcome. The call proceeds as follows:
1. It SHALL read the Reservation with Reservation.Get and fail with PermissionDenied, without revealing whether it exists, when it does not exist or a calling fan is not its User.
2. When Order.GetByReservationID then finds an Order, it SHALL return that Order and do nothing else.
3. While the Reservation is Held, it SHALL fail with FailedPrecondition, changing nothing, when:
   - the Reservation is not holding at that time;
   - Event.IsEventPublished reports false for the sale's event, read with TicketSale.Get, as for a 中止 (cancelled) concert;
   - the Reservation has no authorization reference.
4. It SHALL then check the hold with Reservation.VerifyAuthorization, returning its failure unchanged and leaving the Reservation Held, so the fan can try again.
5. It SHALL then call Reservation.Commit; when Commit reports NotHeld, or the Reservation is Expired or Released, it SHALL fail with FailedPrecondition.

The card hold of a Reservation that is not committed is given back by ReservationUseCase.ReleaseExpired. The fan learns which case applied from ReservationUseCase.Get.

#### Scenario: Fan places the order within the hold

- **WHEN** a fan places the order for their holding, authorized Reservation for 2 tickets
- **THEN** the tickets are committed, the card is charged and the Order is returned

#### Scenario: Hold lapsed before placing

- **WHEN** a fan places the order after their hold expired
- **THEN** IssueFromReservation fails with FailedPrecondition, nothing is charged and the card is not checked

#### Scenario: Concert cancelled during the checkout

- **WHEN** the concert is cancelled while a fan's hold lasts and the fan then places the order
- **THEN** IssueFromReservation fails with FailedPrecondition, the Reservation stays Held and nothing is charged

#### Scenario: Card not yet authenticated

- **WHEN** the fan places the order before completing card authentication
- **THEN** IssueFromReservation fails with FailedPrecondition and the Reservation stays Held

#### Scenario: Double tap on the action

- **WHEN** the fan places the order twice at the same time
- **THEN** one Order is issued, the card is charged once, and both calls return that Order

#### Scenario: Fan and the stalled-checkout job at once

- **WHEN** a fan's slow placement and IssuanceUseCase.IssueDueReservations handle the same Reservation at the same time
- **THEN** the card is charged once and both end with the same Order

#### Scenario: Someone else's checkout

- **WHEN** a fan places the order for a Reservation of another User, whether or not it was paid
- **THEN** IssueFromReservation fails with PermissionDenied and returns no Order

### Requirement: Charge once, then issue

For a Committed Reservation without a capture time, IssueFromReservation SHALL charge the card with Reservation.CaptureAuthorization and record the charge with Reservation.RecordCapture:
- When the capture fails with FailedPrecondition, meaning the hold can no longer be charged, it SHALL give the tickets back with Reservation.RevertCommit and fail with FailedPrecondition.
- When it fails with any other error, it SHALL leave the Reservation Committed and fail with that error; IssuanceUseCase.IssueDueReservations finishes the checkout later.

A Reservation that already has a capture time SHALL never be charged again.

It SHALL then read the charged payment with Order.GetCapturedPayment for the Reservation's authorization reference, read the sale with TicketSale.Get, resolve the sale's event's Organizer with Event.GetOrganizerID, and read the Organizer with Organizer.Get for its platform fee rate. It SHALL build:
- a Paid Order for the Reservation's User, whose source is the Reservation, with the Reservation's amount in yen, the authorization reference as its payment reference and the charged payment's card brand and last four digits, and a paid time of the time of issuance;
- exactly as many Tickets as the Reservation's count, each bound to that User, for the sale's event, carrying the Reservation's holder full name and phone number, and Issued at the same time;
- a Held Settlement for the event and its Organizer, with one split paying that Organizer the Order's amount minus the platform fee at the Organizer's rate.

It SHALL store them with Order.Issue. When Order.Issue fails with AlreadyExists, it SHALL return the Order found by Order.GetByReservationID. Any other failure leaves the charged Reservation Committed for IssuanceUseCase.IssueDueReservations.

#### Scenario: Checkout issued

- **WHEN** a Committed Reservation for 2 tickets of 3000 yen is charged for an Organizer at 8%
- **THEN** a Paid 6000 yen Order, 2 Issued Tickets bound to the fan with their name and phone, and a Held Settlement with one 5520 yen split are created, and the Reservation is Completed

#### Scenario: Card no longer chargeable

- **WHEN** the capture fails with FailedPrecondition
- **THEN** the Reservation is Released, its tickets go back on sale and IssueFromReservation fails with FailedPrecondition

#### Scenario: Card payments unavailable during capture

- **WHEN** the capture fails with Unavailable
- **THEN** the Reservation stays Committed without a capture time and IssueFromReservation fails with Unavailable

#### Scenario: Issuance fails after the charge

- **WHEN** the card was charged and Order.Issue fails with Unavailable
- **THEN** the Reservation stays Committed with its capture time, and a later run issues the Order without charging again
