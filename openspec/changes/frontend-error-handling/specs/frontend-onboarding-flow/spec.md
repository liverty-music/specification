## MODIFIED Requirements

### Requirement: Interactive Artist Discovery (Bubble Network UI)
The system SHALL provide an engaging, gamified interface for users to discover and follow artists using Last.fm API data. The `loading()` lifecycle hook SHALL handle errors gracefully instead of crashing to a white screen.

#### Scenario: Initial artist bubble display
- **WHEN** a user reaches the Artist Discovery step
- **THEN** the system SHALL call Last.fm's `geo.getTopArtists` API with `country=japan`
- **AND** the system SHALL display approximately 30 top artists as floating circular bubbles with physics-based animation
- **AND** each bubble SHALL contain the artist's image and name

#### Scenario: Artist loading fails with error recovery
- **WHEN** the initial artist loading fails due to a network or API error
- **THEN** the system SHALL display an error state with the message and a "Retry" button
- **AND** the system SHALL NOT show a white screen
- **AND** the template SHALL use `promise.bind` to declaratively handle pending, success, and error states

#### Scenario: User selects an artist (Follow action)
- **WHEN** a user taps an artist bubble
- **THEN** the system SHALL highlight the bubble to indicate selection
- **AND** the system SHALL query the internal database for upcoming live events for that artist
- **AND** if upcoming events exist, the system SHALL display a small "[Live Available]" badge on the bubble with animation

#### Scenario: Similar artist chain reaction
- **WHEN** a user selects an artist bubble
- **THEN** the system SHALL call Last.fm's `artist.getSimilar` API using the selected artist as the seed
- **AND** the system SHALL spawn smaller bubbles representing similar artists, visually appearing to "split" from the parent bubble
- **AND** the new bubbles SHALL integrate into the physics-based layout

#### Scenario: Similar artist loading fails gracefully
- **WHEN** the similar artist API call fails
- **THEN** the system SHALL display a toast notification indicating the failure
- **AND** the system SHALL NOT crash or remove already-displayed bubbles
- **AND** the user SHALL be able to continue selecting other artists

#### Scenario: Artist follow RPC fails with rollback
- **WHEN** the fire-and-forget artist follow RPC call fails
- **THEN** the system SHALL display a toast notification "Failed to follow artist. Please try again."
- **AND** the system SHALL revert the local follow state (un-highlight the bubble)

#### Scenario: Completing artist selection
- **WHEN** a user has selected one or more artists
- **THEN** the system SHALL display a persistent floating button at the bottom of the screen showing "[Create Dashboard (X artists following)]"
- **AND** when the user taps this button, the system SHALL proceed to the Loading Sequence step

---

### Requirement: Loading Sequence with Benevolent Deception
The system SHALL provide an engaging loading experience during data aggregation to maintain user engagement during processing time (3-10 seconds). Data aggregation failures SHALL be communicated to the user instead of silently swallowed.

#### Scenario: Data loading with progressive messaging
- **WHEN** the system begins aggregating live event data for followed artists
- **THEN** the system SHALL display a multi-step animated loading sequence (NOT a simple spinner)
- **AND** Phase 1 (0-2s) SHALL display: "あなたのMusic DNAを構築中..."
- **AND** Phase 2 (2-5s) SHALL display: "全国のライブスケジュールと照合中..."
- **AND** Phase 3 (5s+) SHALL display: "AIが最新のツアー情報を検索中..."
- **AND** the system SHALL enforce a minimum 3-second display duration even if data loading completes earlier
- **AND** the system SHALL call `SearchNewConcerts` for each followed artist in parallel
- **AND** the system SHALL use a 10-second global timeout via `AbortController`
- **AND** the system SHALL display a visual progress indicator advancing through the phases

#### Scenario: Loading timeout handling
- **WHEN** data loading exceeds 10 seconds
- **THEN** the system SHALL terminate all remaining search requests
- **AND** the system SHALL proceed to the Dashboard with only the successfully retrieved artist data
- **AND** the system SHALL NOT display an infinite loading state

#### Scenario: Data aggregation partial failure
- **WHEN** some but not all `SearchNewConcerts` calls fail during loading
- **THEN** the system SHALL proceed to the Dashboard with successfully retrieved data
- **AND** the system SHALL display a toast notification on the Dashboard indicating partial data: "Some concert data could not be loaded"

#### Scenario: Data aggregation complete failure
- **WHEN** all `SearchNewConcerts` calls fail during loading
- **THEN** the system SHALL still navigate to the Dashboard
- **AND** the system SHALL display an error banner on the Dashboard indicating the failure with a "Retry" action

#### Scenario: Transition from Artist Discovery
- **WHEN** the user completes the Artist Discovery step
- **THEN** the system SHALL navigate to `/onboarding/loading`
- **AND** the loading sequence SHALL automatically begin data aggregation
- **AND** upon completion, the system SHALL navigate to the Dashboard
