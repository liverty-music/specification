# Settings

## Purpose

Provides user access to account management, system preferences, and legal information. The Settings page is a grouped list UI accessible via the Bottom Navigation Bar's Settings tab.

## Requirements

### Requirement: My Home Area Preference
The system SHALL allow users to change their home area preference (prefecture) which determines the Live Highway Dashboard's geographical context.

#### Scenario: Opening home area selector
- **WHEN** a user taps the "My Home Area" row in Settings
- **THEN** the system SHALL display the `user-home-selector` component as a native `<dialog>` element via `showModal()`
- **AND** the dialog SHALL be promoted to the browser's Top Layer, rendering above all page content including the bottom navigation bar
- **AND** the dialog SHALL NOT use z-index utilities for stacking
- **AND** Step 1 SHALL show quick-select major city buttons (Tokyo, Osaka, Nagoya, Fukuoka, Sapporo, Sendai) and region buttons (Hokkaido, Tohoku, Kanto, Chubu, Kinki, Chugoku, Shikoku, Kyushu)
- **AND** WHEN a user taps a region, Step 2 SHALL show prefectures within the selected region

#### Scenario: Dialog backdrop and dismiss
- **WHEN** the home area selector dialog is open
- **THEN** the `::backdrop` pseudo-element SHALL display a dark translucent overlay with blur effect
- **AND** tapping the backdrop area SHALL close the dialog
- **AND** pressing the ESC key SHALL close the dialog

#### Scenario: Dialog open/close animation
- **WHEN** the home area selector dialog opens
- **THEN** the dialog panel SHALL slide up from the bottom of the viewport with a fade-in (300ms ease-out)
- **AND** WHEN the dialog closes
- **THEN** the panel SHALL slide down with a fade-out (300ms ease-out)
- **AND** users with `prefers-reduced-motion: reduce` SHALL see instant open/close without animation

#### Scenario: Changing home area
- **WHEN** a user selects a prefecture in Step 2 or a quick-select city in Step 1
- **THEN** the system SHALL update the user's home area preference
- **AND** the dialog SHALL close
- **AND** the Settings row SHALL reflect the new home area
- **AND** the Dashboard SHALL use the new home area for Live Highway lane calculations on next load

#### Scenario: My Home Area displays from backend User entity
- **WHEN** the Settings page loads for an authenticated user
- **THEN** the My Home Area row SHALL display the home area from `UserService.current.home`
- **AND** SHALL NOT read from localStorage for home area display
- **AND** if `UserService.current.home` is absent, the row SHALL display the localized "Not set" text

---

### Requirement: Push Notification Toggle
The system SHALL allow users to control push notification delivery for the current browser session. The toggle's displayed state SHALL be derived from the backend push subscription record combined with the browser's `PushManager` state — never from `localStorage`.

#### Scenario: Toggle state on page load — subscribed on this browser
- **WHEN** the Settings page loads
- **AND** `PushManager.getSubscription()` returns a non-null subscription
- **AND** `PushNotificationService.Get(user_id, endpoint)` returns an existing `PushSubscription`
- **THEN** the Push Notifications toggle SHALL display ON

#### Scenario: Toggle state on page load — not subscribed on this browser
- **WHEN** the Settings page loads
- **AND** `PushManager.getSubscription()` returns `null`
- **THEN** the Push Notifications toggle SHALL display OFF
- **AND** the system SHALL NOT call `PushNotificationService.Get` for a non-existent endpoint

#### Scenario: Toggle state on page load — browser has subscription but backend does not (self-heal)
- **WHEN** the Settings page loads
- **AND** `PushManager.getSubscription()` returns a non-null subscription
- **AND** `PushNotificationService.Get` returns `NOT_FOUND`
- **THEN** the system SHALL call `PushNotificationService.Create` with the browser's existing subscription material
- **AND** on success, the Push Notifications toggle SHALL display ON
- **AND** the user SHALL NOT be shown a permission prompt during self-heal

#### Scenario: Toggling notifications ON
- **WHEN** a user toggles the Push Notifications switch ON
- **THEN** the system SHALL call `PushManager.subscribe()` and `PushNotificationService.Create` with the resulting subscription material
- **AND** on success, the toggle SHALL reflect ON
- **AND** the system SHALL NOT write any `localStorage` flag for this state

#### Scenario: Toggling notifications OFF (this browser only)
- **WHEN** a user toggles the Push Notifications switch OFF
- **THEN** the system SHALL call `PushNotificationService.Delete(user_id, endpoint)` with the current browser's endpoint
- **AND** the system SHALL call `PushSubscription.unsubscribe()` on the browser subscription object
- **AND** other browsers registered by the same user SHALL continue to receive notifications
- **AND** the toggle SHALL reflect OFF

#### Scenario: Toggle state is not cached in localStorage
- **WHEN** the Settings page is rendered
- **THEN** the system SHALL NOT read `localStorage['userNotificationsEnabled']` to determine toggle state
- **AND** the `userNotificationsEnabled` key SHALL NOT appear in the `StorageKeys` catalog

---

### Requirement: About Section
The system SHALL provide access to legal and licensing information.

#### Scenario: Legal links
- **WHEN** the About section is displayed
- **THEN** the system SHALL show links to Terms of Service, Privacy Policy, and OSS Licenses
- **AND** tapping a link SHALL open the corresponding page (external or in-app webview)

---

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

### Requirement: Sign Out
The system SHALL allow authenticated users to sign out of their account. The Sign Out control SHALL be rendered only when the user is authenticated and SHALL be hidden for guest (unauthenticated) users.

#### Scenario: Sign out action
- **WHEN** an authenticated user taps the "Sign Out" button
- **THEN** the system SHALL clear the user's authentication session
- **AND** the system SHALL navigate to the Landing Page
- **AND** the Sign Out button SHALL be visually distinct (e.g., red text) and positioned at the bottom of the settings list

#### Scenario: Sign out hidden for guests
- **WHEN** an unauthenticated (guest) user views the Settings page
- **THEN** the system SHALL NOT render the Sign Out control

### Requirement: Guest-Adaptive Account Section

The system SHALL render the Settings ACCOUNT section conditionally on authentication state. For guests, the section SHALL present a sign-in / sign-up call to action and SHALL hide account-bound controls (email address, email verification status, resend-verification, sign-out). For authenticated users, the section SHALL present the existing account controls.

#### Scenario: Guest sees auth entry in ACCOUNT section

- **WHEN** an unauthenticated user views the Settings page
- **THEN** the ACCOUNT section SHALL present a "ログイン / 新規登録" call to action that initiates the OIDC sign-in / sign-up flow
- **AND** the email address row, email-verification badge, and resend-verification button SHALL NOT be rendered

#### Scenario: Authenticated user sees account controls

- **WHEN** an authenticated user views the Settings page
- **THEN** the ACCOUNT section SHALL render the email address, the verification badge, the resend-verification button (when unverified), and the Sign Out control

### Requirement: Guest Language Preference

The system SHALL allow a guest user to change the display language from Settings. For guests, the change SHALL apply via `I18N.setLocale()` only and SHALL NOT call `UserService.UpdatePreferredLanguage` (no backend persistence is possible without an account).

#### Scenario: Guest changes language

- **WHEN** an unauthenticated user selects a language different from the current one
- **THEN** the system SHALL call `I18N.setLocale()` to change the active locale
- **AND** all UI text SHALL immediately update to the selected language
- **AND** the system SHALL NOT call `UserService.UpdatePreferredLanguage`

#### Scenario: Guest home area sourced from guest storage

- **WHEN** an unauthenticated user views or changes "My Home Area"
- **THEN** the system SHALL read and write the home-area code via guest storage rather than the backend User entity
