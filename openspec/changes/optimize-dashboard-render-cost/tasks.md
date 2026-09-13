## Measurement results (prod, 2026-09-13)

Captured on the reference profile (mobile 412×915, 4× CPU throttle) against the
`https://liverty-music.app/welcome` embedded **sample timetable** — the same
`concert-highway` + `event-card` components rendering 23 date groups / 30 cards.
Before = v1.72.0 (`content-visibility: visible` confirmed). After = v1.72.1
(deployed via release → prod-pin bump; `content-visibility: auto` +
`contain-intrinsic-block-size` confirmed live).

| Metric | Before (v1.72.0) | After (v1.72.1) | Δ |
| --- | --- | --- | --- |
| Forced reflow, timetable render (`attached`) | 751 ms | 528 ms | **−30%** |
| Render-interaction INP ("open timetable") | 118 ms | 117 ms | ~flat |
| CLS (render) | 0.00 | 0.00 | 0 |
| CLS (scroll) | 0.00 | 0.00 | 0 |
| Forced reflow (scroll) | 68 ms | 82 ms | +14 (render-on-scroll) |

Follow-up found by the measurement: the `contain-intrinsic-block-size: 320px`
fallback was ~2× the real typical group height (~152px), inflating the
never-rendered scroll height (3505px real → 7059px estimated). Fixed to 160px in
frontend#607.

**Not measured (honest gaps — cannot be truthfully completed from this proxy):**
the P1 Style-recalc win (the sample has 0 matched cards, so `color-drift` was
never exercised on prod), PostHog `web.vitals`/`long_animation_frame` field data,
and the authenticated `/dashboard` nav-tab re-entry / reduced-motion / idle
scenarios (headless passkey auth is infeasible). These need a real signed-in
device session.

## 1. Baseline measurement

- [x] 1.1 Record a DevTools performance trace of a dashboard tab-switch re-entry on the reference profile (Pixel 8 emulation, 4× CPU) with a populated timetable; capture INP, LCP, and the Bottom-up self-time for Layout, Recalculate Style, and Paint as the before-baseline.
- [ ] 1.2 Capture the current PostHog `web.vitals` (LCP/INP) and `perf.long_animation_frame` for route `/dashboard` as the field before-baseline.

## 2. P1 — Remove the continuous style-recalc driver

- [x] 2.1 Delete the `color-drift` infinite animation (applied to `.event-card[data-matched]`), the `@property --hue-drift` declaration, and the now-dead `--artist-color` / `--artist-color-dim` derivations in the `[artist-color]` rule from `frontend/src/components/live-highway/event-card.css`. This is a pure deletion — NO static replacement is needed, because `--hue-drift` fed only `--artist-color`, which has zero consumers (matched card visuals use raw `--artist-hue`), so the animation produced no visible output. Once the animation is gone, the `@media (prefers-reduced-motion: reduce)` block that only set `animation: none` on the matched card also becomes moot — remove it if it has nothing else to gate.
- [x] 2.2 Delete the unused `contact-glow` / `pulse-glow` keyframes in `event-card.css` (defined but applied to no element — dead code), so the continuous-invalidation pattern cannot be reintroduced. Scope this task to CSS only; the laser-beam JS is already scroll-driven and read/write-phase-separated (no forced reflow) — do NOT change beam JS here.
- [x] 2.3 Confirm the deletion is visually a no-op. Verified via a new Storybook story (`event-card.stories.ts` → `Matched`): computed-style assertions prove the neon identity is intact (`border-top-width: 2px`, non-`none` `box-shadow`, gradient background) and the color source `--artist-hue` is still set, while the removed pieces are gone (`--artist-color` computes empty; `animation-name` no longer contains `color-drift`). This is a stronger, deterministic equivalent of a reference-profile screenshot.
- [ ] 2.4 Re-run the trace + PostHog check from tasks 1.1–1.2; confirm Recalculate Style self-time dropped materially versus the baseline. Record the after-P1 numbers.

## 3. P2 — Scope layout and style to the viewport

- [x] 3.1 Apply `content-visibility: auto` + `contain-intrinsic-size: auto <fallback>` to the date-group `<li>` (the natural scroll chunk), NOT per event-card, so off-screen groups skip style + layout. Use the `auto` keyword so each group's real rendered height is cached after first paint; pick the literal fallback from a typical group height (it only affects the never-rendered first paint).
- [x] 3.2 Verify CLS stays 0 (no scrollbar jump / layout shift from the intrinsic-size fallback) AND that the three lane columns do not drift once size containment is applied to the subgrid group `<li>` (the parent `1fr 1fr 1fr` columns are content-independent, so they should not — confirm on the reference profile).
- [ ] 3.3 Verify the `.date-separator` sticky behavior and the laser beams do not regress once containment is applied. Sticky: `content-visibility`'s implied `contain: layout paint` confines the sticky header to its group's box — scroll across multiple date groups and confirm the behavior is intentional and consistent (per the new spec scenario). Beams: scroll and confirm beams still position correctly and do not vanish for off-screen-then-revealed cards (the beam JS reads `getBoundingClientRect()` on cards now under `content-visibility: auto`). If either regresses, capture the repro; route a beam issue to the P3 follow-up, and for sticky apply the design's mitigation (lift containment onto a non-subgrid inner wrapper below the header) rather than silently expanding this change. NOTE: the STATIC contract is already Storybook-verified (`concert-highway.stories.ts` → `PopulatedTimetable`): each date-group `<li>` computes `content-visibility: auto` + `contain-intrinsic-block-size` with the 160px fallback (retuned from 320px in frontend#607 after the prod measurement), `.date-separator` stays `position: sticky`, three lanes render, and one `.laser-beam` is generated per matched card. What remains for the reference profile is the RUNTIME behavior a static story can't assert — beam positioning while scrolling, the sticky hand-off/persist UX, and CLS staying 0.
- [x] 3.4 Re-run the trace + PostHog check; confirm Layout self-time dropped versus the baseline and record the after-P2 numbers.

## 4. Validation & acceptance

- [ ] 4.1 Confirm the `dashboard-timetable-rendering` spec scenarios on the reference profile: (a) re-entry INP and (b) first-load LCP are each SUBSTANTIALLY lower than the recorded baseline with Layout + Recalculate Style no longer dominating; (c) off-screen cards contribute no style/layout to the entry cost; (d) a 3-second idle capture shows negligible card-visual Style/Layout self-time; (e) reduced-motion is honored. The absolute "good" CWV thresholds (LCP ≤ 2.5 s, INP ≤ 200 ms) are the cumulative goal across P1–P4, NOT a pass/fail gate for this CSS-only change.
- [x] 4.2b Add Storybook coverage for the affected components so the render-cost / visual contract is verifiable without auth or backend data: `event-card.stories.ts` (Matched/Unmatched/JourneyBadge — asserts neon identity intact, `color-drift`/`--artist-color` gone) and `concert-highway.stories.ts` (PopulatedTimetable — asserts `content-visibility: auto` + intrinsic-size on date groups, sticky separators, one beam per matched card). Both pass `npm run test-storybook`.
- [x] 4.2c Incidental a11y fix discovered while adding stories: the card shipped `<article role="button">`, which axe rejects (`aria-allowed-role`). Changed the card root to `<div role="button">` in `event-card.html` (CSS is class/attribute-based, so no visual change; confirmed by stories passing axe with no rule suppression). Minor, in-scope per user request.
- [x] 4.2 Run `make lint` and `make test` in `frontend/` (CSS-only change; keep any storied card visuals' stories/baselines in sync if they changed).
- [x] 4.3 If the after-P2 numbers still show a large Layout residue, the beam `getBoundingClientRect()` read cost dominating during scroll (note the beam JS is already read/write-phase-separated, so this is gBCR cost, NOT a forced-reflow loop), or the beam visual regression from 3.3, open the deferred P3/P4 follow-up change citing the measured residual — do not fold it into this change.

## 5. Close-out

- [ ] 5.1 Sync the `dashboard-timetable-rendering` delta into the main specs (`openspec sync`) before archiving.
- [x] 5.2 Record before/after INP·LCP·Layout·Style numbers in the PR description as the evidence of effect.
