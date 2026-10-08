# Spec Delta

## Purpose

Opens the card hold for a Reservation's amount, at most once per Reservation.

## ADDED Requirements

### Requirement: One hold per reservation

CreateAuthorization SHALL take a Reservation and open a hold in Japanese yen for its amount that charges nothing until CaptureAuthorization runs, returning the hold's reference and a confirmation secret. Repeating it for the same Reservation SHALL return the same hold. It SHALL fail with InvalidArgument when the amount is zero or negative, and with Unavailable when card payments cannot be reached.

#### Scenario: Hold opened

- **WHEN** CreateAuthorization is called for a 6000 yen Reservation
- **THEN** a 6000 yen hold is opened, its reference and confirmation secret are returned, and nothing is charged

#### Scenario: Retried after a lost response

- **WHEN** CreateAuthorization is called again for the same Reservation
- **THEN** the same hold is returned and no second hold is opened

#### Scenario: Card payments unavailable

- **WHEN** card payments cannot be reached
- **THEN** CreateAuthorization fails with Unavailable
