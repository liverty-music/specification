## MODIFIED Requirements

### Requirement: Interactive Artist Discovery (Bubble Network UI)

The system SHALL provide an engaging, gamified interface for users to discover and follow artists using Last.fm API data. During the tutorial, followed artists are stored locally (not via backend RPC). Additionally, the system SHALL trigger a background concert search for each followed artist to pre-populate concert data for the Dashboard. The DNA orb SHALL visually evolve as artists are followed, incorporating each artist's color into its particle system.

#### Scenario: Initial artist bubble display

- **WHEN** a user reaches the Artist Discovery step (Step 1)
- **THEN** the system SHALL call Last.fm's `geo.getTopArtists` API with `country=japan`
- **AND** the system SHALL display approximately 30 top artists as floating circular bubbles with physics-based animation

#### Scenario: Guest user follows artist via bubble tap

- **WHEN** a guest user (in tutorial) taps an artist bubble
- **THEN** the system SHALL trigger the absorption animation
- **AND** the system SHALL store the artist in `liverty:guest:followedArtists` in LocalStorage
- **AND** the system SHALL NOT call any backend RPC for the follow operation itself
- **AND** the system SHALL call `ConcertService/SearchNewConcerts` fire-and-forget in the background
- **AND** errors from `SearchNewConcerts` SHALL be logged to console and NOT affect the follow operation or UI
- **AND** upon absorption completion, the bubble's hue SHALL be injected into the orb's particle system with a swirl animation

#### Scenario: Discover to Dashboard transition

- **WHEN** a user is at Step 1 (Artist Discovery)
- **AND** the user has followed >= 3 artists
- **AND** concert search results have been received for all followed artists (or timed out)
- **THEN** the system SHALL activate a coach mark spotlight on the Dashboard icon in the bottom navigation bar
- **AND** the system SHALL display the coach mark message: "タイムテーブルを見てみよう！"
- **AND** when the user taps the Dashboard icon through the spotlight, the system SHALL advance `onboardingStep` to 3 (DASHBOARD)
- **AND** the system SHALL navigate to `/dashboard`

#### Scenario: Concert data availability at Dashboard

- **WHEN** the user arrives at the Dashboard after completing Artist Discovery
- **THEN** concert data MAY already be available from the fire-and-forget `SearchNewConcerts` calls triggered during artist follows in Discovery
- **AND** the Dashboard SHALL display its own loading skeleton / promise states for any data still pending
- **AND** the system SHALL NOT rely on a loading screen to mask data fetching

## REMOVED Requirements

### Requirement: Progress bar reaches target

**Reason**: The progress bar tracked concert search completion which contradicted the guidance message tracking follow count. Replaced by DNA orb color evolution as visual feedback for follow progress.

**Migration**: Remove `search-progress-bar` HTML/CSS from discover-page template. Remove `searchProgress` getter from DiscoverPage. The `completedSearchCount` tracking remains for the `showDashboardCoachMark` condition.

### Requirement: Step 1 - Progress bar display

**Reason**: Same as above. The progress bar is removed and replaced by DNA orb visual feedback.

**Migration**: Remove the progress bar UI. The concert search tracking logic remains internally for gating the coach mark appearance.

## Test Cases

### Unit Tests (Vitest — discover-page.spec.ts)

#### TC-OF-01: Progress bar elements are absent from template

- **Given** the discover-page component is rendered
- **Then** no `.search-progress-bar` or `.search-progress-fill` elements SHALL exist in the DOM

#### TC-OF-02: searchProgress getter is removed

- **Given** the DiscoverPage class
- **Then** no `searchProgress` property or getter SHALL exist
- **And** `completedSearchCount` SHALL still be available (used by `showDashboardCoachMark`)

#### TC-OF-03: showDashboardCoachMark gates on follow count and search completion

- **Given** `onboardingStep = 1`
- **When** `followedArtists.length >= 3` AND `completedSearchCount >= followedArtists.length`
- **Then** `showDashboardCoachMark` SHALL be `true`

### Unit Tests (Vitest — toast-notification.spec.ts)

#### TC-OF-04: Toast popover container has transparent background

- **Given** the toast-notification component uses `popover="manual"`
- **Then** the popover container SHALL have CSS class `toast-popover`
- **And** the CSS rule `[popover].toast-popover` SHALL set `background: transparent`, `border: none`, `padding: 0`, `margin: 0`
