# Capability: My Artists

## MODIFIED Requirements

### Requirement: Artist List Row

#### Scenario: Passion level indicator displayed

- **GIVEN** the My Artists list view
- **WHEN** an artist row is rendered
- **THEN** a passion level icon SHALL appear next to the artist name

#### Scenario: Tapping passion icon opens selector

- **GIVEN** an artist row with a passion level icon
- **WHEN** the user taps the icon
- **THEN** a bottom sheet SHALL appear with all three passion level options

#### Scenario: Selecting a passion level

- **GIVEN** the passion level bottom sheet is open
- **WHEN** the user selects a level
- **THEN** the UI SHALL update optimistically and call SetPassionLevel RPC
- **AND** if the RPC fails, the UI SHALL roll back to the previous level

## ADDED Requirements

### Requirement: View Toggle (List / Grid)

The My Artists page SHALL offer a view toggle between List view (default) and Grid (Festival) view.

#### Scenario: Toggling view mode

- **GIVEN** the My Artists page header
- **WHEN** the user taps the view toggle button
- **THEN** the page SHALL switch between List and Grid view

### Requirement: Grid (Festival) View

The Grid view SHALL display followed artists as poster-style tiles in a responsive grid layout.

#### Scenario: Must Go tiles are larger

- **GIVEN** the Grid view is active
- **WHEN** an artist has passion level Must Go
- **THEN** their tile SHALL span 2 columns and 2 rows

#### Scenario: Non-Must-Go tiles are standard size

- **GIVEN** the Grid view is active
- **WHEN** an artist has passion level Local Only or Keep an Eye
- **THEN** their tile SHALL span 1 column and 1 row

#### Scenario: Long-press opens context menu

- **GIVEN** the Grid view is active
- **WHEN** the user long-presses a tile
- **THEN** a context menu SHALL appear with passion level options and an unfollow action
