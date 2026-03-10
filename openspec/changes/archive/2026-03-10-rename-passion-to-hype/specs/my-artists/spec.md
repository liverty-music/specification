## MODIFIED Requirements

### Requirement: Artist List Row

Each artist row in the My Artists list view SHALL display the artist's name, color accent, and hype indicator.

#### Scenario: Hype indicator displayed

- **GIVEN** the My Artists list view
- **WHEN** an artist row is rendered
- **THEN** a hype icon SHALL appear next to the artist name (👀 for WATCH, 🔥 for HOME, 🔥🔥🔥 for ANYWHERE)

#### Scenario: Tapping hype icon opens selector

- **GIVEN** an artist row with a hype icon
- **WHEN** the user taps the icon
- **THEN** a bottom sheet SHALL appear with three hype options: WATCH, HOME, and ANYWHERE (NEARBY is hidden in Phase 1)

#### Scenario: Selecting a hype level

- **GIVEN** the hype bottom sheet is open
- **WHEN** the user selects a level
- **THEN** the UI SHALL update optimistically and call SetHype RPC
- **AND** if the RPC fails, the UI SHALL roll back to the previous level

### Requirement: Grid (Festival) View

The Grid view SHALL display followed artists as poster-style tiles in a responsive grid layout.

#### Scenario: ANYWHERE tiles are larger

- **GIVEN** the Grid view is active
- **WHEN** an artist has hype set to ANYWHERE
- **THEN** their tile SHALL span 2 columns and 2 rows

#### Scenario: Non-ANYWHERE tiles are standard size

- **GIVEN** the Grid view is active
- **WHEN** an artist has hype set to WATCH or HOME
- **THEN** their tile SHALL span 1 column and 1 row

#### Scenario: Long-press opens context menu

- **GIVEN** the Grid view is active
- **WHEN** the user long-presses a tile
- **THEN** a context menu SHALL appear with hype options (WATCH, HOME, ANYWHERE) and an unfollow action
