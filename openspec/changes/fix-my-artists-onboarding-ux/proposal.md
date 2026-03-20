## Why

During onboarding Step 5 (My Artists), four UX bugs prevent the flow from completing correctly. The root cause is a responsibility violation: `HypeInlineSlider` contains business logic (auth gate, event branching) that belongs in the parent route. Since the user is a guest, the auth gate blocks all dot taps, `hype-changed` never fires, and `setStep(COMPLETED)` is never reached — the user is permanently stuck. Secondary issues degrade the visual quality of the step (wrong spotlight target, misaligned slider track, incorrect default hype).

## What Changes

- **Refactor hype slider to pure presentation component**: Remove all business logic (`selectHype`, `isAuthenticated`, `isOnboarding`) from `HypeInlineSlider`. The slider becomes a data-only component with twoWay binding on `hype`; user interaction updates the binding and the native `change` event bubbles to the parent.
- **Move business logic to parent route**: `MyArtistsRoute` handles the native `change` event via `onHypeInput()` with three branches: onboarding → complete; unauthenticated → signup prompt; authenticated → optimistic update + RPC. Rejected selections are reverted by pushing the previous value back via twoWay binding.
- **Spotlight target widened to artist list**: Change from `[data-hype-header]` (legend row only) to `.artist-list` (the interactive area).
- **Hype slider track vertical centering**: Add `inset-block-start: 50%; translate: 0 -50%` to center the track line.
- **Default hype level corrected**: Guest follows default from `'away'` → `'watch'`.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `hype-inline-slider`: Refactor to pure presentation component. Remove auth/onboarding logic. Replace `hype-changed`/`hype-signup-prompt` custom events with twoWay `hype` binding; native `change` event bubbles to parent. Fix track vertical alignment.
- `onboarding-tutorial`: Step 5 spotlight target changes from `[data-hype-header]` to `.artist-list`. Step 5 completion handled by parent route via `onHypeInput()` reacting to native `change` event.
- `frontend-onboarding-flow`: Guest follow default hype corrected from `'away'` to `'watch'`.

## Impact

- **Frontend only** — no backend, proto, or infrastructure changes.
- Files affected:
  - `src/components/hype-inline-slider/hype-inline-slider.ts` — remove `selectHype`, `isAuthenticated`, `isOnboarding`; retain only data bindables
  - `src/components/hype-inline-slider/hype-inline-slider.html` — replace `click.trigger`
  - `src/components/hype-inline-slider/hype-inline-slider.css` — track centering fix
  - `src/routes/my-artists/my-artists-route.ts` — replace `onHypeChanged` + `onHypeSignupPrompt` with `onHypeInput`; spotlight target
  - `src/routes/my-artists/my-artists-route.html` — replace event bindings; remove `is-authenticated`/`is-onboarding`
  - `src/services/follow-service-client.ts` — default hype value
  - `test/routes/my-artists-route.spec.ts` — updated for new event flow
