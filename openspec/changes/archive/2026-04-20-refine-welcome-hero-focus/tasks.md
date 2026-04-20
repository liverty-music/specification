## 1. Template Restructure

- [x] 1.1 Replace the always-visible `[Get Started]` / `[Log In]` buttons inside `.welcome-hero` in `frontend/src/routes/welcome/welcome-route.html` with a conditional composition: when `dateGroups.length > 0` render the scroll-affordance button, otherwise render an inline fallback CTA group so unauthenticated users always have a way forward
- [x] 1.2 Remove the `.welcome-scroll-hint` `<div>` element from `.welcome-hero` in `frontend/src/routes/welcome/welcome-route.html`
- [x] 1.3 Add a new `<button class="welcome-scroll-cta" click.trigger="scrollToPreview()" t="welcome.hero.seePreview"></button>` element inside `.welcome-hero`, placed after the language switcher
- [x] 1.4 Ensure Screen 2 (`.welcome-screen-2`) retains its existing `[Get Started]` / `[Log In]` CTA group without changes
- [x] 1.5 Verify language switcher (`.welcome-lang`) remains on Screen 1 between the hero subtitle and the new scroll-CTA button

## 2. ViewModel & Handler

- [x] 2.1 Add a `scrollToPreview()` method to `WelcomeRoute` in `frontend/src/routes/welcome/welcome-route.ts` that scrolls to the `.welcome-screen-2` element
- [x] 2.2 Implement smooth-scroll behavior by default using `element.scrollIntoView({ behavior: 'smooth', block: 'start' })`
- [x] 2.3 Detect `window.matchMedia('(prefers-reduced-motion: reduce)')` and fall back to `{ behavior: 'auto' }` when set
- [x] 2.4 Guard against missing `.welcome-screen-2` element (e.g., when `dateGroups.length === 0`) by making `scrollToPreview()` a no-op in that case
- [x] 2.5 Add logger debug entry when the scroll-affordance is activated (scope: `WelcomeRoute`)
- [x] 2.6 Remove the `this.guest.clearAll()` call from `handleGetStarted()` so guest follows are preserved when entering onboarding. The existing `landing-page` spec already requires this (scenario: "Get Started initiates onboarding without clearing guest data"); the code had been diverging. `handleLogin()` retains its `clearAll()` call — that path has a different rationale documented inline.

## 3. CSS Layout

- [x] 3.1 In `frontend/src/routes/welcome/welcome-route.css`, relax `scroll-snap-type` on the scope root from `y mandatory` to `y proximity`
- [x] 3.2 Change `.welcome-hero` `block-size` from `100svh` to approximately `95svh` (the peek target) so Screen 2's top edge is faintly visible above the fold
- [x] 3.3 Remove the `.welcome-scroll-hint` rule block and the `@keyframes bounce-down` keyframes — both become dead code
- [x] 3.4 Remove `.welcome-scroll-hint` reference from the `@media (prefers-reduced-motion: reduce)` block
- [x] 3.5 Add a `.welcome-scroll-cta` rule: min 44×44px tap target, clear visible label styling, focus-visible outline, optional downward arrow decoration
- [x] 3.6 Verify the scroll container's `scroll-behavior: smooth` interacts correctly with the new proximity snap — snap points should be at the top of `.welcome-hero` and `.welcome-screen-2`

## 4. i18n Translation Keys

- [x] 4.1 Add `welcome.hero.seePreview` key to the English locale resources with a value like "See how it works ↓"
- [x] 4.2 Add `welcome.hero.seePreview` key to the Japanese locale resources with an appropriate Japanese label (e.g., "使い方を見る ↓" or equivalent confirmed by localization review)

## 5. Unit Tests

- [~] 5.1 Deferred to E2E per codebase convention (route components rely on E2E for DOM assertions — see `app-shell.spec.ts:52` for precedent). Covered by task 6.2.
- [~] 5.2 Deferred to E2E per codebase convention. Covered by task 6.2.
- [x] 5.3 Add a unit test asserting `scrollToPreview()` calls `scrollIntoView` on the Screen 2 element with `behavior: 'smooth'` when `prefers-reduced-motion` is not set
- [x] 5.4 Add a unit test asserting `scrollToPreview()` uses `behavior: 'auto'` when `matchMedia('(prefers-reduced-motion: reduce)').matches` is true
- [x] 5.5 Add a unit test asserting `scrollToPreview()` is a no-op when `dateGroups` is empty (preview section is not rendered)
- [~] 5.6 Deferred to E2E per codebase convention. Covered by task 6.1 (existing E2E assertions updated for Screen 2).
- [x] 5.7 Update `handleGetStarted` unit test to assert `guest.clearAll` is NOT called, aligning with the landing-page spec scenario "Get Started initiates onboarding without clearing guest data"

## 6. E2E Tests

- [x] 6.1 Update `frontend/e2e/functional/onboarding-flow.spec.ts` (or the equivalent welcome-page E2E) to reflect the new layout — `[Get Started]` is now found on Screen 2 only (with inline fallback on Screen 1 when preview is absent)
- [x] 6.2 Add an E2E scenario: visit `/`, confirm no `[Get Started]` / `[Log In]` above the fold, tap `[See how it works ↓]`, assert viewport scrolls to Screen 2, assert `[Get Started]` is now visible
- [x] 6.3 Add an E2E scenario for the peek: visit `/`, confirm the top portion of the concert preview (or its label) is visible within the initial viewport without any scrolling

## 7. Storybook

- [x] 7.1 Update `frontend/src/routes/welcome/welcome-route.stories.ts` so the default story reflects the new Screen 1 composition (documented — without RPC mocks the story renders the empty-preview fallback, see docblock)
- [x] 7.2 Verify the empty-preview story (when `dateGroups.length === 0`) still renders correctly — scroll-CTA button hidden, inline CTAs on Screen 1 (confirmed by template + CSS — story renders fallback path by default)

## 8. QA & Release

- [~] 8.1 Visual QA on iOS Safari — MANUAL: not executable in CI/WSL2 env. Reviewer should load `/` on a physical iPhone and confirm the Screen 2 peek is visible above the fold both when the address bar is expanded and when it collapses on scroll.
- [~] 8.2 Visual QA on Android Chrome — MANUAL: same check as 8.1 on Android. Confirm peek stability through dynamic toolbar resizing.
- [~] 8.3 Visual QA on desktop Chrome and Firefox — MANUAL: with a trackpad (two-finger scroll) and a mouse wheel, scroll partway between Screen 1 and Screen 2 and confirm proximity snap does not jerk back to Screen 1 mid-read.
- [~] 8.4 Keyboard-only QA — MANUAL: with keyboard only, Tab should reach `[See how it works ↓]` on Screen 1, Enter/Space should trigger scroll to Screen 2, focus ring should remain visible throughout, and Tab from there should reach `[Get Started]` → `[Log In]`.
- [~] 8.5 Screen reader QA — MANUAL: with VoiceOver (iOS/macOS) or NVDA/TalkBack (Windows/Android), confirm the button is announced as "See how it works, button" in EN and "使い方を見る, ボタン" (approx) in JA.
- [x] 8.6 Verify `prefers-reduced-motion: reduce` disables smooth scroll on activation — unit-tested (see task 5.4: `scrollToPreview` uses `behavior: 'auto'` under reduced motion).
- [x] 8.7 Run `make check` in `frontend/` — lint, typecheck, unit tests, stylelint all pass (97 files, 1008 tests passed; `welcome-route.spec.ts` 10 tests passed; biome/stylelint clean).
- [x] 8.8 Confirm Storybook builds without errors
