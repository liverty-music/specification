# Spec Delta

## Purpose

ReservationUseCase.Get lets a fan read the state of their own checkout, so the checkout screen can tell them what happened after a step fails.

## ADDED Requirements

### Requirement: The fan's own checkout

Get SHALL take the calling fan, a Reservation and the current time, read it with Reservation.Get and fail with PermissionDenied, without revealing whether it exists, when it does not exist or belongs to another User. It SHALL return the Reservation as of that time: a Held Reservation that is not holding at that time SHALL be returned Expired, since its hold has lapsed for good; any other Reservation SHALL be returned with its stored status. Its commit time tells whether it was ever committed, and its capture time whether it was charged.

#### Scenario: Within the hold

- **WHEN** a fan reads their Held Reservation 5 minutes into the hold
- **THEN** it is returned Held with its hold expiry

#### Scenario: Hold lapsed

- **WHEN** a fan reads their Held Reservation after its hold expired
- **THEN** it is returned Expired

#### Scenario: Card no longer chargeable

- **WHEN** a fan reads a Reservation released because its card could not be charged after the commit
- **THEN** it is returned Released, with a commit time and no capture time

#### Scenario: Replaced by a newer checkout

- **WHEN** a fan reads a Reservation released because they started again in another tab
- **THEN** it is returned Released without a commit time

#### Scenario: Someone else's checkout

- **WHEN** a fan reads a Reservation of another User
- **THEN** Get fails with PermissionDenied
