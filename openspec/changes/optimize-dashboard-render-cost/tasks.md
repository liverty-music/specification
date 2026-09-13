## 1. Baseline measurement

- [ ] 1.1 Record a DevTools performance trace of a dashboard tab-switch re-entry on the reference profile (Pixel 8 emulation, 4× CPU) with a populated timetable; capture INP, LCP, and the Bottom-up self-time for Layout, Recalculate Style, and Paint as the before-baseline.
- [ ] 1.2 Capture the current PostHog `web.vitals` (LCP/INP) and `perf.long_animation_frame` for route `/dashboard` as the field before-baseline.

## 2. P1 — Remove the continuous style-recalc driver

- [ ] 2.1 Remove the `color-drift` infinite animation of the `--hue-drift` custom property (applied to `.event-card[data-matched]`) from `frontend/src/components/live-highway/event-card.css`; replace with a static (or reduced-motion-gated) treatment that keeps the matched card's color/gradient identity without per-frame style recalculation.
- [ ] 2.2 Delete the unused `contact-glow` / `pulse-glow` keyframes in `event-card.css` (defined but applied to no element — dead code), so the continuous-invalidation pattern cannot be reintroduced. Scope this task to CSS animations only; the laser-beam per-frame `getBoundingClientRect()` reflow is JS and is deferred to P3 — do NOT change beam JS here.
- [ ] 2.3 Ensure any retained motion is wrapped in `@media (prefers-reduced-motion: no-preference)` and that reduced-motion users get a fully static card.
- [ ] 2.4 Re-run the trace + PostHog check from tasks 1.1–1.2; confirm Recalculate Style self-time dropped materially versus the baseline. Record the after-P1 numbers.

## 3. P2 — Scope layout and style to the viewport

- [ ] 3.1 Apply `content-visibility: auto` + a correct `contain-intrinsic-size` (from the real card height) to the concert card / lane / date-group elements so off-screen cards skip style + layout.
- [ ] 3.2 Verify CLS stays 0 (no scrollbar jump / layout shift from the intrinsic-size estimate) on the reference profile.
- [ ] 3.3 Verify the laser beams do not visually regress once containment is applied — scroll the timetable and confirm beams still position correctly and do not vanish for off-screen-then-revealed cards (the beam JS reads `getBoundingClientRect()` on cards that now live under `content-visibility: auto`). If they regress, capture the repro and route the fix to the P3 follow-up rather than expanding this change.
- [ ] 3.4 Re-run the trace + PostHog check; confirm Layout self-time dropped versus the baseline and record the after-P2 numbers.

## 4. Validation & acceptance

- [ ] 4.1 Confirm the `dashboard-timetable-rendering` spec scenarios on the reference profile: (a) re-entry INP and (b) first-load LCP are each SUBSTANTIALLY lower than the recorded baseline with Layout + Recalculate Style no longer dominating; (c) off-screen cards contribute no style/layout to the entry cost; (d) a 3-second idle capture shows negligible card-visual Style/Layout self-time; (e) reduced-motion is honored. The absolute "good" CWV thresholds (LCP ≤ 2.5 s, INP ≤ 200 ms) are the cumulative goal across P1–P4, NOT a pass/fail gate for this CSS-only change.
- [ ] 4.2 Run `make lint` and `make test` in `frontend/` (CSS-only change; keep any storied card visuals' stories/baselines in sync if they changed).
- [ ] 4.3 If the after-P2 numbers still show a large Layout residue, the beam `getBoundingClientRect()` forced reflow dominating, or the beam visual regression from 3.3, open the deferred P3/P4 follow-up change citing the measured residual — do not fold it into this change.

## 5. Close-out

- [ ] 5.1 Sync the `dashboard-timetable-rendering` delta into the main specs (`openspec sync`) before archiving.
- [ ] 5.2 Record before/after INP·LCP·Layout·Style numbers in the PR description as the evidence of effect.
