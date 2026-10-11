# components/entity/reservation/set-authorization Specification

## Purpose
Records the fan's 本人確認 (identity check) details and the card hold opened for a Reservation.

## Requirements

### Requirement: Holder identity and hold recorded once

SetAuthorization SHALL take a Reservation, a holder full name, a holder phone number and an authorization reference, and store them while the Reservation is Held. When the Reservation already has the same authorization reference, it SHALL store the given name and phone and succeed. It SHALL fail with FailedPrecondition when the Reservation has another authorization reference or is not Held, with InvalidArgument when the name or phone breaks the holder identity rules, and with NotFound when no Reservation has the id.

#### Scenario: First authorization

- **WHEN** a Held Reservation without a hold gets a name, a phone and a hold reference
- **THEN** all three are stored

#### Scenario: Name corrected on retry

- **WHEN** the same hold reference is set again with a corrected name
- **THEN** the corrected name is stored

#### Scenario: Expired checkout

- **WHEN** the Reservation is Expired
- **THEN** SetAuthorization fails with FailedPrecondition
