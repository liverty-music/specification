## MODIFIED Requirements

### Requirement: Loading Sequence with Benevolent Deception
The system SHALL provide an engaging loading experience during data aggregation to maintain user engagement during processing time (3-10 seconds).

#### Scenario: Data loading with progressive messaging
- **WHEN** the system begins aggregating live event data for followed artists
- **THEN** the system SHALL display a multi-step animated loading sequence (NOT a simple spinner)
- **AND** Phase 1 (0-2s) SHALL display: "あなたのMusic DNAを構築中..."
- **AND** Phase 2 (2-5s) SHALL display: "全国のライブスケジュールと照合中..."
- **AND** Phase 3 (5s+) SHALL display: "AIが最新のツアー情報を検索中... 🤖"
- **AND** the system SHALL enforce a minimum 3-second display duration even if data loading completes earlier
- **AND** the system SHALL call `SearchNewConcerts` for each followed artist in parallel
- **AND** the system SHALL use a 10-second global timeout via `AbortController`

#### Scenario: Loading timeout handling
- **WHEN** data loading exceeds 10 seconds
- **THEN** the system SHALL terminate all remaining search requests
- **AND** the system SHALL proceed to the Dashboard with only the successfully retrieved artist data
- **AND** the system SHALL NOT display an infinite loading state

#### Scenario: Transition from Artist Discovery
- **WHEN** the user completes the Artist Discovery step
- **THEN** the system SHALL navigate to `/onboarding/loading`
- **AND** the loading sequence SHALL automatically begin data aggregation
- **AND** upon completion, the system SHALL navigate to the Dashboard
