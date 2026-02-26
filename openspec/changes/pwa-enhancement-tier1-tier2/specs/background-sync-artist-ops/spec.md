## ADDED Requirements

### Requirement: Offline Artist Operation Queuing
The system SHALL queue artist follow, unfollow, and passion-level change operations when the device is offline and automatically replay them when connectivity is restored.

#### Scenario: Follow artist while offline
- **WHEN** the user follows an artist while the device is offline
- **THEN** the system SHALL apply the follow optimistically in the UI
- **AND** the Service Worker SHALL queue the failed network request via Background Sync API
- **AND** the queue SHALL be stored in IndexedDB under the queue name `artist-ops-queue`

#### Scenario: Unfollow artist while offline
- **WHEN** the user unfollows an artist while the device is offline
- **THEN** the system SHALL apply the unfollow optimistically in the UI
- **AND** the Service Worker SHALL queue the failed network request via Background Sync API

#### Scenario: Change passion level while offline
- **WHEN** the user changes an artist's passion level while the device is offline
- **THEN** the system SHALL apply the passion level change optimistically in the UI
- **AND** the Service Worker SHALL queue the failed network request via Background Sync API

#### Scenario: Connectivity restored — queue replay
- **WHEN** network connectivity is restored
- **THEN** the Service Worker SHALL replay all queued requests from `artist-ops-queue` in FIFO order
- **AND** successfully replayed requests SHALL be removed from the queue
- **AND** requests that fail after replay SHALL be retried according to Workbox BackgroundSync retry policy

#### Scenario: Queue retention limit
- **WHEN** a queued request has been in the queue for more than 7 days without successful replay
- **THEN** the Service Worker SHALL discard the request from the queue
- **AND** the system SHALL NOT notify the user of the discarded request

### Requirement: Background Sync Browser Support
The system SHALL degrade gracefully when the Background Sync API is not supported.

#### Scenario: Browser does not support Background Sync
- **WHEN** the browser does not support the Background Sync API
- **THEN** the system SHALL fall back to standard network error behavior
- **AND** the system SHALL NOT queue requests or attempt SW-based retry
- **AND** the system SHALL display a standard network error message to the user
