## 1. Spikes that can change the design (frontend)

- [ ] 1.1 Reproduce the removed date-group stagger (`event-card.css:29-36`) in a `concert-highway` story and check whether the `sibling-index()` count across already-built groups explains "every row moved together" (design D6); record the cause in design.md, and verify the deal-in (D4) does not share it by running the story with a grown window
- [ ] 1.2 Wrap one bottom-nav tab switch in `document.startViewTransition(async () => { await router.load(path); runTasks() })` and confirm in Chromium that the transition finishes (no `TimeoutError` on `transition.finished`) for Home ↔ Discovery ↔ My Artists; record the result in design.md D5, and if it times out, drop group 5's tab task and revise the app-shell delta ("Tab switches cross-fade") before continuing

## 2. Scroll motion owned by CSS (components/infrastructure/fan/web/route/dashboard)

- [ ] 2.1 Pass `behavior: 'instant'` to the `scrollIntoView()` in the `scrollAnchor` setter, and give `.concert-scroll` `scroll-behavior: smooth` with `auto` under reduced motion; verify the existing re-entry and upward-growth tests ("Scrolling up from a restored date reaches earlier dates without a jump") still pass

## 3. Month jump (components/infrastructure/fan/web/route/dashboard)

- [ ] 3.1 Add `skip-up` and `skip-down` to `svg-icon` in the 24 px, 2 px-stroke style, with a story case each; verify the `svg-icon` story renders both
- [ ] 3.2 Implement `jumpToMonth(step)` on `<concert-highway>` with `openWindow()` and the pause of edge growth until `scrollend` (600 ms fallback) (design D1); verify unit tests for "A month jump builds only around the target month" (at most 24 groups built after a 40-date jump) and for no growth during the jump, and that both jumps end with a scroll in their own direction (downward for next month, upward for previous month)
- [ ] 3.3 Add the capsule (sticky, centred above the FAB, menu-surface and shadow-soft), the `data-has-prev` / `data-has-next` attributes updated on `scrollend`, the `scroll-state(scrollable: top)` query, the `:root:has(.fab-panel:popover-open)` rule, and the `dashboard.monthJump.prev/next` keys in both locale files (design D2); verify a `concert-highway` story per state (both, previous only, next only, before scrolling) and unit tests for "Next month from the middle of November", "Previous month", "No month in that direction", "Named for assistive technology"
- [ ] 3.4 Verify "Not shown before the fan scrolls", "Hidden while the FAB is open" and "Reduced motion" in a Playwright test on a local build of `/dashboard` with a stubbed concert list spanning three months, including that `history.length` does not change after a jump

## 4. Deal-in of date rows (components/infrastructure/fan/web/global/live-highway)

- [ ] 4.1 Add the row trigger, the lane animation with the `sibling-index()` delay, the scroll-driven fallback under `@supports not (timeline-trigger: …)` and `animation: none` under reduced motion (design D4); replace the "No entrance animation" note in `event-card.css`; verify a `reduced-motion`-tagged `concert-highway` story asserts the lane animations' delays (0, 110, 220 ms) and duration (760 ms) through `getAnimations()`, and none under reduced motion
- [ ] 4.2 Verify "Scrolling down", "Scrolling up after a month jump", "Fast scroll" and "A row comes back" in a Playwright test on a local build of `/dashboard`: after a 1500 px programmatic scroll and after an upward scroll, a row in view has running lane animations with currentTime below 760 ms; record a performance trace of a fling on the reference profile (4× CPU) and drop the `filter` from the keyframes if a frame exceeds 16 ms

## 5. View Transitions (components/infrastructure/fan/web/global/app-shell)

- [ ] 5.1 Add the reduced-motion rule for all View Transition pseudo-elements to `global.css`; remove the feature checks in `my-artists-route.ts` and `discovery-route.ts` and the `matchMedia` check in Discovery; add a jsdom stub for `startViewTransition` to `test/setup.ts`; verify the existing my-artists unfollow and discovery swap tests pass
- [ ] 5.2 Run tab switches in a View Transition with `view-transition-name` on the page header and the navigation bar (design D5); verify "Tab switch", "Reduced motion preference" and "Route change from inside a page" in a Playwright test on a local build (the transition's `ready` fires on a tab tap and not on opening an event page; under emulated reduced motion no `::view-transition` animation runs)

## 6. Dialogs and disclosures (components/infrastructure/fan/web/global/ui-primitives)

- [ ] 6.1 Add the fade in/out with `allow-discrete` to the confirm dialog and the `::details-content` height transition to the licenses `<details>` (design D9); verify "Confirmation dialog closes" and "Reduced motion" in the `confirm-dialog` stories (a `reduced-motion`-tagged story asserting the computed transition), and "License text opens" by a Playwright check on a local build of `/legal/licenses` that the section's height changes over the transition

## 7. Japanese text and fonts (components/infrastructure/fan/web/global/design-tokens)

- [ ] 7.1 After `adopt-m3-cube-ui-foundation` has renamed the tokens, add the `Local Noto Sans JP` alias and put it first in `--md-ref-typeface-plain` (design D7); verify "Windows with Noto Sans JP installed" and "iPhone" by a Playwright check that no `fonts.gstatic.com` request is made when the alias resolves (Chromium with a local Noto installed in the test container) and one is made in WebKit, and "Android" on the owner's Android device in production after release
- [ ] 7.2 Add `palt`, `text-autospace`, `line-break: strict`, `word-break: auto-phrase`, heading `text-wrap: balance` and the `text-box` trim on buttons and chips to `global.css` (design D8); verify "Mixed Japanese and Latin text", "A phrase is not split", "Small kana at the start of a line" and "Button label" in a `Foundations/Typography` story, and review the 320 px stories and the visual baselines for wide line-end gaps and raised Japanese labels, regenerating baselines that changed on purpose

## 8. Release check

- [ ] 8.1 After the frontend release, on the owner's Android device in production: jump between months, scroll up and down through dealt-in rows, switch tabs, and confirm no Noto Sans JP download in Chrome's network panel
