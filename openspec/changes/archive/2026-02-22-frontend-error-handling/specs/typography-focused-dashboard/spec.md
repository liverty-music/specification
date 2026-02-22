## MODIFIED Requirements

### Requirement: Three-Lane Live Highway Layout
The system SHALL display live events in a three-column timeline layout organized by geographical proximity and date, with a dark-themed aesthetic. The dashboard SHALL handle data loading errors gracefully and distinguish between empty data and error states.

#### Scenario: Dashboard layout structure
- **WHEN** the dashboard is displayed
- **THEN** the system SHALL implement a vertical-scrolling three-lane layout
- **AND** the Y-axis SHALL represent time (date/month) displayed on the left edge or lane dividers
- **AND** the X-axis SHALL represent distance from the user's registered region
- **AND** the overall dashboard SHALL use the dark surface palette from the design system

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

#### Scenario: Lane 2 - My Region (Adjacent Lane)
- **WHEN** displaying Lane 2 (30% screen width)
- **THEN** the system SHALL show events in the same geographical region as the user's prefecture
- **AND** cards SHALL be medium-sized with compressed information
- **AND** cards SHALL display artist name + prefecture name (e.g., "fukuoka")
- **AND** background SHALL be solid color or subtle gradient

#### Scenario: Lane 3 - Others (Opposite Lane)
- **WHEN** displaying Lane 3 (20% screen width)
- **THEN** the system SHALL show all other nationwide events
- **AND** cards SHALL be text-only list format
- **AND** cards SHALL display artist name + major city name (e.g., "Osaka")
- **AND** the system SHALL handle long text (e.g., via truncation or wrapping) to maintain layout integrity
