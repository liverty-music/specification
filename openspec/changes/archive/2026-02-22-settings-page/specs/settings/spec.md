# Settings

## Purpose

Provides user access to account management, system preferences, and legal information. The Settings page is a grouped list UI accessible via the Bottom Navigation Bar's Settings tab.

## Requirements

### Requirement: My Area Preference
The system SHALL allow users to change their registered area (prefecture) which determines the Live Highway Dashboard's geographical context.

#### Scenario: Opening area selector
- **WHEN** a user taps the "My Area" row in Settings
- **THEN** the system SHALL display a bottom sheet with a 2-step selection UI
- **AND** Step 1 SHALL show regions (e.g., Hokkaido, Tohoku, Kanto, Chubu, Kinki, Chugoku, Shikoku, Kyushu)
- **AND** Step 2 SHALL show prefectures within the selected region

#### Scenario: Changing area
- **WHEN** a user selects a prefecture in Step 2
- **THEN** the system SHALL update the user's registered area
- **AND** the bottom sheet SHALL close
- **AND** the Settings row SHALL reflect the new area
- **AND** the Dashboard SHALL use the new area for Live Highway lane calculations on next load

---

### Requirement: Push Notification Toggle
The system SHALL allow users to control push notification delivery.

#### Scenario: Toggling notifications
- **WHEN** a user toggles the Push Notifications switch
- **THEN** the system SHALL update the notification preference
- **AND** when OFF, the system SHALL NOT send any push notifications
- **AND** when ON, the system SHALL send notifications based on followed artists and their passion levels

---

### Requirement: About Section
The system SHALL provide access to legal and licensing information.

#### Scenario: Legal links
- **WHEN** the About section is displayed
- **THEN** the system SHALL show links to Terms of Service, Privacy Policy, and OSS Licenses
- **AND** tapping a link SHALL open the corresponding page (external or in-app webview)

---

### Requirement: Sign Out
The system SHALL allow users to sign out of their account.

#### Scenario: Sign out action
- **WHEN** a user taps the "Sign Out" button
- **THEN** the system SHALL clear the user's authentication session
- **AND** the system SHALL navigate to the Landing Page
- **AND** the Sign Out button SHALL be visually distinct (e.g., red text) and positioned at the bottom of the settings list
