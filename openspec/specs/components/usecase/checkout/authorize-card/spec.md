# components/usecase/checkout/authorize-card Specification

## Purpose
CheckoutUseCase.AuthorizeCard stores the fan's 本人確認 (identity check) details on their User and opens the card authorization for their own Checkout, returning the card authorization secret the fan's browser uses to complete card authentication.

## Requirements

### Requirement: Details stored and card authorization opened for one's own checkout

AuthorizeCard SHALL take the calling fan, a Checkout, a full name, a phone number and the current time. It SHALL read the Checkout with Checkout.Get and fail with PermissionDenied, without revealing whether it exists, when it does not exist or belongs to another User. It SHALL fail with FailedPrecondition when the Checkout is not holding at that time, and with InvalidArgument when the full name or phone number is missing or breaks the User's personal details rule. It SHALL then:
1. store the full name and phone number on the fan's User with User.UpdatePersonalDetails;
2. when the Checkout has no card authorization, open one with CardAuthorization.Create for the Checkout and its amount, and record it with Checkout.SetCardAuthorization; when it has one, read it with CardAuthorization.Get;
3. return the card authorization secret, which is never stored.

Their failures SHALL be returned unchanged. The Checkout carries no name or phone number.

#### Scenario: Fan authorizes their card
- **WHEN** a fan authorizes their card for their holding Checkout with a name and a phone number
- **THEN** the fan's User carries the name and phone number, a card authorization for the Checkout's amount is opened and recorded on the Checkout, and the card authorization secret is returned

#### Scenario: Card declined, fan retries
- **WHEN** the fan authorizes their card for the same Checkout again after the card was declined
- **THEN** the secret of the same card authorization is returned for another attempt

#### Scenario: Name corrected on retry
- **WHEN** the fan authorizes their card for the same Checkout again with a corrected name
- **THEN** the fan's User carries the corrected name and the same card authorization is used

#### Scenario: Domestic-format phone number
- **WHEN** the fan authorizes their card with the phone number `090-1234-5678`
- **THEN** AuthorizeCard fails with InvalidArgument, the User is unchanged and no card authorization is opened

#### Scenario: Someone else's checkout
- **WHEN** a fan authorizes their card for a Checkout of another User
- **THEN** AuthorizeCard fails with PermissionDenied and nothing changes

#### Scenario: Hold lapsed
- **WHEN** the fan authorizes their card 16 minutes after starting
- **THEN** AuthorizeCard fails with FailedPrecondition and no card authorization is opened, and the fan has to start again
