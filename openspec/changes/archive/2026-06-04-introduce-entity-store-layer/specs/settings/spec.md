## MODIFIED Requirements

### Requirement: Guest Language Preference

The system SHALL allow a guest user to change the display language from
Settings. For guests, the change SHALL apply via `I18N.setLocale()` only and
SHALL NOT call `UserService.UpdatePreferredLanguage` (no backend persistence is
possible without an account). The language selector's selected-state indicator
and the Language row SHALL derive from `UserStore`'s observable current-language
value — NOT from a render-time read of `I18N.getLocale()` that the binding
engine cannot observe — so they reflect the active locale reactively for guests.

#### Scenario: Guest changes language

- **WHEN** an unauthenticated user selects a language different from the current one
- **THEN** the system SHALL call `I18N.setLocale()` to change the active locale
- **AND** all UI text SHALL immediately update to the selected language
- **AND** the system SHALL NOT call `UserService.UpdatePreferredLanguage`

#### Scenario: Selector highlight follows the active locale for guests

- **WHEN** an unauthenticated user changes the language (e.g. English → 日本語)
- **AND** subsequently reopens the language selector
- **THEN** the selector SHALL highlight the newly active language (日本語)
- **AND** SHALL NOT continue highlighting the previously active language
- **AND** the Settings "Language" row SHALL display the newly active language name

#### Scenario: Guest home area sourced from the user store

- **WHEN** an unauthenticated user views or changes "My Home Area"
- **THEN** the system SHALL read and write the home-area code via `UserStore`
  (backed by guest localStorage for a guest) rather than branching on auth state
  at the call site
