## ADDED Requirements

### Requirement: Language Kept Across Sign-in and Sign-out

The language the fan app shows SHALL be saved on this device every time it is applied, whether the user is a guest or signed in: a guest's switch, the detected language on first open, an account's preferred language applied after sign-in, and a signed-in switch from Settings. Signing in, signing out and an involuntary logout SHALL NOT clear the saved language, so the first screen after any of them opens in the language that was shown just before.

#### Scenario: Welcome after sign-out keeps the account's language

- **WHEN** a signed-in fan whose account language is `ja` signs out on a browser whose preferred language is English
- **THEN** the Welcome page after the sign-out redirect is in Japanese
- **AND** a reload of the Welcome page is still in Japanese

#### Scenario: Sign-out after a reload keeps the language

- **WHEN** a signed-in fan whose account language is `ja` reloads the app, and then signs out
- **THEN** the Welcome page after the sign-out redirect is in Japanese

#### Scenario: Language switched while signed in survives sign-out

- **WHEN** a signed-in fan switches the language from `ja` to `en` in Settings and then signs out
- **THEN** the Welcome page after the sign-out redirect is in English

#### Scenario: Involuntary logout keeps the language

- **WHEN** a signed-in fan whose account language is `ja` is logged out because the session can no longer be renewed
- **THEN** the page shown after the logout is in Japanese

### Requirement: Hosted Login Opens in the App's Language

Every redirect from the fan app to the hosted login screen (Login and Sign up, from any screen that offers them) SHALL ask the hosted login to show the language the fan app is showing at that moment. The hosted login's own handling of that request is specified in the fan hosted-login surface.

#### Scenario: Login from the Welcome page in Japanese

- **WHEN** a guest who switched the Welcome page to Japanese taps Login on a browser whose preferred language is English
- **THEN** the hosted login screen opens in Japanese

#### Scenario: Sign up in English

- **WHEN** a guest viewing the app in English taps Sign up on a browser whose preferred language is Japanese
- **THEN** the hosted sign-up screen opens in English


### Requirement: Language Chosen on First Open
The system SHALL choose the language on first open with one rule: the language chosen in the app and saved on this device, else the browser's preferred language when it is Japanese or English, else English. A `?lang=` URL parameter SHALL override the rule for that open. The chosen language SHALL be saved on this device so that later opens do not re-detect. The rule runs before a signed-in user's account is loaded, so its result is a TENTATIVE initial language for a signed-in session: once the account is loaded, its preferred language replaces it per "Account Language Wins While Signed In".

#### Scenario: URL parameter override
- **WHEN** the URL contains a `?lang=en` query parameter
- **THEN** the system SHALL set the active locale to EN regardless of other settings
- **AND** the system SHALL save `en` on this device

#### Scenario: Saved language (tentative initial locale)
- **WHEN** no `?lang=` URL parameter is present
- **AND** the language saved on this device is `en`
- **THEN** the system SHALL set the active locale to EN as the tentative initial value
- **AND** for an anonymous session, this tentative value SHALL be the final active locale
- **AND** for an authenticated session, this tentative value SHALL be replaced by the account's preferred language as soon as the account is loaded

#### Scenario: Browser language detection is saved
- **WHEN** no `?lang=` URL parameter is present
- **AND** no language is saved on this device
- **AND** the browser's preferred language is English (e.g. `en-US`)
- **THEN** the system SHALL set the active locale to EN
- **AND** the system SHALL save `en` on this device so subsequent reloads do not re-detect

#### Scenario: Fallback to English
- **WHEN** no `?lang=` URL parameter is present
- **AND** no language is saved on this device
- **AND** the browser's preferred language is neither Japanese nor English (e.g. `fr`)
- **THEN** the system SHALL set the active locale to EN
- **AND** the system SHALL save `en` on this device

#### Scenario: New account from an unsupported browser language
- **WHEN** a guest who never chose a language, on a browser whose preferred language is French, signs up
- **THEN** the new account's preferred language is `en`

### Requirement: Account Language Wins While Signed In
While the user is authenticated and the account's preferred language is set, the active i18n locale SHALL be the account's preferred language. The language saved on this device MAY decide the tentative locale shown before the account is loaded, but SHALL NOT override the account's preferred language once it is loaded.

#### Scenario: i18n locale aligns with backend value on every authenticated render
- **WHEN** `UserService.current` is populated and `preferred_language` is set
- **THEN** `i18n.getLocale()` SHALL return that value

#### Scenario: Saved language differs from the account's language
- **WHEN** the language saved on this device is `en`
- **AND** a signed-in user whose account language is `ja` opens the app
- **THEN** the app SHALL show Japanese as soon as the account is loaded
- **AND** the language saved on this device SHALL then be `ja`

## MODIFIED Requirements

### Requirement: Language Switching

The system SHALL re-render all translated strings when the active locale
changes without requiring a page reload, using a shared utility for changing
the active locale that selects the correct persistence path based on the
caller's authentication state, so components do not duplicate this logic.
The persistence target SHALL depend on the authentication state: anonymous
changes are saved on this device only; authenticated changes are saved to the
account via `UserService.SetPreferredLanguage` and, once applied, also on this
device per "Language Kept Across Sign-in and Sign-out".

#### Scenario: Switching language mid-session as an anonymous user
- **WHEN** an unauthenticated user changes the language preference (e.g., from the Welcome page language selector)
- **THEN** all `t`-bound template strings SHALL immediately update to the new locale
- **AND** the language saved on this device SHALL be updated
- **AND** the system SHALL NOT issue any backend RPC for the change
- **AND** date/number formatters SHALL use the new locale for subsequent renders

#### Scenario: Switching language mid-session as an authenticated user
- **WHEN** an authenticated user changes the language preference (e.g., from the Settings page)
- **THEN** the system SHALL call `UserService.SetPreferredLanguage` with the new locale
- **AND** on success, the system SHALL apply the new locale so all `t`-bound template strings update immediately
- **AND** the language saved on this device SHALL then hold the new locale
- **AND** date/number formatters SHALL use the new locale for subsequent renders

#### Scenario: Authenticated language switch RPC failure
- **WHEN** the `SetPreferredLanguage` RPC fails (network, server error)
- **THEN** the active locale SHALL end at the value it held before the change was attempted (the implementation MAY apply the new locale optimistically and revert on failure; the user-observable end-state SHALL be unchanged)
- **AND** the language saved on this device SHALL end at the value it held before the change was attempted
- **AND** the system SHALL surface a user-visible error notification (Snack)

#### Scenario: Anonymous caller path
- **WHEN** any component calls the shared language-change utility while unauthenticated
- **THEN** the utility SHALL apply the new locale and save it on this device
- **AND** the utility SHALL NOT issue any backend RPC

#### Scenario: Authenticated caller path
- **WHEN** any component calls the shared language-change utility while authenticated
- **THEN** the utility SHALL call `UserService.SetPreferredLanguage` first
- **AND** on success, the utility SHALL apply the new locale

#### Scenario: Used by both Welcome and Settings
- **WHEN** the Welcome page (anonymous context) and Settings page (authenticated context) both change language
- **THEN** they SHALL both call the same shared utility
- **AND** the utility SHALL route persistence appropriately for each context

## REMOVED Requirements

### Requirement: Remove Legacy localStorage Language Key After Authenticated Session Begins
**Reason**: Removing the saved language after sign-in made the next guest open (after sign-out or an involuntary logout) fall back to the browser language instead of the language the user had chosen. The saved language never overrides a loaded account's preferred language, so keeping it is safe.
**Migration**: None. The saved language is written again the next time any language is applied; devices where it was already removed fall back to the browser language once, as before this change.

### Requirement: Locale Detection
**Reason**: Replaced by "Language Chosen on First Open", which states the one language rule (saved choice > supported browser language > English) and falls back to English instead of Japanese.
**Migration**: None in data. A first open from a browser language other than Japanese or English now shows English.

### Requirement: Locale Sourced from Backend User Entity for Authenticated Sessions
**Reason**: Replaced by "Account Language Wins While Signed In". The saved language is no longer removed while signed in, so the "key absent" scenario no longer holds.
**Migration**: None; covered by the REMOVED requirement above on removing the saved language.
