## MODIFIED Requirements

### Requirement: Data Aggregation Orchestration
The system SHALL only be used for authenticated users who need `loadingService.aggregateData()` after following artists. It SHALL NOT be entered during the onboarding tutorial flow. The system SHALL trigger `SearchNewConcerts` for each followed artist in parallel during the loading sequence.

#### Scenario: Successful aggregation for all artists
- **WHEN** the loading sequence starts
- **THEN** the system SHALL call `ListFollowedArtists` to retrieve the user's followed artists
- **AND** the system SHALL call `SearchNewConcerts` for each followed artist in parallel
- **AND** upon all searches completing, the system SHALL navigate to the Dashboard

#### Scenario: Partial failure
- **WHEN** `SearchNewConcerts` fails for one or more artists
- **THEN** the system SHALL proceed with successfully retrieved data
- **AND** the system SHALL NOT block navigation due to individual artist failures

#### Scenario: Initial artist list retrieval failure
- **WHEN** the loading sequence starts
- **AND** the `ListFollowedArtists` RPC fails with a retriable error after retries
- **THEN** the system SHALL navigate to the Dashboard
- **AND** the system SHALL NOT display an infinite loading state

#### Scenario: Artist list retrieval canceled by abort signal
- **WHEN** the loading sequence starts
- **AND** the `ListFollowedArtists` RPC is in-flight
- **AND** the global timeout fires and aborts the request via AbortSignal
- **THEN** the system SHALL immediately propagate the cancellation error without retrying
- **AND** the system SHALL NOT increment the retry counter
- **AND** the system SHALL NOT emit retry log messages
