## Context

The onboarding flow progresses through discovery → dashboard → my-artists → completed. Upon reaching the dashboard, a lane intro sequence (introducing HOME / NEAR / AWAY stages) begins, followed by a celebration overlay on completion.

The following issues exist:

1. **i18n key resolution bug**: `dashboard-route.ts` generates i18n keys from ISO 3166-2 codes (e.g., `JP-40`) using `replace('jp-', '')`, producing numeric key `40`. The correct `translationKey()` helper in `entities/user.ts` returns the proper key (e.g., `fukuoka`) but is not being used
2. **Tap area restriction**: The coach-mark's `onBlockerClick()` is a no-op, so taps outside the spotlight target are ignored
3. **Celebration understatement**: `font-size: var(--step-2)` and `font-weight: normal` are too subtle for a completion moment
4. **Dashboard layout breakage**: `dashboard-route.css` is missing `grid-template-areas`. All other routes (settings, tickets, my-artists, discovery) define `"header" "content"`, allowing page-header's `grid-area: header` to resolve correctly. Dashboard alone lacks this, causing the page-header to shrink to content width (112px)
5. **Immediate home selector display**: `attached()` directly calls `homeSelector.open()` when `needsRegion && isOnboardingStepDashboard`, bypassing the lane intro context

## Goals / Non-Goals

**Goals:**

- Fix all 5 bugs/UX issues so the onboarding flow works as intended
- Preserve existing onboarding state management (OnboardingService, localStorage persistence)
- Keep all changes within the frontend repository

**Non-Goals:**

- Adding new onboarding steps or changing state transitions
- Major refactoring of the coach-mark component
- Overhauling the celebration animation/particle engine
- Responsive layout for the concert-highway 3-column grid (separate issue)

## Decisions

### D1: i18n key resolution — Use `translationKey()` helper

Replace `code.toLowerCase().replace('jp-', '')` with `translationKey(code)` at 2 locations in `dashboard-route.ts` (L200-202 and L248-252).

**Rationale**: The `translationKey()` function already exists in `entities/user.ts` and returns the correct key from `JP_PREFECTURES` (e.g., `JP-40` → `fukuoka`). The `user-home-selector` component uses the same function, ensuring consistency.

**Alternative considered**: Directly accessing `JP_PREFECTURES[code].ja` for the Japanese name, but going through the i18n framework preserves locale support.

### D2: Tap area — Call `onTap()` from `onBlockerClick()`

Modify the coach-mark's `onBlockerClick()` to call `this.onTap?.()`. All 4 mask elements (top, right, bottom, left) and the target-interceptor become tap-to-advance targets.

**Rationale**: The lane intro uses a "tap to continue" pattern. Limiting taps to the spotlight target creates confusion about what to tap. Making the entire screen tappable minimizes interaction friction.

**Consideration**: The coach-mark may be reused outside onboarding. When `onTap` is not set, the behavior remains a no-op, so existing behavior is preserved.

### D3: Celebration visuals — Increase text size and glow

CSS changes to enhance visual impact:
- `font-size`: `var(--step-2)` → `var(--step-4)` (approximately 2x larger)
- `font-weight`: `normal` → `bold`
- `text-shadow`: Increase glow radius and alpha values
- Add styling for the sub-text (currently unstyled)

**Rationale**: The celebration is the only feedback for onboarding completion. The confetti animation exists but the text itself is too understated to convey accomplishment.

### D4: Dashboard layout — Add `grid-template-areas`

Add to `dashboard-route.css` `:scope` the same pattern used by all other routes:

```css
grid-template-areas:
    "header"
    "content";
```

Change content element placement from `grid-row: 2` to `grid-area: content`.

**Rationale**: The page-header component declares `grid-area: header`, expecting the parent grid to define a `"header"` area. All routes (settings, tickets, my-artists, discovery) follow this pattern. Dashboard was the only one missing it.

### D5: Home selector timing — Always start via lane intro

Change the `attached()` conditional logic:

**Before**:
```
needsRegion && isOnboardingStepDashboard → homeSelector.open() directly
!needsRegion && isOnboardingStepDashboard → startLaneIntro()
```

**After**:
```
isOnboardingStepDashboard → startLaneIntro() (always)
startLaneIntro() handles needsRegion internally via waiting-for-home phase
```

`startLaneIntro()` already contains logic to open the home selector in a `waiting-for-home` sub-state (L236-244). The direct `homeSelector.open()` call in `attached()` was redundant and caused the selector to appear without the lane intro context (stage spotlight).

## Risks / Trade-offs

- **Coach-mark tap behavior change** → If coach-mark is reused outside onboarding, "tap anywhere to advance" may not be desirable. However, since `onTap` defaults to undefined (no-op), the behavior only activates when a tap handler is explicitly provided. No issue at present
- **Celebration text size increase** → Risk of overflow with longer text. The current text is short enough, but future localizations should be tested
- **Home selector timing change** → `startLaneIntro()` awaits data loading via `while (this.isLoading)`. This may introduce a slight delay before the home selector appears, but since the stage intro requires loaded data anyway, this is acceptable
