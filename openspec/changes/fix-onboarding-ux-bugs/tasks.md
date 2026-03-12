## 1. AuthHook Fix — Onboarding-Aware Fallback

- [x] 1.1 Add Priority 2.5 branch in `auth-hook.ts`: when `tutorialStep` is undefined AND `isOnboarding` is true, redirect to current step's route without toast
- [x] 1.2 Add unit test: onboarding user navigating to route without `tutorialStep` (e.g., Tickets) SHALL redirect silently (no toast published to EventAggregator)
- [x] 1.3 Add unit test: onboarding user navigating to route with `tutorialStep` > `currentStep` SHALL redirect to current step's route
- [x] 1.4 Add unit test: non-onboarding unauthenticated user navigating to protected route SHALL still show "Login required" toast

## 2. Coach Mark Spotlight — CSS Anchor Positioning Hybrid + Continuous Persistence

- [x] 2.1 Add inline SVG-free markup to `coach-mark.html`: replace `.coach-mark-spotlight` div with `.visual-spotlight` element + 4 `.click-blocker` divs (top/right/bottom/left)
- [x] 2.2 Rewrite `coach-mark.css`: remove overlay `background`, add `.visual-spotlight` with `anchor()` inset + `box-shadow: 0 0 0 100vmax` + `border-radius: var(--spotlight-radius)`, add `.click-blocker` styles with transparent bg + `pointer-events: auto` + `anchor()` positioning
- [x] 2.3 Add popover UA style reset to `.coach-mark-overlay`: `background: transparent; border: none; padding: 0; margin: 0;` and `::backdrop { display: none; }`
- [x] 2.4 Simplify `coach-mark.ts`: remove `updateSpotlightPosition()` method and `getBoundingClientRect()` calls. Keep `findAndHighlight()` for anchor-name assignment and retry logic. Remove `spotlightEl` ref (no longer needed).
- [x] 2.5 Add `--spotlight-radius` CSS custom property support: set on the spotlight element based on a new `@bindable spotlightRadius` property (default: `'12px'`)
- [x] 2.6 Update `onOverlayClick()`: since click-blockers handle blocking and clicks pass through natively to the target, simplify to only call `onTap()` callback (remove coordinate calculation logic)
- [x] 2.7 Add `view-transition-name: spotlight` to `.visual-spotlight` in CSS, add `::view-transition-group(spotlight)` animation rule (400ms ease-out)
- [x] 2.8 Wrap anchor-name reassignment in `highlight()` with `document.startViewTransition()` for smooth spotlight slide on target change (same-page and cross-route)
- [x] 2.9 Add `prefers-reduced-motion` media query to suppress View Transition animation
- [x] 2.10 Move `<coach-mark>` from individual route templates (discover-page.html, dashboard.html, my-artists-page.html) to a single instance in `my-app.html`
- [x] 2.11 Add onboarding spotlight config to onboarding service: expose `spotlightTarget`, `spotlightMessage`, `spotlightRadius`, `spotlightActive` properties driven by `currentStep`
- [x] 2.12 Bind app-shell `<coach-mark>` to onboarding service properties: `target-selector.bind`, `message.bind`, `spotlight-radius.bind`, `active.bind`
- [x] 2.13 Remove per-page coach mark bindings and onTap handlers from discover-page.ts, dashboard.ts, my-artists-page.ts — delegate to onboarding service `onSpotlightTap()` callback
- [x] 2.14 Ensure popover stays open across route navigations: `highlight()` reassigns anchor-name without calling `hidePopover()`/`showPopover()` when already open
- [x] 2.15 Add `deactivate()` method: called at Step 6, calls `hidePopover()`, removes anchor-name, releases scroll lock
- [x] 2.16 Add inline SVG arrow to `coach-mark.html`: use `switch.bind` on `arrowDirection` to render up/down curved `<path>` elements with `stroke="currentColor"`
- [x] 2.17 Add arrow CSS: `stroke-dasharray`/`stroke-dashoffset` drawing animation (600ms), arrowhead fade-in (300ms delay), `prefers-reduced-motion` override
- [x] 2.18 Add `arrowDirection` computed property to `coach-mark.ts`: determine 'up' or 'down' based on tooltip's resolved position relative to target
- [x] 2.19 Add handwritten font: import `Klee One` from Google Fonts, apply `font-family: 'Klee One', cursive` to `.coach-tooltip-message` in `coach-mark.css`
- [x] 2.20 Add unit test: when coach mark is active, `.visual-spotlight` element exists with `box-shadow` style applied
- [x] 2.21 Add unit test: when coach mark is active, 4 `.click-blocker` elements exist with `pointer-events: auto`
- [x] 2.22 Add unit test: target element receives `anchor-name: --coach-target` when highlighted
- [x] 2.23 Add unit test: changing target via `highlight(newTarget)` does not call `hidePopover()` (popover stays open)
- [x] 2.24 Add unit test: `deactivate()` calls `hidePopover()` and cleans up anchor-name and scroll lock
- [x] 2.25 Add unit test: SVG arrow element exists in tooltip when coach mark is active
- [x] 2.26 Add unit test: tooltip message element uses handwritten font family (`Klee One`)

## 3. Toast Popover White Background Fix

- [x] 3.1 Add popover UA style reset to toast container in `toast-notification.html` or via CSS: `background: transparent; border: none; padding: 0; margin: 0;`
- [x] 3.2 Add visual regression test: toast popover container has transparent background when displayed

## 4. Progress Bar Removal

- [x] 4.1 Remove `.search-progress-bar` and `.search-progress-fill` elements from `discover-page.html`
- [x] 4.2 Remove `.search-progress-bar` and `.search-progress-fill` CSS rules from `discover-page.css`
- [x] 4.3 Remove `searchProgress` getter from `discover-page.ts` (keep `completedSearchCount` and `concertSearchStatus` — still needed for `showDashboardCoachMark`)
- [x] 4.4 Update existing discover-page tests: remove any assertions about progress bar, verify `showDashboardCoachMark` still works correctly

## 5. DNA Orb Color Injection + Swirl Animation

- [x] 5.1 Add `injectColor(hue: number)` method to `OrbRenderer`: replace 5-8 existing particles with new particles at the given hue, trigger swirl state
- [x] 5.2 Add swirl state to `OrbRenderer.update()`: track `swirlIntensity` (decays from 1.0 to 0 over ~1000ms), multiply particle rotation speed by `1 + swirlIntensity * 2` during swirl
- [x] 5.3 Add glow boost during swirl in `OrbRenderer.render()`: add `swirlIntensity * 0.4` to effective intensity
- [x] 5.4 Thread bubble hue through absorption: in `dna-orb-canvas.ts`, pass the absorbed bubble's hue from the absorption animator completion callback to `orbRenderer.injectColor(hue)`
- [x] 5.5 Add `prefers-reduced-motion` check: skip rotation speed boost when reduced motion is preferred
- [x] 5.6 Add unit test: `OrbRenderer.injectColor(142)` results in particles containing hue 142 while total count remains at `maxParticles`
- [x] 5.7 Add unit test: `swirlIntensity` starts at 1.0 after `injectColor()` and decays to 0 after sufficient `update()` calls
- [x] 5.8 Add unit test: multiple rapid `injectColor()` calls each inject their hue and restart swirl

## 6. Home Nav Step Advancement

- [x] 6.1 In `bottom-nav-bar.ts` or `discover-page.ts`: when onboarding user taps Home/Dashboard nav AND `showDashboardCoachMark` is true, advance step to DASHBOARD and navigate to `/dashboard`
- [x] 6.2 Set `--spotlight-radius: 50%` for the Dashboard nav icon coach mark target (circular icon)
- [x] 6.3 Add unit test: tapping Home nav during onboarding when coach mark is active advances `onboardingStep` to 3 and triggers navigation to `/dashboard`
- [x] 6.4 Add unit test: tapping Home nav during onboarding when coach mark is NOT active (fewer than 3 follows) does NOT advance step

## 7. Integration Verification

- [ ] 7.1 Manual E2E test: full onboarding flow verifying continuous spotlight from Step 1 through Step 6
    - Step 0→1: Tap [Get Started] → navigate to Discover (no spotlight yet)
    - Step 1: Follow 3 artists → verify orb color changes on each absorption → spotlight activates on Home icon (`--spotlight-radius: 50%`) → tooltip "タイムテーブルを見てみよう！" in handwritten font → tap Home icon → **spotlight slides** to Dashboard
    - Step 3 (lane intro): Spotlight slides HOME STAGE → NEAR STAGE → AWAY STAGE → first concert card (verify smooth View Transition animation between each) → tooltip "タップして詳細を見てみよう！" → tap card → detail sheet opens → **spotlight slides** to My Artists tab
    - Step 4: Verify spotlight already on [My Artists] tab (no blink) → detail sheet not dismissible → tooltip "アーティスト一覧も見てみよう！" → tap My Artists → **spotlight slides** to Passion Level toggle
    - Step 5: Verify spotlight already on Passion Level toggle (no blink) → tooltip "好きなレベルを設定してみよう！" → change passion level → explanation popup after 800ms
    - Step 6: Spotlight fades out → sign-up modal appears (non-dismissible) → verify cleanup: no `anchor-name` on any element, no scroll lock on `au-viewport`, no orphaned click-blockers, popover hidden
    - **Key verification**: The popover was opened ONCE at Step 1 and never closed until Step 6
- [ ] 7.2 Manual test: during onboarding, tap Tickets/Settings nav items → verify silent redirect, no toast
- [ ] 7.3 Manual test: verify toast notifications display without white corner gap
- [x] 7.4 Run `make check` in frontend repo — all lint and tests pass
