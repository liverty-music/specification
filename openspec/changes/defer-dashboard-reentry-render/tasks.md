## 1. Baseline

- [ ] 1.1 Record a reference-profile (Pixel 8 / 4× CPU) Performance trace with screenshots of BOTH a cold dashboard load and a signed-in tab-switch re-entry with a populated timetable. Capture INP, the re-entry render block, and confirm today's single-paint behavior (no frame-only paint ahead of the timetable render). This is the before-baseline.
- [ ] 1.2 Measure the real median date-group height on the reference dataset — it sets the `contain-intrinsic-size` fallback in 2.2. The spike used 180px against a 159.2px natural height and produced 416px of scroll-height drift over 30 groups; do not carry that number over.

## 2. Structure — flatten, then scope to the viewport

- [ ] 2.1 In `concert-highway.css`, flatten the subgrid chain: the date-group `<li>` declares its own `grid-template-columns` (matching the root's equal-fraction columns) instead of `subgrid`, so it stops being a subgrid participant of `.concert-scroll`. `.lane-grid` may keep `subgrid` because that chain is then internal to the group. There is no grid column-gap to keep in sync (the only `gap` is the month separator's flex gap). Verified in Spike 2: lane offsets stayed within 0.02px of the subgrid baseline.
- [ ] 2.2 Apply `content-visibility: auto` + `contain-intrinsic-size: auto <fallback from 1.2>` to the flattened date group. This is P2 re-applied on a structure that can carry it — do NOT apply it while the subgrid chain still crosses the group boundary (Spike 2 V1 reproduced the prod failure: lanes collapse to full width and stack).
- [ ] 2.3 Rewrite the Storybook regression guard in `concert-highway.stories.ts`. It currently asserts there is NO `content-visibility` and that the `<li>` keeps its subgrid — it encodes the P2 revert and now asserts the opposite of the intended state. Replace it with a guard on the new contract: lanes align with the stage header, in both three-lane and `hideAway` two-lane modes. Do not delete it silently.
- [ ] 2.4 Add a component test asserting lane/stage-header column geometry numerically (not visually) at both three-lane and `hideAway` widths, with variable card counts per lane.

## 3. App Shell frame

- [ ] 3.1 Ungate the stage header and lane columns so they render without data. Withhold them only for a settled-empty result — not for `dateGroups.length === 0`, which cannot distinguish "not yet assigned" from "genuinely zero".
- [ ] 3.2 Replace the generic six-bar `state-placeholder` on the dashboard with a timetable-shaped skeleton (lane columns + a few date rows) so the swap to real content is layout-shift-free. Add named Storybook stories for the new visual states (frame-without-data, timetable skeleton) per the repo's story contract, and regenerate the committed visual baselines inside the pinned Playwright container.
- [ ] 3.3 Gate BOTH empty-state placeholders — the guest one and the "no concerts" one — on a settled condition. Do NOT overload `isLoading`: it also guards `refreshInBackground()`, so a separate settled flag is required or the background refresh stops firing on re-entry.

## 4. Lifecycle — place each concern where it belongs

- [ ] 4.1 Keep `loading()` to its synchronous prelude plus `void this.loadData()` (params/query/filter restore, fetch kickoff). Per the capability this is navigation-scoped, earliest, and blocks nothing — it is correct and stays.
- [ ] 4.2 Move reflection of render state — including the cache fast path's `dateGroups` assignment and its `timetableLoaded` flip — out of `loading()` and into the component lifecycle (`attached()`), so the component's first render contains only the frame and skeleton. Spike 1: this relocation ALONE produced zero frame-only paints, so it is necessary but not sufficient on its own.
- [ ] 4.3 Do NOT add a scheduling primitive. `attaching()` returns nothing; there is no `queueAsyncTask`, `setTimeout(0)` or `scheduler.yield()` anywhere in this change. Spike 1 measured the render block at 44.2 ms for one windowed viewport vs 177.7 ms unwindowed (4x CPU), so containment — not scheduling — is what makes the paint fast. If a future measurement ever shows a yield is needed, use `scheduler.yield()`, not `setTimeout(0)`.
- [ ] 4.4 Re-entry restores in a single bounded paint with reveal motion suppressed. Do not try to produce a frame-only paint on the cached path: it would cost a frame and flash an empty frame over content the fan has already seen.
- [ ] 4.5 Guard the deferred reflection so it never overwrites a fresher background-refresh result that already landed, and cancel it on teardown / a new load so a stale paint never writes into a torn-down or re-navigated route (mirror the existing `abortController` discipline).

## 4b. Reveal motion (CSS only, no JS beyond a guarded fallback)

- [ ] 4b.1 Replace `event-card.css`'s current `animation: fade-slide-up 400ms ease-out both` — which fires on every card simultaneously — with reveal motion on the **date group**, so one keyframe set serves both triggers and the motion unit matches the scroll-reveal unit.
- [ ] 4b.2 First-load reveal: stagger via `animation-delay: calc(sibling-index() * <step>)`, capped (e.g. `min(..., 400ms)`) so groups just below the fold do not sit on a long delay. `sibling-index()` is Baseline newly available (2026-08-18; Chrome 138, Firefox 154, Safari 26.2), which is newer than the repo's stated 2024-2025 Baseline target, so precede it with a `calc(var(--sibling-index) * <step>)` declaration and set that property from a short script guarded by `CSS.supports('animation-delay: calc(sibling-index() * 0.1s)')`.
- [ ] 4b.3 Scroll reveal: `animation-timeline: view()` with `animation-range: entry`, inside `@supports ((animation-timeline: view()) and (animation-range: entry))` — the `animation-range` term is required to exclude partial implementations. Declare `animation-timeline` AFTER the `animation` shorthand or the shorthand resets it. Scroll-driven animations are limited availability (Chrome 115, Safari 26, not Firefox); the reveal is decorative, so this is progressive enhancement with no fallback. Do NOT add `scroll-timeline-polyfill` — the guidance explicitly rules it out.
- [ ] 4b.4 Animate only compositor-friendly properties (`transform`, `opacity`). Add `@media (prefers-reduced-motion: reduce)` disabling the reveal entirely; nothing else may depend on the animation, so suppression must change motion only, never what is shown or when.
- [ ] 4b.5 No gating is needed between the two triggers. Spike 3 measured that `content-visibility: auto` does NOT defer animations in skipped subtrees, so the time-based stagger consumes itself off screen and has always finished before a group is scrolled into view. Add a regression test asserting this stays true, since the whole no-gating design rests on it.
- [ ] 4b.6 Add Storybook stories for the reveal states and confirm `.skeleton`-style animated elements are still not screenshotted (the repo forbids `toMatchScreenshot` on animated elements — assert DOM/a11y instead).

## 5. Scroll position

- [ ] 5.1 Save the timetable scroll offset in `unloading()` — the route lifecycle's documented "save state" hook, and navigation-scoped, which matches a per-route scroll memory. Persist it alongside the cached groups in `ConcertStore` so it survives the route instance being re-created on every navigation.
- [ ] 5.2 Restore in `attached()`, sequenced AFTER the cached groups are reflected — restoring against a not-yet-rendered list lands nowhere. Clamp to the restored content's `scrollHeight` rather than throwing when the content is shorter.

## 6. Cross-route — non-blocking contract

- [ ] 6.1 Fix `settings-route.ts`: `loading()` currently awaits `resolveNotificationToggleState()` and `loadVerificationStatus()` (an RPC), holding the outgoing screen until the network resolves. Start them non-blocking, mirroring `my-artists-route.ts`'s documented pattern.
- [ ] 6.2 Record `lottery-apply`'s `await` inside `loading()` as a deliberate, documented exception at the call site — it parks an unverified fan on `verify-required` before any card hold, where showing the payment step first would be wrong.
- [ ] 6.3 Add a `scripts/verify-route-loading.ts` check (the repo's existing `scripts` vitest project idiom, cf. `verify-build-templates`) that fails on an `await` of network/RPC work directly inside a route's `loading()`, and on synchronous assignment to render-bound state there. Allowlist the documented exceptions from 6.2 and `AuthHook`'s deliberate auth barrier. This is what would have caught 6.1.

## 7. Tests & verification

- [ ] 7.1 Unit-test (`dashboard-route.spec.ts`) that on the cache fast path neither empty state renders before the load settles, the background refresh still fires, `timetableLoaded` still flips (celebration/latch + deep-link intact), and a background refresh that settles BEFORE the deferred reflection is not clobbered by the stale cache. Remove the stale `queueTask` mock — the implementation no longer uses the task queue.
- [ ] 7.2 `make lint` + `make test` in `frontend/`, plus `npm run test-storybook` for the rewritten guard and new stories.
- [ ] 7.3 `npm run build && npm run verify:build-templates` locally — the dashboard template changes here and a moved marker breaks the production image build, not CI. Update `ROUTE_MARKERS` if needed.
- [ ] 7.4 Device verification on the reference profile per design.md → Verification: cold load paints the frame while the fetch is in flight and the visible groups reveal top-to-bottom; re-entry restores in a single bounded paint with no reveal motion, at the previous scroll position, INP substantially below the 1.1 baseline; scrolling reveals later dates (animated where supported) without a scrollbar jump; reduced-motion shows the same content with no motion; background refresh, celebration and deep-link all intact; Settings swaps immediately.

## 8. Close-out

- [ ] 8.1 Sync both deltas into the main specs (`openspec sync`) before archiving. `dashboard-timetable-rendering` does not yet exist under `openspec/specs/` — it is created by the sibling `optimize-dashboard-render-cost` change, so that change must sync first or the two deltas must be reconciled at sync time.
- [ ] 8.2 Record before/after INP for both cold load and re-entry, plus the frame-paints-first evidence, in the PR description.
- [ ] 8.3 Hand off to `progressive-route-rendering`: that change generalises this one's mechanism (`attached()` reflection, `unloading()` scroll save, and the CSS reveal model) into shared router hooks and rolls the App Shell treatment out to Tickets / Order / Discovery. Its design and tasks were deliberately left unwritten until this implementation lands, so record here what the final shape actually was — what the scroll-save/restore sequencing needed, what the skeleton's structure is, and whether the reveal model transferred to non-timetable lists — so the abstraction is extracted from working code rather than re-designed.
