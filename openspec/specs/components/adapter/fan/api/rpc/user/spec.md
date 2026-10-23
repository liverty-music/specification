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

Get, Update, SetPreferredLanguage, SetHome and ResendEmailVerification SHALL name no User: the request carries no User id, and each call acts on the signed-in caller's own User. Get, Update, SetPreferredLanguage and SetHome SHALL resolve the caller's User from the caller's sign-in identity through UserUseCase.ResolveCaller and return its failure unchanged, NotFound when the caller has no User, before any other read or any change. ResendEmailVerification leaves resolving the caller to UserUseCase.ResendEmailVerification.

#### Scenario: Own account

- **WHEN** a signed-in caller calls Get, SetPreferredLanguage or SetHome
- **THEN** the call proceeds for the caller's User

#### Scenario: Another user's account

- **WHEN** a signed-in caller wants to read or change another User's account
- **THEN** no user service call accepts that User, and every call reads or changes only the caller's own User

#### Scenario: Missing user id

- **WHEN** a signed-in caller calls Get, SetPreferredLanguage or SetHome, whose requests carry no User id
- **THEN** the call acts on the caller's own User and does not fail for a missing User id

#### Scenario: Caller has no account

- **WHEN** the signed-in caller's identity has no User
- **THEN** the call fails with NotFound

### Requirement: Get returns the caller's profile

Get SHALL return the caller's User as resolved by the per-user check, so the same profile is restored on every device.

#### Scenario: Caller reads their profile

- **WHEN** a signed-in caller calls Get
- **THEN** the caller's User is returned with their home and preferred language

### Requirement: Create registers the signed-in identity

Create SHALL name no User id. It SHALL take the provider user ID, email and name from the caller's sign-in identity and never from the request; the request SHALL still carry a well-formed email, which is ignored. It SHALL take the optional Home and optional preferred language from the request, fail with InvalidArgument when a Home in the request is malformed or a given preferred language is not exactly two lowercase letters, and otherwise call UserUseCase.Create and return the User it returns.

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

### Requirement: SetPreferredLanguage checks the language first

SetPreferredLanguage SHALL fail with InvalidArgument when the language is not exactly two lowercase letters, before the caller is resolved, so a malformed request fails the same way for every caller. It SHALL then apply the per-user check and call UserUseCase.SetPreferredLanguage for the caller's User.

#### Scenario: Language changed

- **WHEN** a signed-in caller calls SetPreferredLanguage with `en`
- **THEN** the returned User has preferred language `en`

#### Scenario: Malformed language from a caller without an account

- **WHEN** a signed-in caller whose identity has no User sends `ja-JP`
- **THEN** it fails with InvalidArgument, not NotFound

### Requirement: SetHome requires a well-formed home

SetHome SHALL fail with InvalidArgument when the request carries no Home, or a Home whose country code, level 1 or level 2 is malformed. It SHALL then apply the per-user check and call UserUseCase.SetHome for the caller's User.

#### Scenario: Home set

- **WHEN** a signed-in caller calls SetHome with country code `JP` and level 1 `JP-13`
- **THEN** the returned User has that home

#### Scenario: Missing home

- **WHEN** the request carries no Home
- **THEN** SetHome fails with InvalidArgument and nothing changes

#### Scenario: Another user's account

- **WHEN** a signed-in caller calls SetHome with a well-formed Home
- **THEN** only the caller's own home is changed, and no other User's home can be named or changed

### Requirement: ResendEmailVerification is decided by the usecase

ResendEmailVerification SHALL call UserUseCase.ResendEmailVerification with the caller's sign-in identity and return its failure unchanged. Resolving the caller, the limit of 3 resends per 10 minutes per User and announcing the resend request are that usecase's rules; the code itself is sent later by UserUseCase.ReissueEmailVerification.

#### Scenario: Caller resends their own email

- **WHEN** a signed-in caller requests a resend for their own unverified account
- **THEN** the call succeeds once UserUseCase.ResendEmailVerification has announced the resend request for the caller's User

#### Scenario: Usecase failure returned unchanged

- **WHEN** UserUseCase.ResendEmailVerification fails with ResourceExhausted
- **THEN** ResendEmailVerification fails with ResourceExhausted

### Requirement: Update changes the caller's full name and phone number

Update SHALL take a new full name, a new phone number or both, and fail with InvalidArgument, before any usecase runs, when neither is given or a given value breaks the User's personal details rule, including a phone number not in E.164 form; a value not given keeps the current one. It SHALL then run UserUseCase.Update for the caller's User and return the User.

#### Scenario: Fan corrects their phone number
- **WHEN** a signed-in fan calls Update with only the phone number `+819098765432`
- **THEN** the caller's User carries the new phone number and the other fields are unchanged

#### Scenario: Nothing to update
- **WHEN** Update is called with neither a full name nor a phone number
- **THEN** it fails with InvalidArgument and nothing changes

#### Scenario: Domestic-format phone number on update
- **WHEN** Update is called with the phone number `090-9876-5432`
- **THEN** it fails with InvalidArgument and nothing changes

### Requirement: A returned User carries its profile fields

Every user service call that returns a User SHALL return its id, email, provider user ID, name, preferred language when set, home as country code, level 1 and, when set, level 2, and the User's full name and phone number when set, which the lottery entry and checkout screens prefill. It SHALL NOT return the home's centroid or a verification level.

#### Scenario: User with home and language

- **WHEN** a call returns a User with preferred language `ja` and home `JP-13`
- **THEN** the response carries preferred language `ja` and home country code `JP`, level 1 `JP-13`, without a centroid

#### Scenario: User without optional values

- **WHEN** a call returns a User with no preferred language, no home, no full name and no phone number
- **THEN** the response carries none of them

#### Scenario: Returning fan

- **WHEN** Get returns a User who gave the full name `山田 花子` and the phone number `+819012345678` in an earlier lottery entry or checkout
- **THEN** the response carries that full name and phone number
