## ADDED Requirements

### Requirement: Periodic Concert Data Refresh
The system SHALL register a Periodic Background Sync task to keep cached concert data fresh without requiring the user to open the application.

#### Scenario: PWA installed — periodic sync registered
- **WHEN** the PWA is installed on the user's device
- **AND** the browser supports the Periodic Background Sync API
- **THEN** the system SHALL register a periodic sync tag `concert-refresh` with a minimum interval of 12 hours

#### Scenario: Periodic sync fires
- **WHEN** the browser triggers the `concert-refresh` periodic sync event
- **THEN** the Service Worker SHALL fetch the concert-list endpoint for the user's configured area
- **AND** the Service Worker SHALL update the `concert-api-v1` cache with the fresh response

#### Scenario: Periodic sync fails
- **WHEN** the periodic sync network request fails
- **THEN** the Service Worker SHALL silently discard the failure
- **AND** the system SHALL NOT show any user-facing error
- **AND** the browser SHALL retry the periodic sync at the next scheduled interval

### Requirement: Periodic Sync Browser Support
The system SHALL degrade gracefully when the Periodic Background Sync API is not supported.

#### Scenario: Browser does not support Periodic Background Sync
- **WHEN** the browser does not support the `periodicSync` API (e.g., Safari, Firefox)
- **THEN** the system SHALL NOT attempt to register a periodic sync task
- **AND** the system SHALL rely on the NetworkFirst caching strategy during active app usage to refresh concert data
- **AND** the system SHALL NOT produce any error or console warning
