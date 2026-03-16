## MODIFIED Requirements

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

#### Scenario: Dashboard silently displays cached data on refresh failure
- **WHEN** the dashboard has previously loaded data successfully
- **AND** a subsequent data refresh fails
- **THEN** the system SHALL continue displaying the previously loaded data silently
- **AND** the system SHALL NOT display any warning banner or stale data indicator
- **AND** the error SHALL be logged for observability but not surfaced to the user
