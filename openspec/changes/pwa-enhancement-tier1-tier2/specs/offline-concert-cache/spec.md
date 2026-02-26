## ADDED Requirements

### Requirement: Concert List Offline Cache
The system SHALL cache concert-list API responses using a NetworkFirst strategy so users can browse previously loaded concert data when offline.

#### Scenario: Online request — fresh data served
- **WHEN** the user loads the dashboard while online
- **THEN** the Service Worker SHALL attempt to fetch concert data from the network
- **AND** the system SHALL cache the successful response in the `concert-api-v1` cache
- **AND** the system SHALL serve the fresh network response to the application

#### Scenario: Offline or slow network — cached data served
- **WHEN** the user loads the dashboard while offline or the network request exceeds 3 seconds
- **THEN** the Service Worker SHALL serve the most recent cached response from the `concert-api-v1` cache
- **AND** the dashboard SHALL display a visual indicator (e.g., subtle banner or badge) communicating that cached data is being shown

#### Scenario: No cached data available while offline
- **WHEN** the user loads the dashboard while offline
- **AND** no cached concert data exists
- **THEN** the system SHALL display an empty state message indicating no cached data is available
- **AND** the system SHALL NOT display a loading spinner indefinitely

#### Scenario: Cache expiration
- **WHEN** cached concert data is older than 24 hours
- **THEN** the Service Worker SHALL evict the expired entries from the `concert-api-v1` cache
- **AND** the cache SHALL retain a maximum of 50 entries

### Requirement: Stale Data Indicator
The system SHALL inform users when concert data is served from cache rather than from the live network.

#### Scenario: Cached response detected
- **WHEN** the dashboard receives a response served from the Service Worker cache
- **THEN** the system SHALL display a non-intrusive indicator (e.g., "Showing cached data" text or icon)
- **AND** the indicator SHALL be visually distinct but not disruptive to the browsing experience

#### Scenario: Fresh response replaces cached data
- **WHEN** the system transitions from showing cached data to receiving a fresh network response
- **THEN** the stale-data indicator SHALL be removed
- **AND** the dashboard SHALL update with the fresh data
