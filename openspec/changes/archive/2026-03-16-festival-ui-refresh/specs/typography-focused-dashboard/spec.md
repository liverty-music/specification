## MODIFIED Requirements

### Requirement: Three-Lane Live Highway Layout
The system SHALL display live events in a three-column equal-width timeline layout organized by geographical proximity and date, with festival-style sticky STAGE headers using per-stage identity colors and a vibrant dark-themed aesthetic. The dashboard SHALL handle data loading errors gracefully and distinguish between empty data and error states.

#### Scenario: Dashboard data loading uses promise.bind
- **WHEN** the dashboard loads event data
- **THEN** the template SHALL use `promise.bind` to declaratively handle pending, success, and error states
- **AND** the pending state SHALL display loading skeletons matching the three-lane card layout
- **AND** the error state SHALL display an error message with a "Retry" button

#### Scenario: Dashboard displays empty state
- **WHEN** the dashboard data loads successfully but no events are found
- **THEN** the system SHALL display an empty state message (distinct from the error state)
- **AND** the empty state SHALL NOT be confused with a loading failure

#### Scenario: Dashboard silently displays cached data on refresh failure
- **WHEN** the dashboard has previously loaded data successfully
- **AND** a subsequent data refresh fails
- **THEN** the system SHALL continue displaying the previously loaded data silently
- **AND** the system SHALL NOT display any warning banner or stale data indicator
- **AND** the error SHALL be logged for observability but not surfaced to the user

#### Scenario: Equal-width three-lane grid
- **WHEN** the dashboard renders the event grid
- **THEN** the system SHALL use `grid-template-columns: 1fr 1fr 1fr` for equal lane widths
- **AND** each lane SHALL occupy exactly one-third of the viewport width

#### Scenario: Festival-style color-coded STAGE headers
- **WHEN** the dashboard renders
- **THEN** the system SHALL display a sticky header row at the top of the timetable
- **AND** each stage header span SHALL use its stage identity color as background via `data-stage` attribute selectors (CUBE CSS exception pattern) within the dashboard block's `@scope`:
  - `[data-stage="home"]`: `--color-stage-home` (orange)
  - `[data-stage="near"]`: `--color-stage-near` (cyan)
  - `[data-stage="away"]`: `--color-stage-away` (magenta)
- **AND** text color SHALL be `--color-surface-base` (dark) for contrast against the vibrant backgrounds
- **AND** the labels SHALL use `--font-display` with `font-weight: normal` (400, Righteous single weight), uppercase text
- **AND** the header SHALL use `position: sticky; inset-block-start: 0` with an opaque background

#### Scenario: Lane 1 - HOME STAGE
- **WHEN** displaying the HOME STAGE lane
- **THEN** the system SHALL show events in the user's registered prefecture (proto field: `home`)
- **AND** cards SHALL feature the artist name as the dominant visual element
- **AND** cards SHALL use `container-type: inline-size` for responsive font sizing

#### Scenario: Lane 2 - NEAR STAGE
- **WHEN** displaying the NEAR STAGE lane
- **THEN** the system SHALL show events in nearby prefectures (proto field: `nearby`)
- **AND** cards SHALL display artist name and location label

#### Scenario: Lane 3 - AWAY STAGE
- **WHEN** displaying the AWAY STAGE lane
- **THEN** the system SHALL show events in all other prefectures (proto field: `away`)
- **AND** cards SHALL display artist name and location label

#### Scenario: Dynamic artist name font sizing
- **WHEN** rendering an artist name within a lane card
- **THEN** the system SHALL use CSS container queries to dynamically size the font
- **AND** the font size SHALL use `clamp(12px, 5cqi, 24px)` or equivalent container-relative sizing
- **AND** the minimum font size SHALL be 12px to ensure readability
- **AND** long artist names SHALL wrap with `overflow-wrap: break-word`
- **AND** card height SHALL expand to accommodate line breaks (no fixed height, no text truncation)

#### Scenario: Stage-colored lane accents
- **WHEN** rendering the lane columns in the timetable
- **THEN** each lane SHALL have a subtle `border-block-start` accent using its stage color at 40% opacity
- **AND** lane separators SHALL use `border-inline-end` with the adjacent stage color at 15% opacity

#### Scenario: Date separator gradient treatment
- **WHEN** rendering a date separator between date groups
- **THEN** the separator background SHALL use a linear gradient from `--color-stage-home` through `--color-stage-near` to `--color-stage-away` at 10% opacity
- **AND** the date text SHALL use `--color-brand-accent` color
- **AND** the separator SHALL maintain `position: sticky` with `inset-block-start: 0` behavior and `backdrop-filter: blur(4px)`
