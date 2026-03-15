## Why

The onboarding flow shipped in PR #146 has multiple UX bugs that break the tutorial experience: the "Login required" toast fires incorrectly during onboarding, the spotlight overlay doesn't visually highlight the target element, the progress bar contradicts the guidance message, and the Home nav button silently fails to navigate. These issues make the onboarding confusing and unusable — users cannot complete the tutorial as designed.

## What Changes

- **Fix auth redirect during onboarding**: When an onboarding user taps a route without `tutorialStep` (Tickets, Settings), redirect silently to the current step's route instead of showing a "Login required" toast.
- **Fix spotlight visibility**: Replace the broken box-shadow-on-child approach with a CSS Anchor Positioning hybrid (visual spotlight via `box-shadow` on an anchor-positioned element + transparent click-blockers). This makes the spotlight cutout actually visible with border-radius support.
- **Remove progress bar, add DNA orb color injection**: Remove the concert-search progress bar (which contradicts the guidance message). Instead, when a bubble is absorbed into the orb, inject that bubble's hue into the orb's particle system with a swirl animation — making the orb visually richer as more artists are followed.
- **Fix Home nav during onboarding**: Spotlight the Home icon as the coach mark target. When tapped, advance the onboarding step to DASHBOARD and navigate. Also handle direct nav-bar clicks during onboarding by advancing the step if the user has met the follow threshold.
- **Fix toast popover white background leak**: Reset UA default styles on the toast popover container to prevent white background bleeding at corners.
- **Add tests**: Add unit and integration tests covering the fixed behaviors to prevent regression.

## Capabilities

### New Capabilities

- `onboarding-spotlight`: Coach mark spotlight implementation using CSS Anchor Positioning hybrid (visual box-shadow layer + transparent click-blockers), replacing the broken overlay+child box-shadow approach.
- `dna-orb-color-injection`: DNA orb particle color injection — absorbing a followed artist's bubble injects its hue into the orb's particle system with a swirl animation.

### Modified Capabilities

- `frontend-onboarding-flow`: Auth redirect behavior during onboarding changes (no toast for non-tutorial routes), progress bar removed, Home nav spotlight added.
- `frontend-route-guard`: AuthHook gains an onboarding-aware fallback that redirects without toast when tutorialStep is undefined but user is in onboarding.
- `onboarding-tutorial`: Tutorial step progression updated — Home nav click advances step to DASHBOARD when follow threshold is met.

## Impact

- **Frontend components**: `coach-mark/`, `toast-notification/`, `dna-orb/orb-renderer.ts`, `dna-orb/dna-orb-canvas.ts`, `bottom-nav-bar/`
- **Frontend hooks**: `auth-hook.ts` (redirect logic change)
- **Frontend routes**: `discover-page.ts` (progress bar removal, orb integration), `discover-page.html`, `discover-page.css`
- **Tests**: New test files for auth-hook onboarding scenarios, coach-mark spotlight visibility, orb color injection, discover-page guidance consistency
- **No backend or proto changes required**
