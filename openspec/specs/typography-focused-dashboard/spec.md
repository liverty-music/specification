# Capability: Typography-Focused Dashboard

## Purpose

Display upcoming concerts in a three-lane layout (Main, Region, Other) with typography-focused card design and visual mutations for high-priority artists.

## Requirements

### Requirement: Three-Lane Live Highway Layout
The system SHALL display live events in a three-column timeline layout organized by geographical proximity and date, with a dark-themed aesthetic. The dashboard SHALL handle data loading errors gracefully and distinguish between empty data and error states.

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

#### Scenario: Lane 1 - My City (Main Lane)
- **WHEN** displaying Lane 1 (50% screen width)
- **THEN** the system SHALL show events in the user's registered prefecture
- **AND** the system SHALL use mega-typography style cards with the display font at 4xl size or larger
- **AND** cards SHALL feature the artist name in extra-bold font as the dominant visual element
- **AND** cards SHALL apply a subtle gradient or shadow to create visual depth
- **AND** cards SHALL NOT display images, dates, or venue names on the surface

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
