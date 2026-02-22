# App Shell Layout (Delta)

## Changed Requirements

### Requirement: Bottom Navigation Bar
The system SHALL use a Bottom Navigation Bar as the primary navigation structure for post-onboarding routes.

#### Scenario: Tab bar layout
- **WHEN** the user is on any post-onboarding route
- **THEN** the system SHALL display a fixed Bottom Navigation Bar at the bottom of the viewport
- **AND** the bar SHALL contain exactly 4 tabs: Home, Discover, My Artists, Settings
- **AND** each tab SHALL display an icon and a text label
- **AND** the bar SHALL use the dark surface palette from the design system

#### Scenario: Active tab indication
- **WHEN** a tab corresponds to the current route
- **THEN** the tab icon and label SHALL be highlighted using the brand accent color
- **AND** all other tabs SHALL use a muted/secondary color

#### Scenario: Tab navigation
- **WHEN** a user taps a tab
- **THEN** the system SHALL navigate to the corresponding route
- **AND** the URL SHALL update to reflect the active tab (e.g., `/dashboard`, `/discover`, `/my-artists`, `/settings`)
- **AND** browser back/forward navigation SHALL work correctly between tabs

#### Scenario: Safe area handling
- **WHEN** the device has a home indicator or system gesture bar (e.g., iPhone with notch)
- **THEN** the Bottom Navigation Bar SHALL include appropriate safe area padding at the bottom

---

### Requirement: Tab bar conditional visibility
The system SHALL hide the Bottom Navigation Bar during onboarding flows.

#### Scenario: Tab bar hidden during onboarding
- **WHEN** the user is on the Landing Page, Artist Discovery, or Loading Sequence routes
- **THEN** the system SHALL NOT display the Bottom Navigation Bar

#### Scenario: Tab bar visible after onboarding
- **WHEN** the user is on the Dashboard or any post-onboarding route
- **THEN** the system SHALL display the Bottom Navigation Bar

---

### Removed Requirements

- **Conditional Navigation Display** (top navigation bar): Replaced by Bottom Navigation Bar. The top navigation bar is no longer the primary navigation element.
- **Auth Status UI Redesign** (sign-out in top nav): Sign-out moves to Settings tab.
