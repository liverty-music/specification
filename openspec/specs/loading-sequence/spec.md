## Purpose

This capability defines the loading sequence experience displayed during data aggregation for authenticated users who need post-follow concert data aggregation. The loading sequence provides an engaging, multi-phase animated experience that maintains user engagement during the 3-10 second processing time required to search for live event data across followed artists. This route is NOT used during the onboarding tutorial flow.

## Requirements

### Requirement: Progressive Loading Animation
The system SHALL display a multi-phase animated loading sequence with visual richness during data aggregation, replacing a simple spinner.

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

#### Scenario: Visual progress indicator
- **WHEN** the loading sequence is active
- **THEN** the system SHALL display a visual progress indicator (e.g., progress bar, step dots, or animated ring)
- **AND** the indicator SHALL advance through the phases to communicate progress
- **AND** the indicator SHALL be styled using the design system's brand accent color

#### Scenario: Step indicator display
- **WHEN** the loading sequence transitions between phases
- **THEN** the system SHALL display a step indicator showing the current phase number (e.g., "1/3", "2/3", "3/3") or equivalent visual dots
- **AND** completed phases SHALL be visually distinguished from pending phases

#### Scenario: Visual effects beyond text
- **WHEN** the loading sequence is displayed
- **THEN** the system SHALL include at least one animated visual element beyond text (e.g., pulsing orb, particle animation, or animated gradient)
- **AND** the visual element SHALL enhance the feeling of "something being built" to match the messages

---

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
- **AND** the `ListFollowedArtists` RPC fails after retries
- **THEN** the system SHALL navigate to the Dashboard
- **AND** the system SHALL NOT display an infinite loading state

---

### Requirement: Global Timeout
The system SHALL enforce a 10-second global timeout on data aggregation to prevent infinite loading states.

#### Scenario: Timeout fires
- **WHEN** 10 seconds have elapsed and data aggregation has not completed
- **THEN** the system SHALL abort all remaining search requests
- **AND** the system SHALL navigate to the Dashboard with only the successfully retrieved data
- **AND** the system SHALL NOT display an error message

---

### Requirement: Navigation Guard
The system SHALL prevent direct access to the loading sequence route.

#### Scenario: Onboarding user reaches loading-sequence
- **WHEN** an onboarding user navigates to `/onboarding/loading`
- **THEN** the system SHALL redirect to the Dashboard (`/dashboard`)

#### Scenario: Direct URL access while unauthenticated
- **WHEN** an unauthenticated user navigates directly to `/onboarding/loading`
- **THEN** the system SHALL redirect to the Landing Page (`/`)

#### Scenario: Direct URL access while authenticated with completed onboarding
- **WHEN** an authenticated user with ≥1 followed artist navigates directly to `/onboarding/loading`
- **THEN** the system SHALL redirect to the Dashboard (`/dashboard`)

#### Scenario: Direct URL access while authenticated without followed artists
- **WHEN** an authenticated user with no followed artists navigates directly to `/onboarding/loading`
- **THEN** the system SHALL redirect to the Artist Discovery page (`/onboarding/discover`)

---

### Requirement: Visual Continuity
The loading sequence SHALL maintain a dark-themed visual presentation consistent with the application's immersive screens.

#### Scenario: Consistent visual theme
- **WHEN** the loading sequence is displayed
- **THEN** the background SHALL use a dark gradient consistent with the application's immersive screen aesthetic
- **AND** the transition into the loading sequence SHALL not introduce a jarring visual break

---

### Requirement: CSS Stacking via Isolation
All z-index declarations in `loading-sequence.css` SHALL be removed. The root wrapper element SHALL use `isolation: isolate` to create an explicit stacking context. Within this boundary, elements stack by DOM source order (later siblings paint above earlier ones) without z-index.
