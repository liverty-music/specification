## MODIFIED Requirements

### Requirement: Persistent Help Icon in Onboarding Pages

The system SHALL display a persistent `?` help icon in the top-right area of the Discovery, Dashboard, and My Artists page headers for all users, regardless of onboarding state.

#### Scenario: Help icon is visible during onboarding

- **WHEN** the user is on the Discovery, Dashboard, or My Artists page during onboarding
- **THEN** a `?` icon button SHALL be visible in the page header
- **AND** the button SHALL have `aria-label="ヘルプを表示"` for accessibility

#### Scenario: Help icon is visible after onboarding

- **WHEN** the user is on the Discovery, Dashboard, or My Artists page after completing onboarding
- **THEN** the `?` icon button SHALL still be visible in the page header
- **AND** tapping it SHALL open the help bottom-sheet

### Requirement: Page-specific Help Content

The help bottom-sheet SHALL display content specific to the current page only. Content for other pages SHALL NOT be rendered.

#### Scenario: Discovery help content

- **WHEN** the help bottom-sheet opens on the Discovery page
- **THEN** the sheet SHALL display guidance explaining that tapping artist bubbles follows them
- **AND** the sheet SHALL state that unfollowing is done from the My Artists page
- **AND** the sheet SHALL mention genre tabs and the search bar as discovery methods

#### Scenario: Dashboard help content

- **WHEN** the help bottom-sheet opens on the Dashboard page
- **THEN** the sheet SHALL display an explanation of the HOME / NEAR / AWAY stage structure
- **AND** each stage label SHALL be styled with its corresponding stage color token (`--color-stage-home`, `--color-stage-near`, `--color-stage-away`)
- **AND** the sheet SHALL explain that tapping a concert card shows details

#### Scenario: My Artists help content

- **WHEN** the help bottom-sheet opens on the My Artists page
- **THEN** the sheet SHALL display the four Hype levels with notification scope:
  - Watch — no notifications
  - Home — notifications for concerts in home area
  - Nearby — notifications for nearby concerts too
  - Away — notifications for all concerts nationwide
- **AND** the sheet SHALL explain that tapping a dot changes the Hype level
- **AND** the sheet SHALL include a practical tip recommending Home as a starting level for artists the user is curious about

#### Scenario: Only active page content is rendered

- **WHEN** the help bottom-sheet opens on any page
- **THEN** only the content for the current page SHALL be displayed
- **AND** content for other pages SHALL NOT be rendered

## ADDED Requirements

### Requirement: Help sheet visual readability

The help bottom-sheet SHALL use design tokens that provide sufficient contrast and visual hierarchy.

#### Scenario: Sheet background contrast

- **WHEN** the help bottom-sheet is open
- **THEN** the sheet content area SHALL use `--color-surface-overlay` as background color
- **AND** the background SHALL be visually distinct from the app's base surface (`--color-surface-base`)

#### Scenario: Title typography

- **WHEN** the help bottom-sheet displays a title
- **THEN** the title SHALL use `--font-display` font family
- **AND** the title SHALL be visually distinct from body text

#### Scenario: Muted text contrast

- **WHEN** the help sheet displays secondary or note text
- **THEN** the text SHALL use `color: var(--color-text-secondary)` instead of opacity reduction
- **AND** the text SHALL meet readable contrast against the sheet background

## REMOVED Requirements

### Requirement: Discovery follow progress in help

**Reason**: Follow count display is not help content. If needed, it belongs in the persistent page UI (e.g., Discovery header or bubble area).

**Migration**: Remove `followedCount` bindable from `page-help` component. Remove `pageHelp.discovery.followedCount` from i18n files.

### Requirement: Account registration note in My Artists help

**Reason**: Account registration prompts are the responsibility of the `signup-prompt-banner` component, which already displays contextually after onboarding.

**Migration**: Remove `pageHelp.myArtists.accountNote` from i18n files. Remove the corresponding `<p>` element from the My Artists help section template.
