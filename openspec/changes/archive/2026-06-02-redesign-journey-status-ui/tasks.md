## 1. View-model: derive UI state from status

- [x] 1.1 In `event-detail-sheet.ts`, add a pure helper that maps the current `journeyStatus` to per-node UI state (`completed` / `current` / `future` / `dimmed`) using the journey DAG (`TRACKING → APPLIED → {LOST | UNPAID → PAID}`)
- [x] 1.2 Add getters for the two phases: process nodes (`TRACKING`, `APPLIED`) and outcome routes (failure: `LOST`; success: `UNPAID`, `PAID`)
- [x] 1.3 Add an `outcomePending` getter that is true until `APPLIED` is reached (drives the "結果待ち" dim)
- [x] 1.4 Keep selection wired to the existing `journeyService.setStatus`; ensure any node (including dimmed) remains selectable (no state-machine guard)
- [x] 1.5 Unit-test the derivation for all five statuses (completed/current/future/dimmed sets + `outcomePending`) in `test/components/live-highway/`

## 2. Template: two-phase layout + radiogroup

- [x] 2.1 Replace the flat `repeat.for` pill row in `event-detail-sheet.html` with the process phase (`TRACKING ▸ APPLIED` horizontal segment)
- [x] 2.2 Add the outcome phase as a vertical stack: success route (`当選` heading → `UNPAID → PAID` mini-flow) on top, failure route (`LOST`) below
- [x] 2.3 Convert the control to `role="radiogroup"` with `role="radio"` options and bind `aria-checked` to the current status
- [x] 2.4 Add per-node non-color cues (icon for completed `✓` / action `!` / fail `✕` / current `●`) alongside text labels
- [x] 2.5 Preserve existing `data-testid` hooks and the "stop tracking" (remove journey) control

## 3. Styling: fill-vs-outline contrast + semantic color

- [x] 3.1 In `event-detail-sheet.css`, define scoped `oklch()` semantic color tokens (neutral/blue process, red `LOST`, amber `UNPAID`, green `PAID`) compliant with `cube/require-token-variables`
- [x] 3.2 Implement the contrast model: solid fill for `current`, low-emphasis `✓` for `completed`, outline for `future`, reduced-opacity for `dimmed` — exactly one solid node at a time
- [x] 3.3 Style the two-phase / vertical-outcome layout for the ~340px bottom sheet with ≥44px tap targets
- [x] 3.4 Remove the obsolete 25%-tint `[data-active]` / per-status `--_journey-*` active styles

## 4. Copy

- [x] 4.1 Add i18n keys for the "申込フロー" and "結果" section headings, the "当選" group heading, and the "結果待ち" affordance in `src/locales/ja/translation.json` and `src/locales/en/translation.json`

## 5. Verify

- [x] 5.1 Run `make check` (Biome + stylelint + typecheck + vitest) until green
- [x] 5.2 Manually verify all five statuses render correctly (current solid, passed `✓`, future outlined, exclusive route dimmed, `UNPAID` most prominent) in the bottom sheet
- [x] 5.3 If the visual-regression suite flags the intended UI change, refresh frontend visual baselines per the established baseline-refresh process

## 6. Ship

- [x] 6.1 Open the frontend PR (Conventional Commits, mandatory body + `Refs: #<issue>`); drive CI green and merge after all checks pass
- [x] 6.2 Cut the frontend prod release (GH Release retag → prod AR) and confirm the automated pin-bump → ArgoCD auto-sync reflects the change in prod
