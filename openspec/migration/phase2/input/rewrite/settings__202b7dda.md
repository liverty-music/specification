<!-- spec: settings | target: components/infrastructure/fan/web/route/settings | flags: CLASSNAME | new_name: Language Preference -->

### Requirement: Language Preference
The system SHALL allow users to change the display language of the application. While authenticated, the change SHALL be persisted to the backend user row via `UserService.UpdatePreferredLanguage` — Settings SHALL NOT read or write `localStorage['language']` for the language preference.

#### Scenario: Displaying language option
- **WHEN** the Settings page is displayed for an authenticated user
- **THEN** the system SHALL show a "Language" row displaying the current language name derived from `UserService.current.preferred_language` (e.g., "日本語" or "English")
- **AND** the system SHALL NOT read `localStorage['language']` to populate this row

#### Scenario: Displaying language option before backfill completes
- **WHEN** the Settings page is displayed and `UserService.current.preferredLanguage` is absent (legacy NULL row, or backfill RPC still in flight after hydration)
- **THEN** the system SHALL derive the displayed language name from `I18N.getLocale()` (the currently active locale, which is the value the backfill RPC will send)
- **AND** the system SHALL NOT read `localStorage['language']` to populate this row
- **AND** the row SHALL re-evaluate automatically once `UserService.current.preferredLanguage` becomes populated by the backfill response

#### Scenario: Changing language
- **WHEN** a user taps the "Language" row
- **THEN** the system SHALL display a selection UI with available languages: 日本語, English
- **AND** WHEN the user selects a language different from the current one
- **THEN** the system SHALL call `UserService.UpdatePreferredLanguage` with the new value
- **AND** on success, the system SHALL call `I18N.setLocale()` to change the active locale
- **AND** all UI text on the Settings page and throughout the app SHALL immediately update to the selected language
- **AND** the system SHALL NOT write to `localStorage['language']`
- **AND** subsequent reads of `UserService.current.preferred_language` SHALL return the new value (write-through per `user-profile-hydration`)

#### Scenario: Language change RPC failure
- **WHEN** the `UpdatePreferredLanguage` RPC fails (network or server error)
- **THEN** the active locale SHALL end at the value it held before the change was attempted (the implementation MAY apply the new locale optimistically and revert on failure, consistent with `frontend-i18n`'s "Authenticated language switch RPC failure" scenario; the user-observable end-state SHALL be unchanged)
- **AND** the displayed "Language" row SHALL end at the prior value (since the row is derived from `UserService.current.preferredLanguage`, which is restored when the optimistic update is reverted)
- **AND** the system SHALL surface a Snack notification indicating the change could not be saved

#### Scenario: Re-selecting the current language is a no-op
- **WHEN** a user taps the "Language" row and selects the language already in effect
- **THEN** the system SHALL close the selection UI without issuing an RPC
- **AND** no DB write SHALL occur

---
