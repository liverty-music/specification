## SCOPE UPDATE: P2 was reverted — this change ships P1 only

P2 (`content-visibility` viewport-scoping) was implemented, measured (the −30%
forced-reflow win below is real), then **reverted** in frontend#612 (shipped in
prod v1.72.3): its paint containment disabled the `<li>` subgrid (cards overflowed
their lane) and, when moved to `.lane`, clipped the matched card's spotlight glow;
no viable un-clip exists (`overflow-clip-margin` requires `overflow: clip`, which
disables the sticky header, and is unsupported in Safari). P2's viewport-scoping is **deferred to P4** (group→lane→
card flatten). See design.md → the SUPERSEDING revert decision. The P2/§3 tasks
below are kept for the record but reflect reverted work.

## Measurement results (prod, 2026-09-13)

**A. Welcome-sample proxy** — reference profile (mobile 412×915, 4× CPU) against
the `/welcome` embedded sample timetable (same components, 23 groups / 30 cards,
**0 matched cards**). Before = v1.72.0. "After (P2)" = v1.72.1/.2 **while P2 was
still live**; P2 is now reverted so these Layout numbers are NOT in prod.

| Metric | Before (v1.72.0) | With P2 (v1.72.1) | Δ |
| --- | --- | --- | --- |
| Forced reflow, timetable render (`attached`) | 751 ms | 528 ms | −30% (reverted) |
| Render-interaction INP ("open timetable") | 118 ms | 117 ms | ~flat |
| CLS (render / scroll) | 0.00 / 0.00 | 0.00 / 0.00 | 0 |

**B. Authenticated `/dashboard`, real device (user-captured, matched cards
present)** — confirms the P1 win directly:

| Scenario | Result |
| --- | --- |
| Idle 3 s with matched cards (task 2.4) | No continuous Recalculate Style; matched cards static → **P1 (color-drift removal) confirmed** |
| Nav-tab re-entry INP (task 4.1a) | **2536 ms** vs the 7419 ms baseline (**−66%**), CLS 0 — substantial. The trace's Rendering category totals 2622 ms across the whole ~9 s capture window (not within the 2536 ms interaction), so Layout/Style still dominate the session → residual is P3/P4 |

The −66% re-entry improvement is attributable to P1 (the perpetual per-frame
style-recalc is gone); the remaining ~2.5 s is the synchronous DOM build of the
timetable, addressed by P4 (and it is the same synchronous render behind the
header/nav paint-starvation follow-up).

**Still not captured:** PostHog `web.vitals` field data (task 1.2); the P2 Layout
win is moot in prod (reverted).

## 1. Baseline measurement

- [x] 1.1 Record a DevTools performance trace of a dashboard tab-switch re-entry on the reference profile (Pixel 8 emulation, 4× CPU) with a populated timetable; capture INP, LCP, and the Bottom-up self-time for Layout, Recalculate Style, and Paint as the before-baseline.
- [ ] 1.2 Capture the current PostHog `web.vitals` (LCP/INP) and `perf.long_animation_frame` for route `/dashboard` as the field before-baseline.

## 2. P1 — Remove the continuous style-recalc driver

- [x] 2.1 Delete the `color-drift` infinite animation (applied to `.event-card[data-matched]`), the `@property --hue-drift` declaration, and the now-dead `--artist-color` / `--artist-color-dim` derivations in the `[artist-color]` rule from `frontend/src/components/live-highway/event-card.css`. This is a pure deletion — NO static replacement is needed, because `--hue-drift` fed only `--artist-color`, which has zero consumers (matched card visuals use raw `--artist-hue`), so the animation produced no visible output. Once the animation is gone, the `@media (prefers-reduced-motion: reduce)` block that only set `animation: none` on the matched card also becomes moot — remove it if it has nothing else to gate.
- [x] 2.2 Delete the unused `contact-glow` / `pulse-glow` keyframes in `event-card.css` (defined but applied to no element — dead code), so the continuous-invalidation pattern cannot be reintroduced. Scope this task to CSS only; the laser-beam JS is already scroll-driven and read/write-phase-separated (no forced reflow) — do NOT change beam JS here.
- [x] 2.3 Confirm the deletion is visually a no-op. Verified via a new Storybook story (`event-card.stories.ts` → `Matched`): computed-style assertions prove the neon identity is intact (`border-top-width: 2px`, non-`none` `box-shadow`, gradient background) and the color source `--artist-hue` is still set, while the removed pieces are gone (`--artist-color` computes empty; `animation-name` no longer contains `color-drift`). This is a stronger, deterministic equivalent of a reference-profile screenshot.
- [x] 2.4 Confirm Recalculate Style self-time dropped materially. DONE via the user's authenticated real-device capture (Measurement results B): a 3-second idle with matched cards on-screen shows NO continuous Recalculate Style (color-drift gone), and the nav-tab re-entry INP dropped 7419 ms → 2536 ms (−66%). PostHog field data (1.2) still outstanding but the trace confirms the P1 Style win.

## 3. P2 — Scope layout and style to the viewport (REVERTED — deferred to P4)

> P2 was implemented, measured (−30% forced reflow), then reverted (frontend#612,
> prod v1.72.3). `content-visibility`'s paint/layout containment disables the `<li>`
> subgrid (cards overflow their lane) and, on `.lane`, clips the matched-card glow;
> no cross-browser fix exists. The tasks below record that outcome; a correct
> implementation is deferred to P4 (see design.md).

- [x] 3.1 Attempt P2 (`content-visibility: auto` + `contain-intrinsic-block-size`) — implemented on the date-group `<li>`, then on `.lane`, then **REVERTED**. Root cause: containment disables subgrid (li) / clips glow (lane). Correct viewport-scoping needs the P4 flatten. Not in shipped prod.
- [x] 3.2 CLS stays 0 — CONFIRMED (0.00 on render + scroll, prod). The column-drift risk is moot now that P2 is reverted (subgrid intact, cards confined — reverified on prod v1.72.3: `grid-template-columns: subgrid`, lane 121 px / card 103 px).
- [x] 3.3 (SUPERSEDED by the revert — no longer applicable) Sticky/beam-under-containment verification is moot: with P2 reverted there is no containment, so `.date-separator` sticky and the laser beams behave exactly as before this change (reverified on prod v1.72.3). Re-opens only if P2 is re-attempted under P4.
- [x] 3.4 After-P2 Layout measured: forced reflow 751 ms → 528 ms (−30%) on the welcome-sample proxy (Measurement results A). NOTE: this win is NOT in shipped prod — P2 was reverted. It stands as the evidence that the P4 approach is worth pursuing.

## 4. Validation & acceptance

- [x] 4.1 Spec scenarios for the P1-only shipped change: (a) re-entry INP SUBSTANTIALLY lower — MET (7419 ms → 2536 ms, −66%, CLS 0); (d) 3-second idle shows negligible card-visual Style — MET (no continuous recalc, task 2.4); (e) reduced-motion honored — implemented (fade-slide-up gated on `prefers-reduced-motion`). Deferred: (b) first-load LCP not separately captured on the authenticated device (re-entry was); (c) "off-screen cards contribute no style/layout" is a P2/P4 outcome — **moved to P4** (P2 reverted). At sync (5.1), scope the spec's "off-screen content is not styled/laid out eagerly" scenario to P4 so the P1-only change does not claim it.
- [x] 4.2b Add Storybook coverage for the affected components so the render-cost / visual contract is verifiable without auth or backend data: `event-card.stories.ts` (Matched/Unmatched/JourneyBadge — asserts neon identity intact, `color-drift`/`--artist-color` gone) and `concert-highway.stories.ts` (PopulatedTimetable). After the P2 revert this story is the lane-overflow regression guard: it asserts NO `content-visibility`, the `<li>` keeps `grid-template-columns: subgrid`, each lane is < half the row width, a card does not overflow its lane, plus sticky separators and one beam per matched card. Both pass `npm run test-storybook`.
- [x] 4.2c Incidental a11y fix discovered while adding stories: the card shipped `<article role="button">`, which axe rejects (`aria-allowed-role`). Changed the card root to `<div role="button">` in `event-card.html` (CSS is class/attribute-based, so no visual change; confirmed by stories passing axe with no rule suppression). Minor, in-scope per user request.
- [x] 4.2 Run `make lint` and `make test` in `frontend/` (CSS-only change; keep any storied card visuals' stories/baselines in sync if they changed).
- [x] 4.3 Follow-ups identified (to be opened as separate changes, NOT folded here): **P4** — viewport-scoping done right (flatten group→lane→card so containment lives on a non-subgrid full-row box; re-earn the −30% Layout win P2 showed) + optional virtualization; **P3** — beam `getBoundingClientRect()` scroll cost (already reflow-optimized, so gBCR cost only); **header/nav paint starvation** on re-entry (synchronous 23-group render blocks the optimistic header/nav paint; INP 2536 ms) — fix via yield-before-heavy-render and/or the P4 flatten. See design.md → Follow-ups.

## 5. Close-out

- [ ] 5.1 Sync the `dashboard-timetable-rendering` delta into the main specs (`openspec sync`) before archiving.
- [x] 5.2 Record before/after INP·LCP·Layout·Style numbers in the PR description as the evidence of effect.
