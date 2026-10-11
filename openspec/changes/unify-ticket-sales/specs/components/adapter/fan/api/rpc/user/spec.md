# Spec Delta

## RENAMED Requirements

- FROM: `### Requirement: UpdatePreferredLanguage checks the language first`
- TO: `### Requirement: SetPreferredLanguage checks the language first`

- FROM: `### Requirement: UpdateHome requires a well-formed home`
- TO: `### Requirement: SetHome requires a well-formed home`

## ADDED Requirements

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

## MODIFIED Requirements

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

ResendEmailVerification SHALL call UserUseCase.ResendEmailVerification with the caller's sign-in identity and return its failure unchanged. Whether verification is available, resolving the caller, and the limit of 3 resends per 10 minutes per User are that usecase's rules.

#### Scenario: Caller resends their own email

- **WHEN** a signed-in caller requests a resend for their own unverified account
- **THEN** a fresh verification email is sent

#### Scenario: Usecase failure returned unchanged

- **WHEN** UserUseCase.ResendEmailVerification fails with ResourceExhausted
- **THEN** ResendEmailVerification fails with ResourceExhausted

## REMOVED Requirements

### Requirement: A returned user shows the profile fields
**Reason**: The scenario "Returning buyer" is renamed "Returning fan": a fan who gave their details in a lottery entry or a checkout is a User, not a buyer (design D17). A MODIFIED block cannot drop a scenario, so the requirement is replaced.
**Migration**: The same rule continues as "A returned User carries its profile fields" above.
