## ADDED Requirements

### Requirement: A first-party series leaves with its last event

When the removal of Events leaves a Series with no Event, the Series SHALL be removed with them if it is first-party, and SHALL remain if it was found by discovery.

#### Scenario: First-party series left empty
- **WHEN** the removal of Events leaves a first-party Series with no Event
- **THEN** the Series is removed with them

#### Scenario: Discovered series left empty
- **WHEN** the removal of Events leaves a discovered Series with no Event
- **THEN** the Series remains

#### Scenario: Series with events left
- **WHEN** a first-party Series still has an Event after the removal
- **THEN** the Series remains
