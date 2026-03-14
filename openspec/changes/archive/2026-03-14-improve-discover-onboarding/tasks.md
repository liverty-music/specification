## 1. Fix Discover Page Layout

- [x] 1.1 Add explicit `inline-size`, `block-size`, and `flex-shrink: 0` to `.search-icon` in `discover-page.css`
- [x] 1.2 Add explicit `inline-size`, `block-size`, and `flex-shrink: 0` to `.clear-button` and its child SVG in `discover-page.css`
- [x] 1.3 Change `grid-template-rows` from `auto auto auto 1fr` to `auto auto 1fr` in `.discover-layout`

## 2. Remove Onboarding HUD

- [x] 2.1 Remove `.onboarding-hud` and `.hud-message` markup from `discover-page.html`
- [x] 2.2 Remove `.onboarding-hud`, `.hud-message`, and `@keyframes hud-enter` styles from `discover-page.css`
- [x] 2.3 Remove `guidanceMessage` computed property and `guidanceHiding` state from `discover-page.ts`
- [x] 2.4 Remove unused i18n keys (`discovery.guidanceStart`, `discovery.guidanceRemaining`, `discovery.guidanceLast`, `discovery.guidanceReady`, `discovery.guidanceNoConcerts`) from locale files

## 3. Add Popover Onboarding Guide

- [x] 3.1 Add popover element with `popover="auto"` to `discover-page.html` (conditional on `isOnboarding`)
- [x] 3.2 Add popover CSS with `:popover-open`, `@starting-style`, and `transition-behavior: allow-discrete` to `discover-page.css`
- [x] 3.3 Add `prefers-reduced-motion` media query to disable popover transitions
- [x] 3.4 Call `showPopover()` in `discover-page.ts` `attached()` lifecycle hook when `isOnboarding` is true
- [x] 3.5 Add i18n key for popover guide message

## 4. Accumulating Orb Effects

- [x] 4.1 Add `baseIntensity` property and `setFollowCount(count)` method to `OrbRenderer` with easing curve `1 - 1 / (1 + count * 0.5)`
- [x] 4.2 Update `OrbRenderer.update()` to use `effectiveSwirl = baseIntensity + swirlIntensity` for particle speed multiplier
- [x] 4.3 Update `OrbRenderer.render()` to add `baseIntensity` to effective intensity for glow and visible particle count
- [x] 4.4 Increase `injectColor()` particle replacement count from 5-8 to 10-15
- [x] 4.5 Respect `prefers-reduced-motion` in `baseIntensity` — accumulate color richness but suppress swirl acceleration
- [x] 4.6 Wire `OrbRenderer.setFollowCount()` from `DnaOrbCanvas.followedCountChanged()` callback

## 5. Tests

- [x] 5.1 Update unit tests for `discover-page` to remove HUD-related assertions and add popover assertions
- [x] 5.2 Add unit tests for `OrbRenderer.baseIntensity` accumulation curve and `setFollowCount`
- [x] 5.3 Update E2E tests in `onboarding-flow.spec.ts` to verify popover appears and dismisses on discover page entry
- [x] 5.4 Update E2E layout tests in `discover.layout.spec.ts` to verify 3-row grid and search bar sizing
