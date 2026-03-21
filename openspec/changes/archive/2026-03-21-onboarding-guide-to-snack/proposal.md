## Why

The onboarding popover guide on the discover page has poor visibility — its translucent gradient background blends into the bubble canvas, making it easy to miss. Replacing it with the existing snack-bar notification system unifies the visual language (tone & manner) across the app and leverages a proven, accessible notification pattern with better contrast and positioning.

## What Changes

- Remove the `<dialog popover="auto" class="onboarding-guide">` element from `discovery-route.html`
- Remove the `onboardingGuide` ref, `showPopover()` call in `attached()`, and related template/CSS (~50 lines)
- Publish a `Snack` event via `IEventAggregator` in `attached()` when `isOnboarding` is true, with a longer duration (4000–5000 ms) so users have time to read the message
- The snack-bar's existing auto-dismiss replaces the popover's light-dismiss; no explicit tap is required to proceed to bubble interaction

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `onboarding-popover-guide`: Replace Popover API `<dialog>` with snack-bar notification. The guide message is now delivered as an `info`-severity snack instead of a standalone popover, changing dismiss behavior from light-dismiss to auto-dismiss.
- `onboarding-guidance`: The discover page no longer renders a popover element for onboarding; guidance is handled by the global snack-bar component.

## Impact

- **Frontend only** — no backend, proto, or infrastructure changes
- `discovery-route.ts` / `.html` / `.css`: Template simplification, CSS deletion
- `snack-bar`: No changes needed (existing API supports this use case)
- E2E test `onboarding-flow.spec.ts`: Update popover assertions to snack-bar assertions
- Unit test `discovery-route.spec.ts`: Update `showPopover` mocks to `ea.publish(Snack)` assertions
