## Why

During onboarding Step 5 (My Artists), four UX bugs prevent the flow from completing correctly. The root cause is a responsibility violation: `HypeInlineSlider` contains business logic (auth gate, event branching) that belongs in the parent route. Since the user is a guest, the auth gate blocks all dot taps, `hype-changed` never fires, and `setStep(COMPLETED)` is never reached — the user is permanently stuck. Secondary issues degrade the visual quality of the step (wrong spotlight target, misaligned slider track, incorrect default hype).

## What Changes

- **Refactor hype slider to controlled component**: Remove all business logic (`selectHype`, `isAuthenticated`, `isOnboarding`) from `HypeInlineSlider`. The slider becomes a pure presentation component that dispatches `hype-select` on dot tap (with `preventDefault()` to block native radio change). The parent route decides whether to accept the selection.
- **Move business logic to parent route**: `MyArtistsRoute` handles the `hype-select` event with three branches: onboarding → complete; unauthenticated → signup prompt; authenticated → optimistic update + RPC.
- **Spotlight target widened to artist list**: Change from `[data-hype-header]` (legend row only) to `.artist-list` (the interactive area).
- **Hype slider track vertical centering**: Add `inset-block-start: 50%; translate: 0 -50%` to center the track line.
- **Default hype level corrected**: Guest follows default from `'away'` → `'watch'`.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `hype-inline-slider`: Refactor to controlled component pattern. Remove auth/onboarding logic. Replace `hype-changed`/`hype-signup-prompt` events with single `hype-select` event. Fix track vertical alignment.
- `onboarding-tutorial`: Step 5 spotlight target changes from `[data-hype-header]` to `.artist-list`. Step 5 completion handled by parent route reacting to `hype-select` event.
- `frontend-onboarding-flow`: Guest follow default hype corrected from `'away'` to `'watch'`.

## Impact

- **Frontend only** — no backend, proto, or infrastructure changes.
- Files affected:
  - `src/components/hype-inline-slider/hype-inline-slider.ts` — remove `selectHype`, `isAuthenticated`, `isOnboarding`; add `onSelect`
  - `src/components/hype-inline-slider/hype-inline-slider.html` — replace `click.trigger`
  - `src/components/hype-inline-slider/hype-inline-slider.css` — track centering fix
  - `src/routes/my-artists/my-artists-route.ts` — replace `onHypeChanged` + `onHypeSignupPrompt` with `onHypeSelect`; spotlight target
  - `src/routes/my-artists/my-artists-route.html` — replace event bindings; remove `is-authenticated`/`is-onboarding`
  - `src/services/follow-service-client.ts` — default hype value
  - `test/routes/my-artists-route.spec.ts` — updated for new event flow
