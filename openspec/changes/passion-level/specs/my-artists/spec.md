# My Artists (Delta)

## New Requirements

### Requirement: Passion Level Indicator
The system SHALL display the current passion level for each followed artist on the My Artists page.

#### Scenario: Displaying passion level icon
- **WHEN** the My Artists list is displayed
- **THEN** each artist row SHALL show a passion level icon alongside the artist name
- **AND** the icon SHALL correspond to the current level: 🔥🔥 (Must Go), 🔥 (Local Only), or 👀 (Keep an Eye)

---

### Requirement: Passion Level Selector
The system SHALL provide an inline control to change each artist's passion level from the My Artists page.

#### Scenario: Opening the selector
- **WHEN** a user taps the passion level icon on an artist row
- **THEN** the system SHALL display a dropdown or bottom sheet with the three passion level options
- **AND** the currently active level SHALL be visually indicated

#### Scenario: Changing passion level
- **WHEN** a user selects a different passion level from the selector
- **THEN** the system SHALL update the icon on the artist row immediately (optimistic update)
- **AND** the system SHALL call `ArtistService.SetPassionLevel` RPC to persist the change
- **AND** any RPC error SHALL be logged but SHALL NOT revert the UI state

---

### Requirement: View Toggle (List / Grid)
The system SHALL provide a view toggle to switch between List View and Grid (Festival) View on the My Artists page.

#### Scenario: Default view
- **WHEN** the My Artists page is opened
- **THEN** the system SHALL display the List View by default

#### Scenario: Switching to Grid (Festival) View
- **WHEN** a user taps the view toggle control
- **THEN** the system SHALL switch to a grid layout where artist names are displayed as bold, poster-style tiles
- **AND** each tile SHALL use the artist's dynamic color as the background
- **AND** tile size SHALL reflect the artist's passion level (Must Go tiles are larger)

#### Scenario: Switching back to List View
- **WHEN** a user taps the view toggle while in Grid View
- **THEN** the system SHALL switch back to the vertical list layout with passion level selectors

#### Scenario: Passion level interaction in Grid View
- **WHEN** a user long-presses an artist tile in Grid View
- **THEN** the system SHALL display a context menu with passion level options and an unfollow action
