# components/usecase/reservation/authorize Specification

## Purpose
ReservationUseCase.Authorize records the fan's 本人確認 (identity check) details for a checkout and opens the card hold the fan's browser then authenticates.

## Requirements

### Requirement: Identity recorded and hold opened for one's own checkout

Authorize SHALL take the calling fan, a Reservation, a holder full name, a holder phone number and the current time. It SHALL read the Reservation with Reservation.Get and fail with PermissionDenied, without revealing whether it exists, when it does not exist or belongs to another User. It SHALL fail with FailedPrecondition when the Reservation is not holding at that time. It SHALL then:
1. open the hold with Reservation.CreateAuthorization;
2. record the name, the phone and the hold with Reservation.SetAuthorization;
3. store the name and the phone on the fan with User.UpdateHolderIdentity;
4. return the hold's confirmation secret, which is never stored.

Their failures SHALL be returned unchanged.

#### Scenario: Fan authorizes

- **WHEN** a fan authorizes their holding Reservation with a name and a phone number
- **THEN** a hold for the Reservation's amount is opened, the name and phone are saved on the Reservation and the fan, and the confirmation secret is returned

#### Scenario: Card declined, fan retries

- **WHEN** the fan authorizes the same Reservation again after the card was declined
- **THEN** the same hold is returned for another attempt

#### Scenario: Someone else's checkout

- **WHEN** a fan authorizes a Reservation of another User
- **THEN** Authorize fails with PermissionDenied and nothing changes

#### Scenario: Hold lapsed

- **WHEN** the fan authorizes 16 minutes after starting
- **THEN** Authorize fails with FailedPrecondition and no hold is opened, and the fan has to start again
