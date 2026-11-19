# Spec Delta

## MODIFIED Requirements

### Requirement: Recently discovered

A ConcertSearch SHALL count as recently discovered at a moment when it has a last find time and less than the discovery window has passed since it. A ConcertSearch with no last find time is never recently discovered.

#### Scenario: Found 3 days ago with a 14-day window
- **WHEN** the last find time is 3 days before the moment and the window is 14 days
- **THEN** the ConcertSearch is recently discovered

#### Scenario: Never found
- **WHEN** the ConcertSearch has no last find time
- **THEN** it is not recently discovered
