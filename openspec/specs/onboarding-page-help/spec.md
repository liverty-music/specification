# Onboarding Page Help

## Purpose

Provides persistent, page-specific help content via a help icon and bottom-sheet on the Discovery, Dashboard, and My Artists pages. Auto-opens on first visit to each page during onboarding to deliver contextual guidance without blocking the user's flow. The help icon remains accessible after onboarding completes so users can revisit guidance at any time.

## Requirements

### Requirement: Persistent Help Icon in Onboarding Pages

The system SHALL display a persistent `?` help icon in the top-right area of the Discovery, Dashboard, and My Artists pages for all users regardless of onboarding state.

#### Scenario: Help icon is always visible

- **WHEN** the user is on the Discovery, Dashboard, or My Artists page
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

The help bottom-sheet SHALL display page-specific guide content when opened. Only the active page's content SHALL be rendered (mutually exclusive, enforced via `switch.bind` on the `page` bindable).

#### Scenario: Discovery help content

- **WHEN** the help bottom-sheet opens on the Discovery page
- **THEN** the sheet SHALL display guidance explaining that tapping artist bubbles follows them
- **AND** the sheet SHALL explain that followed artists can be unfollowed from the My Artists page
- **AND** the sheet SHALL mention that genre tabs and the search bar are available for browsing

#### Scenario: Dashboard help content

- **WHEN** the help bottom-sheet opens on the Dashboard page
- **THEN** the sheet SHALL display an explanation of the three stage lanes: HOME, NEAR, and AWAY
- **AND** each stage label SHALL be rendered in its corresponding stage color (`--color-stage-home`, `--color-stage-near`, `--color-stage-away`)
- **AND** the sheet SHALL explain that tapping a concert card opens the concert detail

#### Scenario: My Artists help content

- **WHEN** the help bottom-sheet opens on the My Artists page
- **THEN** the sheet SHALL display the four Hype level explanations with notification scope:
  - Watch — 通知なし
  - Home — 居住エリアのライブを通知
  - Nearby — 近くのライブも通知
  - Away — 全国のライブを通知
- **AND** the sheet SHALL explain that tapping the dot icon changes an artist's Hype level
- **AND** the sheet SHALL include a practical tip recommending Home level for artists the user is curious about

### Requirement: Help sheet visual readability

The help bottom-sheet SHALL use design tokens that ensure clear visual distinction from the app surface.

#### Scenario: Sheet background, title font, and muted text rendering

- **WHEN** the help bottom-sheet is displayed
- **THEN** the sheet background SHALL use `var(--color-surface-overlay)` so the sheet is visually elevated above the page surface
- **AND** help section titles SHALL use `font-family: var(--font-display)`
- **AND** secondary text (notes, tips) SHALL use `color: var(--color-text-secondary)` instead of reduced opacity

### Requirement: Help seen flags cleared on onboarding reset

- **WHEN** the user starts a fresh onboarding session (taps [Get Started] on Welcome)
- **THEN** the system SHALL clear all `liverty:onboarding:helpSeen:*` keys from localStorage
