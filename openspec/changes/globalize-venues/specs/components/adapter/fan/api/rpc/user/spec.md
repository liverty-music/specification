## MODIFIED Requirements

### Requirement: SetHome requires a well-formed home

SetHome SHALL fail with InvalidArgument when the request carries no Home, or a Home whose country code is not two uppercase letters or whose level 1 is not in the form of a first-level Area code (two uppercase letters, optionally followed by a hyphen and 1 to 3 uppercase letters or digits). It SHALL then apply the per-user check and call UserUseCase.SetHome for the caller's User, whose failures, InvalidArgument for a level 1 that is no first-level Area included, SHALL be returned unchanged.

#### Scenario: Home set

- **WHEN** a signed-in caller calls SetHome with country code `JP` and level 1 `JP-13`
- **THEN** the returned User has that home

#### Scenario: Missing home

- **WHEN** the request carries no Home
- **THEN** SetHome fails with InvalidArgument and nothing changes

#### Scenario: Well-formed code that is no first-level Area

- **WHEN** a signed-in caller calls SetHome with country code `JP` and level 1 `JP-99`
- **THEN** UserUseCase.SetHome fails with InvalidArgument, SetHome returns it, and the caller's home is unchanged

#### Scenario: Another user's account

- **WHEN** a signed-in caller calls SetHome with a well-formed Home
- **THEN** only the caller's own home is changed, and no other User's home can be named or changed

### Requirement: A returned User carries its profile fields

Every user service call that returns a User SHALL return its id, email, provider user ID, name, preferred language, home as country code and level 1, and the User's full name and phone number when set, which the lottery entry and checkout screens prefill. It SHALL NOT return the home's reference point or a verification level.

#### Scenario: User with home and language

- **WHEN** a call returns a User with preferred language `ja` and home `JP-13`
- **THEN** the response carries preferred language `ja` and home country code `JP`, level 1 `JP-13`, without a reference point

#### Scenario: User without optional values

- **WHEN** a call returns a User with preferred language `en` and no home, no full name and no phone number
- **THEN** the response carries preferred language `en` and none of the others

#### Scenario: Returning fan

- **WHEN** Get returns a User who gave the full name `山田 花子` and the phone number `+819012345678` in an earlier lottery entry or checkout
- **THEN** the response carries that full name and phone number
