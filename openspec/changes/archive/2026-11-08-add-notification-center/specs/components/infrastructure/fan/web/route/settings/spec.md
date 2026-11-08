## ADDED Requirements

### Requirement: Language preference from the account
The system SHALL allow users to change the display language of the application. While authenticated, the change SHALL be persisted to the backend user row via `UserService.SetPreferredLanguage` and, once applied, also saved on this device per `components/infrastructure/fan/web/global/i18n` "Language Kept Across Sign-in and Sign-out". Settings SHALL NOT read browser local storage for the language preference: the row and the selector derive from the current user's preferred language.

#### Scenario: Displaying language option
- **WHEN** the Settings page is displayed for an authenticated user
- **THEN** the system SHALL show a "Language" row displaying the current language name derived from the current user's preferred language (e.g., "日本語" or "English")
- **AND** the system SHALL NOT read browser local storage to populate this row

#### Scenario: Displaying language option before the account loads
- **WHEN** the Settings page is displayed for an authenticated user whose account has not loaded yet
- **THEN** the system SHALL derive the displayed language name from the currently active locale
- **AND** the system SHALL NOT read browser local storage to populate this row
- **AND** the row SHALL re-evaluate automatically once the account, with its preferred language, has loaded

#### Scenario: Changing language
- **WHEN** a user taps the "Language" row
- **THEN** the system SHALL display a selection UI with available languages: 日本語, English
- **AND** WHEN the user selects a language different from the current one
- **THEN** the system SHALL call `UserService.SetPreferredLanguage` with the new value
- **AND** on success, the system SHALL change the active locale
- **AND** all UI text on the Settings page and throughout the app SHALL immediately update to the selected language
- **AND** the language saved on this device SHALL then hold the selected language, so the first screen after a sign-out opens in it
- **AND** subsequent reads of the current user's preferred language SHALL return the new value (write-through per `user-profile-hydration`)

#### Scenario: Language change RPC failure
- **WHEN** the `SetPreferredLanguage` RPC fails (network or server error)
- **THEN** the active locale SHALL end at the value it held before the change was attempted (the implementation MAY apply the new locale optimistically and revert on failure, consistent with `frontend-i18n`'s "Authenticated language switch RPC failure" scenario; the user-observable end-state SHALL be unchanged)
- **AND** the displayed "Language" row SHALL end at the prior value (since the row is derived from the current user's preferred language, which is restored when the optimistic update is reverted)
- **AND** the language saved on this device SHALL end at the value it held before the change was attempted
- **AND** the system SHALL surface a Snack notification indicating the change could not be saved

#### Scenario: Re-selecting the current language is a no-op
- **WHEN** a user taps the "Language" row and selects the language already in effect
- **THEN** the system SHALL close the selection UI without issuing an RPC
- **AND** no DB write SHALL occur

## REMOVED Requirements

### Requirement: Language Preference
**Reason**: Replaced by "Language preference from the account", which states the behavior without the scenario of an account with no language.
**Migration**: None.
