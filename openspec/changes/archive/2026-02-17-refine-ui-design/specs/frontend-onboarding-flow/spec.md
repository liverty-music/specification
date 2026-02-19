## MODIFIED Requirements

### Requirement: Just-in-Time Region Configuration
The system SHALL collect the user's primary residential area using a Just-in-Time approach, presenting the region selector as an overlay on the dashboard to minimize setup friction.

#### Scenario: Region setup overlay on first dashboard access
- **WHEN** the user completes the Loading Sequence and accesses the Dashboard for the first time
- **AND** the user has not yet configured their region
- **THEN** the system SHALL display the Dashboard with a blurred background
- **AND** the system SHALL present a bottom sheet overlay with the message "To find live events near you, tell us your main area"
- **AND** the system SHALL provide a prefecture dropdown selector or quick-select buttons for major cities
- **AND** the bottom sheet SHALL use the design system's dark surface palette and sheet radius token

#### Scenario: Magic moment after region selection
- **WHEN** the user selects their region in the bottom sheet
- **THEN** the system SHALL immediately close the bottom sheet
- **AND** the system SHALL unblur the Dashboard background with a smooth transition animation
- **AND** the system SHALL dynamically populate the Live Highway UI with region-relevant events
- **AND** this SHALL create a "magic moment" where personalized content appears instantly

### Requirement: Loading Sequence with Benevolent Deception
The system SHALL provide an engaging loading experience with visual richness during data aggregation to maintain user engagement during processing time (3-10 seconds).

#### Scenario: Data loading with progressive messaging
- **WHEN** the system begins aggregating live event data for followed artists
- **THEN** the system SHALL display a multi-step animated loading sequence (NOT a simple spinner)
- **AND** Phase 1 (0-2s) SHALL display: "あなたのMusic DNAを構築中..."
- **AND** Phase 2 (2-5s) SHALL display: "全国のライブスケジュールと照合中..."
- **AND** Phase 3 (5s+) SHALL display: "AIが最新のツアー情報を検索中... 🤖"
- **AND** the system SHALL enforce a minimum 3-second display duration even if data loading completes earlier
- **AND** the system SHALL call `SearchNewConcerts` for each followed artist in parallel
- **AND** the system SHALL use a 10-second global timeout via `AbortController`
- **AND** the system SHALL display a visual progress indicator advancing through the phases

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
- **AND** the page transition SHALL use the design system's transition animation

## ADDED Requirements

### Requirement: Onboarding Flow Visual Continuity
The system SHALL maintain visual continuity throughout the entire onboarding flow from Landing Page through Dashboard.

#### Scenario: Consistent visual language
- **WHEN** the user progresses through the onboarding flow (Landing → Discovery → Loading → Dashboard)
- **THEN** every screen SHALL use the same dark theme surface palette
- **AND** every screen SHALL use the same display font for headings
- **AND** route transitions between screens SHALL use the page transition animation defined in the app-shell-layout spec
- **AND** there SHALL be no visual discontinuity (e.g., white-to-dark jumps) between screens
