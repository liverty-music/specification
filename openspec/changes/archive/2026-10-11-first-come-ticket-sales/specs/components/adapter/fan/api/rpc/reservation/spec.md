# Spec Delta

## Purpose

The fan-facing checkout service boundary: starting, reading, authorizing and confirming a checkout is for the signed-in fan, who is always the caller.

## ADDED Requirements

### Requirement: Checkout calls are for the signed-in fan

Start, Get, Authorize and Confirm SHALL require a signed-in caller and fail with Unauthenticated otherwise. They SHALL resolve the caller to their stored User with User.GetByExternalID, failing with NotFound when the caller has no stored account. They SHALL pass that User, never one named in the request, to ReservationUseCase.Start, ReservationUseCase.Get, ReservationUseCase.Authorize and IssuanceUseCase.IssueFromReservation respectively. Errors from the usecase SHALL be returned unchanged.

#### Scenario: Fan starts a checkout

- **WHEN** a signed-in fan calls Start for 2 tickets
- **THEN** ReservationUseCase.Start runs for that fan and the Reservation is returned

#### Scenario: Guest tries to buy

- **WHEN** a caller who is not signed in calls Start
- **THEN** the call fails with Unauthenticated and nothing is held

#### Scenario: Fan confirms

- **WHEN** a signed-in fan calls Confirm for their Reservation
- **THEN** IssuanceUseCase.IssueFromReservation runs with that fan as the caller and the Order is returned

### Requirement: Requests are validated before any usecase runs

Before any usecase runs, the boundary SHALL fail with InvalidArgument when:
- Start's sale is missing or malformed, or its count is missing;
- the Reservation of Get, Authorize or Confirm is missing or malformed;
- Authorize's name or phone number is missing.

#### Scenario: Missing name

- **WHEN** Authorize is called without a name
- **THEN** it fails with InvalidArgument and no hold is opened
