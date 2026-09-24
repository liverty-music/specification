# User.UpdatePreferredLanguage

## Purpose

Sets a User's preferred language and returns the updated User.

## Requirements

### Requirement: UpdatePreferredLanguage changes only the language

UpdatePreferredLanguage SHALL set the User's preferred language to the given value, change no other attribute of the User, and return the updated User.

#### Scenario: Language changed

- **WHEN** UpdatePreferredLanguage runs with `en` for a User whose preferred language is `ja`
- **THEN** the User's preferred language is `en`, every other attribute is unchanged, and the returned User carries `en`

### Requirement: UpdatePreferredLanguage failures

UpdatePreferredLanguage SHALL fail with NotFound when no User has the given id, and with InvalidArgument when the id or the language is empty; in each case nothing changes.

#### Scenario: Unknown id

- **WHEN** no User has the given id
- **THEN** UpdatePreferredLanguage fails with NotFound

#### Scenario: Empty language

- **WHEN** the language is empty
- **THEN** UpdatePreferredLanguage fails with InvalidArgument and the stored language is unchanged
