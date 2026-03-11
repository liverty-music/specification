### Requirement: Onboarding guidance rendered within unified DiscoverPage
The onboarding guidance HUD (progress dots, guidance message, CTA button) SHALL be rendered as a conditional section within `DiscoverPage` at `/discover`, instead of in a separate page.

#### Scenario: Onboarding user navigates to discover
- **WHEN** `OnboardingService.isOnboarding` is `true` and the user navigates to `/discover`
- **THEN** the onboarding HUD (progress dots + guidance message) SHALL be visible
- **AND** the search bar and genre filter SHALL also be available

#### Scenario: Normal user navigates to discover
- **WHEN** `OnboardingService.isOnboarding` is `false` and the user navigates to `/discover`
- **THEN** the onboarding HUD SHALL NOT be rendered
- **AND** no CTA button SHALL be shown (bottom navigation provides transitions)

#### Scenario: CTA button removed during onboarding
- **REMOVED**: The "ダッシュボードを生成する" CTA button is removed from the discover page. The CTA is replaced by a coach mark spotlight on the nav-bar Dashboard icon (defined in `onboarding-tutorial` Step 1 completion).

**Reason**: The nav-bar Dashboard icon spotlight teaches users about navigation while serving as the CTA. A separate button is redundant.
**Migration**: Remove the `complete-button-wrapper` and `complete-button` elements from `discover-page.html`. CTA behavior is handled by the coach mark component targeting `[data-nav-dashboard]`.

### Requirement: Followed count reflects localStorage state
The `LocalArtistClient.followedCount` property SHALL be an `@observable` that is updated whenever `follow()`, `unfollow()`, or `clearAll()` is called, so that Aurelia bindings re-evaluate immediately.

#### Scenario: Initial page load with existing guest data
- **WHEN** the user navigates to `/discover` during onboarding and `localStorage['guest.followedArtists']` contains 3 artists
- **THEN** the counter SHALL display `3/3` and the complete button SHALL be visible

#### Scenario: Follow an artist during onboarding
- **WHEN** the user taps a bubble to follow an artist
- **THEN** the counter SHALL increment by 1 within the same frame (e.g., `0/3` → `1/3`)
- **AND** the progress bar fill width SHALL update accordingly

#### Scenario: Unfollow an artist
- **WHEN** the user unfollows a previously followed artist
- **THEN** the counter SHALL decrement by 1 immediately

### Requirement: Persistent guidance until first interaction
The onboarding guidance message SHALL remain visible until the user taps their first bubble. There SHALL be no auto-dismiss timer.

#### Scenario: Page load without prior interactions
- **WHEN** the user arrives at the discovery page for the first time (followedCount = 0)
- **THEN** the guidance message "好きなアーティストを3組タップしよう！" SHALL be displayed
- **AND** the message SHALL NOT auto-dismiss after any timeout

#### Scenario: First bubble tap dismisses guidance
- **WHEN** the user taps their first bubble
- **THEN** the guidance message SHALL fade out (400ms transition)
- **AND** a progress-specific message SHALL appear in its place

### Requirement: Staged progress messages
The system SHALL display contextual progress messages that change as the user follows more artists.

#### Scenario: After following 1 artist
- **WHEN** followedCount becomes 1
- **THEN** the guidance area SHALL display "いいね！あと2組！"

#### Scenario: After following 2 artists
- **WHEN** followedCount becomes 2
- **THEN** the guidance area SHALL display "あと1組！"

#### Scenario: After following 3 or more artists
- **WHEN** followedCount reaches 3 (TUTORIAL_FOLLOW_TARGET)
- **THEN** the guidance area SHALL display "準備完了！"
- **AND** the system SHALL NOT display a separate CTA button
- **AND** the progress bar SHALL switch to showing concert search completion status

### Requirement: Orb pulse on follow
The central Music DNA orb SHALL pulse each time an artist is followed, providing visual feedback that the selection was registered.

#### Scenario: Bubble tap triggers orb pulse
- **WHEN** a bubble is tapped and the follow operation succeeds
- **THEN** the `DnaOrbCanvas.followedCountChanged` callback SHALL fire
- **AND** the orb SHALL play a pulse animation

### Requirement: Search and genre filter available during onboarding
The search bar and genre filter chips SHALL be visible and functional during onboarding, allowing users to find specific artists they already know.

#### Scenario: Onboarding user searches for an artist
- **WHEN** the user is in onboarding mode and types a query into the search bar
- **THEN** search results SHALL appear and the user SHALL be able to follow artists from the results
- **AND** the follow operation SHALL use the same unified flow (localStorage during onboarding)

### Requirement: Complete button is tappable on all devices (REMOVED)

**Reason**: The CTA button has been removed. Dashboard transition is now triggered via the coach mark spotlight on the nav-bar Dashboard icon (see `onboarding-tutorial` Step 1 completion).
**Migration**: Remove `complete-button-wrapper` and `complete-button` elements and related event handlers.

### Requirement: Concert Search Progress Bar

The system SHALL display a progress bar on the discover page that tracks concert search completion for followed artists, replacing the numeric counter after 3 artists are followed.

#### Scenario: Progress bar appears after 3 follows

- **WHEN** `followedCount >= 3` during onboarding
- **THEN** the progress bar SHALL display below the guidance message
- **AND** the progress bar fill width SHALL represent `completedSearchCount / followedCount * 100%`
- **AND** the progress bar SHALL use a continuous fill animation (not discrete steps)

#### Scenario: Concert search completes for an artist

- **WHEN** a `SearchNewConcerts` call completes (success or timeout) for a followed artist
- **THEN** the progress bar fill SHALL update to reflect the new completion ratio
- **AND** the update SHALL animate smoothly (300ms transition)

#### Scenario: All searches complete

- **WHEN** all followed artists (minimum 3) have completed concert searches
- **THEN** the system SHALL activate the nav-bar Dashboard icon coach mark (per `onboarding-tutorial` Step 1 completion)

#### Scenario: Search timeout

- **WHEN** a concert search for an artist exceeds 15 seconds
- **THEN** the system SHALL treat the search as completed for progress bar purposes
- **AND** the system SHALL NOT block CTA activation due to the timeout

### Requirement: No z-index stacking in discovery page CSS
The discovery page SHALL NOT use `z-index` for visual stacking. All layer ordering SHALL be achieved through DOM source order.

#### Scenario: Overlay elements paint above canvas
- **WHEN** the discovery page renders
- **THEN** the onboarding HUD, orb label, and complete button SHALL paint above the canvas
- **AND** no CSS `z-index` property SHALL be present in the discovery page CSS

#### Scenario: Starfield pseudo-element paints behind content
- **WHEN** the discovery page renders
- **THEN** the `.container::before` starfield SHALL paint behind all content elements
- **AND** the starfield SHALL use `pointer-events: none` without `z-index`
