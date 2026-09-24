# UserUseCase.UpdatePreferredLanguage

## Purpose

Sets or changes a User's preferred display language, so the same language is used on every device and in notifications, and returns the updated User.

## Requirements

### Requirement: A valid language is stored for the user

UpdatePreferredLanguage SHALL take a User id and a language. It SHALL fail with InvalidArgument and change nothing when the id is empty or the language is not a valid preferred language in the terms of the User entity. Otherwise it SHALL call User.UpdatePreferredLanguage and return the updated User; a failure of User.UpdatePreferredLanguage, such as NotFound for an unknown User, SHALL be returned as it is.

#### Scenario: Successful language update

- **WHEN** UpdatePreferredLanguage is called with a stored User's id and `en`
- **THEN** it returns the User with preferred language `en`

#### Scenario: Malformed language

- **WHEN** UpdatePreferredLanguage is called with `ja-JP`
- **THEN** it fails with InvalidArgument and nothing changes

#### Scenario: Empty id

- **WHEN** UpdatePreferredLanguage is called with an empty id
- **THEN** it fails with InvalidArgument

#### Scenario: Unknown user

- **WHEN** no User has the given id
- **THEN** UpdatePreferredLanguage fails with NotFound
