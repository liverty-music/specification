## ADDED Requirements

### Requirement: Persistent Help Icon in Onboarding Pages

The system SHALL display a persistent `?` help icon in the top-right area of the Discovery, Dashboard, and My Artists pages during onboarding.

#### Scenario: Help icon is always visible

- **WHEN** the user is on the Discovery, Dashboard, or My Artists page during onboarding
- **THEN** a `?` icon button SHALL be visible in the top-right corner of the page header
- **AND** the button SHALL have `aria-label="ヘルプを表示"` for accessibility

### Requirement: Auto-open on First Page Visit

The system SHALL automatically open the help bottom-sheet on the user's first visit to each page during onboarding.

#### Scenario: First visit to Discovery during onboarding

- **WHEN** the user arrives at the Discovery page for the first time during onboarding
- **AND** `localStorage['liverty:onboarding:helpSeen:discovery']` is not set
- **THEN** the help bottom-sheet SHALL open automatically
- **AND** the system SHALL set `localStorage['liverty:onboarding:helpSeen:discovery']` to `'1'`

#### Scenario: First visit to My Artists during onboarding

- **WHEN** the user arrives at the My Artists page for the first time during onboarding
- **AND** `localStorage['liverty:onboarding:helpSeen:my-artists']` is not set
- **THEN** the help bottom-sheet SHALL open automatically
- **AND** the system SHALL set `localStorage['liverty:onboarding:helpSeen:my-artists']` to `'1'`

#### Scenario: Subsequent visits do not auto-open

- **WHEN** the user visits a page where `localStorage['liverty:onboarding:helpSeen:<page>']` is already set
- **THEN** the help bottom-sheet SHALL NOT open automatically
- **AND** the user MAY open it manually by tapping the `?` icon

### Requirement: Page-specific Help Content

The help bottom-sheet SHALL display page-specific guide content when opened.

#### Scenario: Discovery help content

- **WHEN** the help bottom-sheet opens on the Discovery page
- **THEN** the sheet SHALL display guidance explaining that tapping artist bubbles follows them
- **AND** the sheet SHALL note that followed artists can be managed from the My Artists page
- **AND** the sheet SHALL include the current follow progress (e.g., "3 / 5 フォロー済み")

#### Scenario: Dashboard help content

- **WHEN** the help bottom-sheet opens on the Dashboard page
- **THEN** the sheet SHALL display an explanation of the HOME / NEAR / AWAY lane structure
- **AND** the sheet SHALL explain how the hype level setting determines which lanes show notifications

#### Scenario: My Artists help content

- **WHEN** the help bottom-sheet opens on the My Artists page
- **THEN** the sheet SHALL display the hype level explanation:
  - 👀 Watch — 通知なし
  - 🔥 Home — 居住エリアのライブを通知
  - 🔥🔥 Nearby — 近くのライブも通知
  - 🔥🔥🔥 Away — 全国のライブを通知
- **AND** the sheet SHALL note that an account is required to receive notifications

### Requirement: Help seen flags cleared on onboarding reset

- **WHEN** the user starts a fresh onboarding session (taps [Get Started] on Welcome)
- **THEN** the system SHALL clear all `liverty:onboarding:helpSeen:*` keys from localStorage
