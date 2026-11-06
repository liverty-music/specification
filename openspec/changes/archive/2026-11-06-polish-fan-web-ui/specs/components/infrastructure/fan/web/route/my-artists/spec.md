## RENAMED Requirements

- FROM: `### Requirement: Sticky Header Legend`
- TO: `### Requirement: Hype header legend stays above the scrolling list`

## MODIFIED Requirements

### Requirement: Hype header legend stays above the scrolling list

The My Artists list view SHALL display a header row showing hype tier icons and labels above the artist rows. Only the artist rows SHALL scroll; the header SHALL stay outside the scrolling area, so no row can be drawn over it. The header SHALL remain the column header of the artist table for assistive technology.

#### Scenario: Header renders with 4 columns

- **WHEN** the My Artists page renders in list view
- **THEN** the system SHALL display a header row below the page title
- **AND** the header SHALL contain 4 equally-spaced columns: 👀 Watch, 🔥 Home, 🔥🔥 Nearby, 🔥🔥🔥 Away, the same in every language
- **AND** each column SHALL vertically align with the corresponding dot stop on the artist rows

#### Scenario: Header column alignment matches artist row dot positions

- **WHEN** the header and any artist row are visible simultaneously
- **THEN** the center of each header label SHALL be horizontally aligned, within 1 px, with the center of the corresponding dot in the artist row

#### Scenario: Header remains visible during scroll

- **WHEN** the user scrolls the artist list by 300 px on a 375 × 600 px screen with 40 followed artists
- **THEN** the header SHALL stay at the same position it had before the scroll
- **AND** every header label SHALL be fully visible, with no part of a row, a dot or a track line drawn over it
- **AND** the header SHALL have a `[data-hype-header]` attribute for coach mark targeting

#### Scenario: Header stays clear while a row animates out

- **WHEN** the fan removes an artist in edit mode while the list is scrolled
- **THEN** the row's exit animation SHALL NOT draw over the header

#### Scenario: Table semantics are kept

- **WHEN** a screen reader reads the artist list
- **THEN** it SHALL announce a table whose column headers are the four hype labels and whose row headers are the artist names

### Requirement: Slider dot positions align with header columns

The 4 dot stops of every artist row SHALL align with the 4 header legend columns at every viewport width.

#### Scenario: Slider spans header dot columns

- **WHEN** the page renders on a 320 px, a 375 px and a 768 px wide screen
- **THEN** on each width the center of every dot stop SHALL be horizontally aligned, within 1 px, with the center of its header column
