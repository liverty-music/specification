## REMOVED Requirements

### Requirement: Persistent guidance until first interaction
**Reason**: Replaced by one-time popover guide (`onboarding-popover-guide` capability). The persistent HUD created a "forced task" feel and occupied grid space that reduced the bubble area.
**Migration**: Remove `.onboarding-hud` and `.hud-message` elements from `discover-page.html`. Remove associated CSS styles. Replace with popover element per `onboarding-popover-guide` spec.

### Requirement: Staged progress messages
**Reason**: Replaced by accumulating orb visual effects (`artist-discovery-dna-orb-ui` capability). The numeric countdown is replaced by visual feedback — the orb becomes more vibrant with each follow, providing implicit progress.
**Migration**: Remove `guidanceMessage` computed property and related i18n keys (`discovery.guidanceStart`, `discovery.guidanceRemaining`, `discovery.guidanceLast`, `discovery.guidanceReady`, `discovery.guidanceNoConcerts`). The `followedCount` property is retained for the coach-mark activation threshold.

### Requirement: Concert Search Progress Bar
**Reason**: The progress bar was tightly coupled to the HUD. Concert search completion continues to be tracked internally for coach-mark activation (`showDashboardCoachMark` computed), but no longer has a visible progress bar UI.
**Migration**: Remove progress bar markup and CSS from `discover-page.html`/`.css`. The `completedSearchCount` and `allSearchesComplete` properties in `discover-page.ts` are retained as they gate the dashboard spotlight activation.

## MODIFIED Requirements

### Requirement: Onboarding guidance rendered within unified DiscoverPage
The onboarding guidance SHALL be rendered as a Popover API element within `DiscoverPage` at `/discover`, instead of as an inline grid row.

#### Scenario: Onboarding user navigates to discover
- **WHEN** `OnboardingService.isOnboarding` is `true` and the user navigates to `/discover`
- **THEN** the onboarding popover guide SHALL be shown via `showPopover()`
- **AND** the search bar and genre filter SHALL also be available
- **AND** the discover page grid SHALL have 3 rows (`auto auto 1fr`), not 4

#### Scenario: Normal user navigates to discover
- **WHEN** `OnboardingService.isOnboarding` is `false` and the user navigates to `/discover`
- **THEN** no onboarding popover SHALL be rendered
- **AND** no CTA button SHALL be shown (bottom navigation provides transitions)

#### Scenario: CTA button removed during onboarding
- **REMOVED**: The "ダッシュボードを生成する" CTA button is removed from the discover page. The CTA is replaced by a coach mark spotlight on the nav-bar Dashboard icon (defined in `onboarding-tutorial` Step 1 completion).

**Reason**: The nav-bar Dashboard icon spotlight teaches users about navigation while serving as the CTA. A separate button is redundant.
**Migration**: Remove the `complete-button-wrapper` and `complete-button` elements from `discover-page.html`. CTA behavior is handled by the coach mark component targeting `[data-nav-dashboard]`.

### Requirement: Followed count reflects localStorage state
The `LocalArtistClient.followedCount` property SHALL be an `@observable` that is updated whenever `follow()`, `unfollow()`, or `clearAll()` is called, so that Aurelia bindings re-evaluate immediately.

#### Scenario: Initial page load with existing guest data
- **WHEN** the user navigates to `/discover` during onboarding and `localStorage['guest.followedArtists']` contains 3 artists
- **THEN** the orb SHALL reflect the accumulated intensity for 3 follows
- **AND** the coach-mark activation conditions SHALL evaluate correctly

#### Scenario: Follow an artist during onboarding
- **WHEN** the user taps a bubble to follow an artist
- **THEN** the orb SHALL receive a color injection with the bubble's hue
- **AND** `baseIntensity` SHALL increase per the easing curve

#### Scenario: Unfollow an artist
- **WHEN** the user unfollows a previously followed artist
- **THEN** `followedCount` SHALL decrement by 1 immediately
- **AND** `baseIntensity` SHALL NOT decrease (visual intensity is one-directional within a session)

### Requirement: Orb pulse on follow
The central Music DNA orb SHALL pulse each time an artist is followed, providing visual feedback that the selection was registered.

#### Scenario: Bubble tap triggers orb pulse
- **WHEN** a bubble is tapped and the follow operation succeeds
- **THEN** the `DnaOrbCanvas.followedCountChanged` callback SHALL fire
- **AND** the orb SHALL play a pulse animation
- **AND** the orb's `baseIntensity` SHALL increase according to the easing curve

### Requirement: Search and genre filter available during onboarding
The search bar and genre filter chips SHALL be visible and functional during onboarding, allowing users to find specific artists they already know.

#### Scenario: Onboarding user searches for an artist
- **WHEN** the user is in onboarding mode and types a query into the search bar
- **THEN** search results SHALL appear and the user SHALL be able to follow artists from the results
- **AND** the follow operation SHALL use the same unified flow (localStorage during onboarding)

### Requirement: No z-index stacking in discovery page CSS
The discovery page SHALL NOT use `z-index` for visual stacking. The popover guide renders in the top layer automatically; all other layer ordering SHALL be achieved through DOM source order.

#### Scenario: Overlay elements paint above canvas
- **WHEN** the discovery page renders
- **THEN** the orb label SHALL paint above the canvas via DOM order
- **AND** no CSS `z-index` property SHALL be present in the discovery page CSS

#### Scenario: Popover renders in top layer
- **WHEN** the onboarding popover is shown
- **THEN** it SHALL render in the browser's top layer via Popover API
- **AND** no manual `z-index` management SHALL be needed
