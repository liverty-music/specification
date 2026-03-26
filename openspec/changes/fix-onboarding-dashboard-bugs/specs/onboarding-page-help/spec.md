## MODIFIED Requirements

### Requirement: Auto-open on First Page Visit

The system SHALL automatically open the help bottom-sheet on the user's first visit to Discovery and My Artists pages during onboarding. The Dashboard page SHALL NOT auto-open the help sheet.

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

#### Scenario: Dashboard does NOT auto-open

- **WHEN** the user arrives at the Dashboard page during onboarding
- **THEN** the help bottom-sheet SHALL NOT open automatically
- **AND** the user MAY open it manually by tapping the `?` icon

#### Scenario: Subsequent visits do not auto-open

- **WHEN** the user visits a page where `localStorage['liverty:onboarding:helpSeen:<page>']` is already set
- **THEN** the help bottom-sheet SHALL NOT open automatically
- **AND** the user MAY open it manually by tapping the `?` icon

### Requirement: Persistent Help Icon in Onboarding Pages

The system SHALL display a persistent `?` help icon in the top-right area of the Discovery, Dashboard, and My Artists pages during onboarding. The icon SHALL be placed inside a `<page-header>` component on all pages.

#### Scenario: Help icon is always visible

- **WHEN** the user is on the Discovery, Dashboard, or My Artists page during onboarding
- **THEN** a `?` icon button SHALL be visible in the top-right corner of the page header
- **AND** the button SHALL have `aria-label="ヘルプを表示"` for accessibility
- **AND** the `<page-help>` component SHALL be placed inside the `<page-header>` `<au-slot>` on all pages
