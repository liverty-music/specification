# components/usecase/order/issue-due-reservations Specification

## Purpose
IssuanceUseCase.IssueDueReservations finishes checkouts whose tickets were committed but whose charge or issuance did not complete, and reports charged checkouts that stay unissued.

## Requirements

### Requirement: Stalled checkouts finished within one minute

IssueDueReservations SHALL run every 1 minute. For each Committed Reservation returned by Reservation.ListDue, it SHALL run IssuanceUseCase.IssueFromReservation without a calling fan. A Reservation whose issuance fails SHALL NOT stop the others and is tried again on the next run, until it is Completed or, if it was never charged, Released. When the listing fails, IssueDueReservations SHALL fail with that error and issue nothing.

#### Scenario: Capture interrupted

- **WHEN** a checkout's tickets were committed at 18:20 and the charge did not complete
- **THEN** by 18:22 the card is charged once and the Order and Tickets are issued

#### Scenario: Charged but not issued

- **WHEN** a checkout was charged at 18:20 and its Order was not stored
- **THEN** by 18:22 the Order and Tickets are issued and the card is not charged again

#### Scenario: One checkout fails

- **WHEN** issuance of one Reservation fails
- **THEN** the other Reservations are still issued and the failed one is tried again 1 minute later

### Requirement: A charged checkout left unissued is reported

When a Committed Reservation has a capture time more than 10 minutes before the run and is still not Completed, IssueDueReservations SHALL report it, with its id and payment reference, as needing an operator on every run, while still trying to issue it.

#### Scenario: Organizer record broken

- **WHEN** a checkout was charged at 18:20 and its issuance keeps failing
- **THEN** from 18:31 every run reports it as needing an operator and tries again
