## ADDED Requirements

### Requirement: Progressive Loading Animation
The system SHALL display a multi-phase animated loading sequence during data aggregation, replacing a simple spinner.

#### Scenario: Phase 1 display (0-2 seconds)
- **WHEN** the loading sequence begins
- **THEN** the system SHALL display the message "あなたのMusic DNAを構築中..."
- **AND** the message SHALL appear with a fade-in animation

#### Scenario: Phase 2 display (2-5 seconds)
- **WHEN** 2 seconds have elapsed since the loading sequence began
- **THEN** the system SHALL transition to display the message "全国のライブスケジュールと照合中..."
- **AND** the transition SHALL use a smooth crossfade animation

#### Scenario: Phase 3 display (5+ seconds)
- **WHEN** 5 seconds have elapsed since the loading sequence began
- **THEN** the system SHALL transition to display the message "AIが最新のツアー情報を検索中... 🤖"

### Requirement: Minimum Display Duration
The system SHALL enforce a minimum 3-second display time for the loading sequence regardless of data loading speed.

#### Scenario: Fast data load
- **WHEN** all data aggregation completes in under 3 seconds
- **THEN** the system SHALL continue displaying the loading animation until 3 seconds have elapsed
- **AND** the system SHALL then navigate to the Dashboard

#### Scenario: Normal data load
- **WHEN** data aggregation completes after 3 or more seconds
- **THEN** the system SHALL navigate to the Dashboard immediately upon completion

### Requirement: Data Aggregation Orchestration
The system SHALL trigger `SearchNewConcerts` for each followed artist in parallel during the loading sequence.

#### Scenario: Successful aggregation for all artists
- **WHEN** the loading sequence starts
- **THEN** the system SHALL call `ListFollowedArtists` to retrieve the user's followed artists
- **AND** the system SHALL call `SearchNewConcerts` for each followed artist in parallel
- **AND** upon all searches completing, the system SHALL navigate to the Dashboard

#### Scenario: Partial failure
- **WHEN** `SearchNewConcerts` fails for one or more artists
- **THEN** the system SHALL proceed with successfully retrieved data
- **AND** the system SHALL NOT block navigation due to individual artist failures

### Requirement: Global Timeout
The system SHALL enforce a 10-second global timeout on data aggregation to prevent infinite loading states.

#### Scenario: Timeout fires
- **WHEN** 10 seconds have elapsed and data aggregation has not completed
- **THEN** the system SHALL abort all remaining search requests
- **AND** the system SHALL navigate to the Dashboard with only the successfully retrieved data
- **AND** the system SHALL NOT display an error message

### Requirement: Navigation Guard
The system SHALL prevent direct access to the loading sequence route.

#### Scenario: Direct URL access while unauthenticated
- **WHEN** an unauthenticated user navigates directly to `/onboarding/loading`
- **THEN** the system SHALL redirect to the Landing Page (`/`)

#### Scenario: Direct URL access while authenticated with completed onboarding
- **WHEN** an authenticated user with ≥1 followed artist navigates directly to `/onboarding/loading`
- **THEN** the system SHALL redirect to the Dashboard (`/dashboard`)

#### Scenario: Direct URL access while authenticated without followed artists
- **WHEN** an authenticated user with no followed artists navigates directly to `/onboarding/loading`
- **THEN** the system SHALL redirect to the Artist Discovery page (`/onboarding/discover`)
