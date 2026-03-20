## Context

Onboarding Step 5 (My Artists) is the final interactive step before completing onboarding. The user is a guest (unauthenticated) who has followed artists during discovery. The page displays those artists with hype sliders. The intended flow: spotlight highlights the slider area → user taps a hype dot → onboarding completes → redirect to welcome.

Currently, `HypeInlineSlider.selectHype()` contains business logic (auth gate, event branching) that belongs in the parent route. Since the user is a guest, `hype-signup-prompt` fires instead of `hype-changed`, and the onboarding completion handler never executes. This is a progression-blocking bug caused by a responsibility violation — a UI component should not own authentication or onboarding logic.

## Goals / Non-Goals

**Goals:**
- Refactor `HypeInlineSlider` into a pure presentation component (zero methods, zero event dispatch)
- Move all business logic (auth check, onboarding completion, signup prompt, RPC calls) to the parent route
- Correct the spotlight target to cover the interactive area (artist list with sliders)
- Fix visual regressions: slider track alignment, default hype value

**Non-Goals:**
- Persisting the signup-prompt-banner state across navigation (becomes irrelevant once onboarding completes correctly)
- Changing the hype-notification-dialog or signup flow for non-onboarding guests

## Decisions

### 1. Pure Presentation Slider with twoWay Binding

Remove all methods (`selectHype`), all business-logic bindables (`isAuthenticated`, `isOnboarding`), and all custom event dispatch (`INode` dependency) from the slider. The slider becomes data-only: three bindables (`artistId`, `hypeColor`, `hype`) and a static `stops` array.

The `hype` bindable uses `BindingMode.twoWay`. When the user clicks a radio, Aurelia's `checked.bind` updates `hype`, which pushes to the parent's `artist.hype` via two-way binding. The native `change` event bubbles through the light DOM to the parent.

The parent handles the `change` event with all business logic. If the selection is rejected (unauthenticated, onboarding), the parent reverts `artist.hype = prev`, which pushes back via two-way binding. Programmatic changes do not trigger `change` events (native DOM behavior), so no infinite loop.

**Alternative considered**: Controlled component with `preventDefault()` + `hype-select` CustomEvent. Rejected as unnecessarily complex — requires a method and event dispatch in the slider when Aurelia's binding + native DOM events achieve the same result with zero component code.

**Alternative considered**: `isOnboarding` bypass flag. Rejected because the slider still owns business logic and violates single responsibility.

### 2. Parent Route Handles All Business Logic via `change` Event

`MyArtistsRoute.onHypeInput()` receives the native `change` event and branches using a `prevHypes` Map to track previous values:

| Condition | Action |
|-----------|--------|
| `isOnboardingStepMyArtists` | Revert hype → deactivate spotlight → `setStep(COMPLETED)` → navigate to LP |
| `!isAuthenticated` | Revert hype → show notification dialog (signup prompt) |
| `isAuthenticated` | Accept → update `prevHypes` → `SetHype` RPC with retry |

### 3. Spotlight target: `[data-artist-rows]` instead of `[data-hype-header]`

The hype-legend header is a passive reference element. The interactive target is the artist list containing hype sliders. Using `[data-artist-rows]` makes the spotlight cutout cover the actual tap target area.

### 4. CSS logical properties for track centering

Use `inset-block-start: 50%; translate: 0 -50%` for vertical centering. The project enforces logical properties via stylelint (`csstools/use-logical`).

### 5. Default hype `'watch'` for guest follows

`'watch'` (observation level) is the lowest hype tier and the correct default for newly followed artists. `'away'` was a bug — it's the highest intensity tier.

## Risks / Trade-offs

- **[Risk] twoWay binding + revert pattern** → Reverts are safe because programmatic changes to radio checked state do not fire native `change` events. No infinite loop risk.
- **[Risk] `prevHypes` Map adds state tracking** → Minimal overhead. Initialized once in `loading()`, updated only on successful authenticated changes.
- **[Risk] Spotlight over `[data-artist-rows]` is a larger area** → The larger spotlight correctly matches the interactive region. Click-blockers and target-interceptor already handle arbitrary-sized targets.
