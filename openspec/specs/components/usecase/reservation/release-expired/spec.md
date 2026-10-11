# components/usecase/reservation/release-expired Specification

## Purpose
ReservationUseCase.ReleaseExpired ends checkouts whose hold lapsed and gives back the card holds of every ended checkout, so the tickets go back on sale and no fan stays authorized for nothing.

## Requirements

### Requirement: Lapsed holds and leftover card holds handled within one minute

ReleaseExpired SHALL run every 1 minute over the Reservations returned by Reservation.ListDue:
- For a Held Reservation, it SHALL call Reservation.Release. A Reservation committed meanwhile is left Committed.
- For an Expired or Released Reservation with an authorization reference and no authorization release time, it SHALL call Reservation.CancelAuthorization and then Reservation.RecordAuthorizationRelease. This includes a Reservation just expired, one replaced when the fan started again, and one whose commit was reverted.

A Reservation whose handling fails SHALL NOT stop the others and is tried again on the next run.

#### Scenario: Fan walked away

- **WHEN** a fan's hold expired at 18:15 after authorizing their card
- **THEN** within 1 minute after the hold expired the Reservation is Expired and its tickets are on sale again, and within 1 more minute the card hold is released

#### Scenario: Count changed after authorizing

- **WHEN** a fan authorized their card for 2 tickets and then started again for 3
- **THEN** the card hold of the 2-ticket Reservation is released within 1 minute

#### Scenario: Committed at the last moment

- **WHEN** a Reservation is committed just before ReleaseExpired handles it
- **THEN** it stays Committed and its card hold is not released

#### Scenario: Cancellation fails

- **WHEN** releasing one card hold fails with Unavailable
- **THEN** the other Reservations are still handled and the failed hold is tried again 1 minute later

### Requirement: A charged hold on an ended checkout is reported

When CancelAuthorization fails with FailedPrecondition because the hold of an Expired or Released Reservation was charged, ReleaseExpired SHALL report that Reservation, with its id and payment reference, as needing an operator on every run until it is resolved, and SHALL go on with the others.

#### Scenario: Money taken on an ended checkout

- **WHEN** the card hold of a Released Reservation turns out to have been charged
- **THEN** the Reservation is reported as needing an operator on every run
