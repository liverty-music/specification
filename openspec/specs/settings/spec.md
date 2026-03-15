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
The system SHALL allow users to control push notification delivery.

#### Scenario: Toggling notifications
- **WHEN** a user toggles the Push Notifications switch
- **THEN** the system SHALL subscribe or unsubscribe the user's push subscriptions via the backend `PushNotificationService` RPC
- **AND** when OFF, the system SHALL call `Unsubscribe` to remove all of the user's push subscriptions so no notifications are delivered to any device
- **AND** when ON, the system SHALL call `Subscribe` to register the current device's push subscription for notifications based on followed artists and their passion levels

---

### Requirement: About Section
The system SHALL provide access to legal and licensing information.

#### Scenario: Legal links
- **WHEN** the About section is displayed
- **THEN** the system SHALL show links to Terms of Service, Privacy Policy, and OSS Licenses
- **AND** tapping a link SHALL open the corresponding page (external or in-app webview)

---

### Requirement: Language Preference
The system SHALL allow users to change the display language of the application.

#### Scenario: Displaying language option
- **WHEN** the Settings page is displayed
- **THEN** the system SHALL show a "Language" row displaying the current language name (e.g., "日本語" or "English")

#### Scenario: Changing language
- **WHEN** a user taps the "Language" row
- **THEN** the system SHALL display a selection UI with available languages: 日本語, English
- **AND** WHEN the user selects a language
- **THEN** the system SHALL call `I18N.setLocale()` to change the active locale
- **AND** the system SHALL persist the selection in localStorage under the `language` key
- **AND** all UI text on the Settings page and throughout the app SHALL immediately update to the selected language

---

### Requirement: Sign Out
The system SHALL allow users to sign out of their account.

#### Scenario: Sign out action
- **WHEN** a user taps the "Sign Out" button
- **THEN** the system SHALL clear the user's authentication session
- **AND** the system SHALL navigate to the Landing Page
- **AND** the Sign Out button SHALL be visually distinct (e.g., red text) and positioned at the bottom of the settings list
