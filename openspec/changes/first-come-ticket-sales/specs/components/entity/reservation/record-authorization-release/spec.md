# Spec Delta

## Purpose

Records that an ended Reservation's card hold was given back, so it is not released again.

## ADDED Requirements

### Requirement: Release recorded once

RecordAuthorizationRelease SHALL set the authorization release time of an Expired or Released Reservation that has an authorization reference, and SHALL change nothing when it is already set. It SHALL fail with FailedPrecondition for a Reservation in any other status or without an authorization reference, and with NotFound when no Reservation has the id.

#### Scenario: Hold given back

- **WHEN** the card hold of an Expired Reservation is released at 18:16
- **THEN** its authorization release time is 18:16
