## ADDED Requirements

### Requirement: Page header offers a Settings entry on tab pages

On the pages of the four navigation tabs (Home, Discover, My Artists, Tickets), the page header SHALL show a gear icon button at its trailing end that opens the Settings route. The button SHALL have an accessible name from the invariant `nav.settings` label ("Settings"). The header SHALL NOT show this button on the Settings route itself or on routes outside the four tabs. The button SHALL coexist with a route's own trailing header content, which sits before it.

#### Scenario: Gear on a tab page
- **WHEN** the dashboard, Discover, My Artists or Tickets route is displayed
- **THEN** the page header SHALL show a gear button at its trailing end named "Settings"
- **AND** tapping it SHALL display the Settings route

#### Scenario: No gear on Settings
- **WHEN** the Settings route is displayed
- **THEN** the page header SHALL NOT show the gear button

#### Scenario: No gear outside the tabs
- **WHEN** an Event page or an order detail is displayed
- **THEN** the page header SHALL NOT show the gear button

#### Scenario: Gear after a route's own trailing content
- **WHEN** My Artists shows its own trailing header content
- **THEN** that content SHALL come before the gear button
