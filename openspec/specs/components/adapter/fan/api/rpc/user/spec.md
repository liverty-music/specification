# User RPC

## Purpose

The fan-facing user service boundary: how it resolves the signed-in caller, which requests it rejects before any usecase runs, and which usecase or operation each call reaches.

## Requirements

### Requirement: Every user call requires a signed-in caller

Every call to the user service SHALL fail with Unauthenticated when the caller presents no valid sign-in token or the token names no identity, before the request is looked at further.

#### Scenario: Not signed in

- **WHEN** a caller without a valid sign-in token calls any user service call
- **THEN** it fails with Unauthenticated and nothing is read or changed

### Requirement: Per-user calls act only on the caller's own account

Get, UpdatePreferredLanguage, UpdateHome and ResendEmailVerification SHALL each name the target User by id. The boundary SHALL fail with InvalidArgument when the id is missing or is not a well-formed id. Get, UpdatePreferredLanguage and UpdateHome SHALL then resolve the caller through UserUseCase.ResolveCaller with the caller's identity and the named id, and return its failure unchanged: NotFound when the caller has no User, and PermissionDenied when the named id is not the caller's, before any other read or any change. ResendEmailVerification leaves the same check to UserUseCase.ResendEmailVerification.

#### Scenario: Own account

- **WHEN** a signed-in caller names their own User id
- **THEN** the call proceeds for the caller's User

#### Scenario: Another user's account

- **WHEN** a signed-in caller names a different User's id
- **THEN** the call fails with PermissionDenied and nothing is returned or changed

#### Scenario: Missing user id

- **WHEN** a signed-in caller names no User id
- **THEN** the call fails with InvalidArgument

#### Scenario: Caller has no account

- **WHEN** the signed-in caller's identity has no User
- **THEN** the call fails with NotFound

### Requirement: A returned user shows the profile fields

Every user service call that returns a User SHALL return its id, email, external id, name, preferred language when set, home as country code, level 1 and, when set, level 2, and the 本人確認 (identity check) holder full name and phone number when set, which the checkout prefills. It SHALL NOT return the home's centroid or a verification level.

#### Scenario: User with home and language

- **WHEN** a call returns a User with preferred language `ja` and home `JP-13`
- **THEN** the response carries preferred language `ja` and home country code `JP`, level 1 `JP-13`, without a centroid

#### Scenario: User without optional values

- **WHEN** a call returns a User with no preferred language, no home and no holder identity
- **THEN** the response carries none of them

#### Scenario: Returning buyer

- **WHEN** Get returns a User who checked out before as `山田 花子` with phone number `+819012345678`
- **THEN** the response carries that holder full name and phone number

### Requirement: Get returns the caller's profile

Get SHALL return the caller's User as resolved by the per-user check, so the same profile is restored on every device.

#### Scenario: Caller reads their profile

- **WHEN** a signed-in caller calls Get with their own User id
- **THEN** the caller's User is returned with their home and preferred language

### Requirement: Create registers the signed-in identity

Create SHALL name no User id. It SHALL take the external id, email and name from the caller's sign-in identity and never from the request; the request SHALL still carry a well-formed email, which is ignored. It SHALL take the optional Home and optional preferred language from the request, fail with InvalidArgument when a Home in the request is malformed or a given preferred language is not exactly two lowercase letters, and otherwise call UserUseCase.Create and return the User it returns.

#### Scenario: First sign-in

- **WHEN** a signed-in caller whose identity has no User calls Create with preferred language `ja`
- **THEN** a User is registered with the email and name of the sign-in identity and preferred language `ja`, and returned

#### Scenario: Request email differs from the identity

- **WHEN** the request carries an email different from the sign-in identity's email
- **THEN** the User is registered with the sign-in identity's email

#### Scenario: Returning identity

- **WHEN** a signed-in caller whose identity already has a User calls Create
- **THEN** that existing User is returned

#### Scenario: Missing email in the request

- **WHEN** the request carries no email
- **THEN** Create fails with InvalidArgument

### Requirement: UpdatePreferredLanguage checks the language first

UpdatePreferredLanguage SHALL fail with InvalidArgument when the language is not exactly two lowercase letters, before the caller is resolved, so a malformed request fails the same way for every caller. It SHALL then apply the per-user check and call UserUseCase.UpdatePreferredLanguage for the caller's User.

#### Scenario: Language changed

- **WHEN** a signed-in caller calls UpdatePreferredLanguage for their own User with `en`
- **THEN** the returned User has preferred language `en`

#### Scenario: Malformed language from a caller without an account

- **WHEN** a signed-in caller whose identity has no User sends `ja-JP`
- **THEN** it fails with InvalidArgument, not NotFound

### Requirement: UpdateHome requires a well-formed home

UpdateHome SHALL fail with InvalidArgument when the request carries no Home, or a Home whose country code, level 1 or level 2 is malformed. It SHALL then apply the per-user check and call UserUseCase.UpdateHome for the caller's User.

#### Scenario: Home set

- **WHEN** a signed-in caller calls UpdateHome for their own User with country code `JP` and level 1 `JP-13`
- **THEN** the returned User has that home

#### Scenario: Missing home

- **WHEN** the request carries no Home
- **THEN** UpdateHome fails with InvalidArgument and nothing changes

#### Scenario: Another user's account

- **WHEN** the named User id is not the caller's
- **THEN** UpdateHome fails with PermissionDenied and no home is changed

### Requirement: ResendEmailVerification is decided by the usecase

ResendEmailVerification SHALL call UserUseCase.ResendEmailVerification with the caller's sign-in identity and the named User id, and return its failure unchanged. Whether verification is available, the caller check, and the limit of 3 resends per 10 minutes per User are that usecase's rules.

#### Scenario: Caller resends their own email

- **WHEN** a signed-in caller requests a resend for their own unverified account
- **THEN** a fresh verification email is sent

#### Scenario: Usecase failure returned unchanged

- **WHEN** UserUseCase.ResendEmailVerification fails with ResourceExhausted
- **THEN** ResendEmailVerification fails with ResourceExhausted
