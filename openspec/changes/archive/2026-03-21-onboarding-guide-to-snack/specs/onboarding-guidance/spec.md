## MODIFIED Requirements

### Requirement: Onboarding guidance rendered within unified DiscoverPage
The onboarding guidance SHALL be delivered as a snack-bar notification within the global `<snack-bar>` component, instead of as a Popover API element within `DiscoverPage`.

#### Scenario: Onboarding user navigates to discover
- **WHEN** `OnboardingService.isOnboarding` is `true` and the user navigates to `/discover`
- **THEN** the onboarding snack notification SHALL be shown via `ea.publish(new Snack(...))`
- **AND** the search bar and genre filter SHALL also be available
- **AND** the discover page grid SHALL have 3 rows (`auto auto 1fr`), not 4

#### Scenario: Normal user navigates to discover
- **WHEN** `OnboardingService.isOnboarding` is `false` and the user navigates to `/discover`
- **THEN** no onboarding notification SHALL appear
- **AND** no CTA button SHALL be shown (bottom navigation provides transitions)

#### Scenario: CTA button removed during onboarding
- **REMOVED**: The "ダッシュボードを生成する" CTA button is removed from the discover page. The CTA is replaced by a coach mark spotlight on the nav-bar Dashboard icon (defined in `onboarding-tutorial` Step 1 completion).

**Reason**: The nav-bar Dashboard icon spotlight teaches users about navigation while serving as the CTA. A separate button is redundant.
**Migration**: Remove the `complete-button-wrapper` and `complete-button` elements from `discover-page.html`. CTA behavior is handled by the coach mark component targeting `[data-nav-dashboard]`.

### Requirement: No z-index stacking in discovery page CSS
The discovery page SHALL NOT use `z-index` for visual stacking. The snack-bar renders in the top layer automatically via Popover API; all other layer ordering SHALL be achieved through DOM source order.

#### Scenario: Overlay elements paint above canvas
- **WHEN** the discovery page renders
- **THEN** the orb label SHALL paint above the canvas via DOM order
- **AND** no CSS `z-index` property SHALL be present in the discovery page CSS

#### Scenario: Snack notification renders in top layer
- **WHEN** the onboarding snack is shown
- **THEN** it SHALL render in the browser's top layer via the snack-bar's Popover API usage
- **AND** no manual `z-index` management SHALL be needed
