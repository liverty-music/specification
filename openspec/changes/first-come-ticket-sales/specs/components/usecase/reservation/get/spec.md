# Spec Delta

## Purpose

ReservationUseCase.Get lets a fan read the state of their own checkout, so the checkout screen can tell them what happened after a step fails.

## ADDED Requirements

### Requirement: The fan's own checkout

Get SHALL take the calling fan, a Reservation and the current time, read it with Reservation.Get and fail with PermissionDenied, without revealing whether it exists, when it does not exist or belongs to another User. It SHALL return:
- its status;
- whether it is holding at that time, and its hold expiry;
- whether it has an authorization reference;
- whether it was ever committed;
- whether it was charged;
- when it is Completed, the Order's id from Order.GetByReservationID.

#### Scenario: Hold lapsed

- **WHEN** a fan reads their Held Reservation after its hold expired
- **THEN** it is returned Held and not holding

#### Scenario: Card no longer chargeable

- **WHEN** a fan reads a Reservation released because its card could not be charged after the commit
- **THEN** it is returned Released, ever committed and not charged

#### Scenario: Replaced by a newer checkout

- **WHEN** a fan reads a Reservation released because they started again in another tab
- **THEN** it is returned Released and never committed

#### Scenario: Someone else's checkout

- **WHEN** a fan reads a Reservation of another User
- **THEN** Get fails with PermissionDenied
