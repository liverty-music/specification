## ADDED Requirements

### Requirement: One observable language source for each sign-in state

The fan app's current language SHALL come from one source for each sign-in state: the account's preferred language for a signed-in fan, and the language chosen on the device for a guest. Everything on screen that depends on the language, including a language selector's highlight, SHALL update as soon as that language changes, without a reload.

#### Scenario: Guest language exposed as observable
- **WHEN** a guest changes the language
- **THEN** the screen and the language selector's highlight show the new language without a reload

#### Scenario: Unified resolution across auth states
- **WHEN** a screen shows the current language
- **THEN** it shows the account's preferred language for a signed-in fan and the device's language for a guest

#### Scenario: Account language used as is
- **WHEN** a signed-in fan's account is restored
- **THEN** the account's preferred language is the current language, and the account is not changed

## REMOVED Requirements

### Requirement: Unified Language Preference Resolution
**Reason**: Replaced by "One observable language source for each sign-in state", which states the behavior without the scenarios of the removed behavior.
**Migration**: None.


### Requirement: Backfill Preferred Language When Missing
**Reason**: A User always has a preferred language; UserUseCase.Create requires one, and no stored User lacks it.
**Migration**: None.
