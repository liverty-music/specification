# Capability: Typography-Focused Dashboard

## Purpose

Display upcoming concerts in a three-lane layout (Main, Region, Other) with typography-focused card design and visual mutations for high-priority artists.

## Requirements

### Requirement: Three-Lane Live Highway Layout
The system SHALL display live events in a three-column equal-width timeline layout organized by geographical proximity and date, with festival-style sticky STAGE headers and a dark-themed aesthetic. The dashboard SHALL handle data loading errors gracefully and distinguish between empty data and error states.

#### Scenario: Dashboard data loading uses promise.bind
- **WHEN** the dashboard loads event data
- **THEN** the template SHALL use `promise.bind` to declaratively handle pending, success, and error states
- **AND** the pending state SHALL display loading skeletons matching the three-lane card layout
- **AND** the error state SHALL display an error message with a "Retry" button

#### Scenario: Dashboard displays empty state
- **WHEN** the dashboard data loads successfully but no events are found
- **THEN** the system SHALL display an empty state message (distinct from the error state)
- **AND** the empty state SHALL NOT be confused with a loading failure

#### Scenario: Dashboard displays stale data on refresh failure
- **WHEN** the dashboard has previously loaded data successfully
- **AND** a subsequent data refresh fails
- **THEN** the system SHALL continue displaying the previously loaded data
- **AND** the system SHALL display a warning banner: "Data may be outdated. Refresh failed."
- **AND** the banner SHALL include a "Retry" button

#### Scenario: Equal-width three-lane grid
- **WHEN** the dashboard renders the event grid
- **THEN** the system SHALL use `grid-template-columns: 1fr 1fr 1fr` for equal lane widths
- **AND** each lane SHALL occupy exactly one-third of the viewport width

#### Scenario: Festival-style sticky STAGE headers
- **WHEN** the dashboard renders
- **THEN** the system SHALL display a sticky header row at the top of the timetable
- **AND** the header SHALL use `position: sticky; top: 0` with an opaque background
- **AND** the header SHALL display three lane labels: "HOME STAGE", "NEAR STAGE", "AWAY STAGE"
- **AND** the labels SHALL use bold, uppercase text at 14-16px font size
- **AND** the "Live Highway" title text SHALL be removed

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

### Requirement: Lane 1 - My City (Main Lane) at 50% width (REMOVED)

**Reason**: Replaced by equal-width lanes (33:33:33). The 50% main lane concept is superseded by the festival timetable aesthetic with equal STAGE columns.
**Migration**: Update `grid-template-columns` from `50% 30% 20%` to `1fr 1fr 1fr`. Remove mega-typography 4xl sizing; use container query-based dynamic sizing instead.

### Requirement: Must Go Mutation UI

When a Must Go artist's event appears in Lane 2 (Region) or Lane 3 (Other), the event card SHALL visually mutate to draw attention.

#### Scenario: Must Go event in Region lane

- **GIVEN** a Must Go artist has an event in the Region lane
- **WHEN** the dashboard renders that event
- **THEN** the card SHALL be expanded with a badge, vivid accent color with glow shadow, and bolder typography

#### Scenario: Must Go event in Other lane

- **GIVEN** a Must Go artist has an event in the Other lane
- **WHEN** the dashboard renders that event
- **THEN** the card SHALL be promoted from text-only to card style with a badge, background color, and ring border

#### Scenario: Must Go event in Main lane is not mutated

- **GIVEN** a Must Go artist has an event in the Main lane
- **WHEN** the dashboard renders that event
- **THEN** the card SHALL render normally (Main lane cards are already prominent)

#### Scenario: Non-Must-Go events are not mutated

- **GIVEN** an artist with Local Only or Keep an Eye passion level
- **WHEN** the dashboard renders their event in any lane
- **THEN** the card SHALL render in its normal style without mutation

### Requirement: Mutation Layout Handling

The dashboard layout SHALL accommodate mutated cards without breaking lane alignment.

#### Scenario: Multiple mutated cards on same date

- **GIVEN** multiple Must Go artists have events on the same date in Lane 2 or Lane 3
- **WHEN** the dashboard renders that date group
- **THEN** all mutated cards SHALL render without overflow, stacking vertically within their lane
