# Spec Delta

## Purpose

CheckoutUseCase.Authorize stores the fan's 本人確認 (identity check) details on their User and opens the card hold for their own Checkout, returning the secret the fan's browser uses to complete card authentication.

## ADDED Requirements

### Requirement: Details stored and hold opened for one's own checkout

Authorize SHALL take the calling fan, a Checkout, a full name, a phone number and the current time. It SHALL read the Checkout with Checkout.Get and fail with PermissionDenied, without revealing whether it exists, when it does not exist or belongs to another User. It SHALL fail with FailedPrecondition when the Checkout is not holding at that time, and with InvalidArgument when the full name or phone number is missing or breaks the User's personal details rule. It SHALL then:
1. store the full name and phone number on the fan's User with User.UpdatePersonalDetails;
2. open the hold with Checkout.CreateAuthorization;
3. record the hold with Checkout.SetAuthorization;
4. return the hold's confirmation secret, which is never stored.

Their failures SHALL be returned unchanged. The Checkout carries no name or phone number.

#### Scenario: Fan authorizes
- **WHEN** a fan authorizes their holding Checkout with a name and a phone number
- **THEN** the fan's User carries the name and phone number, a hold for the Checkout's amount is opened and recorded on the Checkout, and the confirmation secret is returned

#### Scenario: Card declined, fan retries
- **WHEN** the fan authorizes the same Checkout again after the card was declined
- **THEN** the same hold is returned for another attempt

#### Scenario: Name corrected on retry
- **WHEN** the fan authorizes the same Checkout again with a corrected name
- **THEN** the fan's User carries the corrected name and the same hold is returned

#### Scenario: Domestic-format phone number
- **WHEN** the fan authorizes with the phone number `090-1234-5678`
- **THEN** Authorize fails with InvalidArgument, the User is unchanged and no hold is opened

#### Scenario: Someone else's checkout
- **WHEN** a fan authorizes a Checkout of another User
- **THEN** Authorize fails with PermissionDenied and nothing changes

#### Scenario: Hold lapsed
- **WHEN** the fan authorizes 16 minutes after starting
- **THEN** Authorize fails with FailedPrecondition and no hold is opened, and the fan has to start again
