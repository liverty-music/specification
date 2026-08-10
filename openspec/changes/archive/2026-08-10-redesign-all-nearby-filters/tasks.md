## 1. Date-range bottom sheet component

- [x] 1.1 Create a `date-range-sheet` component built on the shared `bottom-sheet` primitive: quick-preset chips (今週末 / 7日以内 / 30日以内) + editable 開始/終了 `<input type="date">` fields + a range hint + an apply action
- [x] 1.2 Move the preset date math (weekend / 7-day / 30-day resolution) into the sheet, reusing `date-presets.ts`; a quick preset applies its `{ from, to }` and closes the sheet in one tap
- [x] 1.3 Custom path: editing a field keeps the sheet open; apply confirms and closes. Live-validate `from ≤ to` and inclusive span ≤ 30 days, show an inline hint, and block apply on invalid; set the `to` input `min`/`max` too
- [x] 1.4 Emit the existing `range-changed` `{ from, to }` `CalendarDate` pair (unchanged contract) on apply / preset selection

## 2. Compact filter bar (chips)

- [x] 2.1 Replace the inline date-preset group + standalone area row in `dashboard-route.html` with a single-row filter bar: an area chip and a date chip
- [x] 2.2 Date chip: label shows the current selection (preset name, or localized range via `Intl.DateTimeFormat('ja-JP')` e.g. `8/12〜8/20`, single day when `from === to`); tap opens the `date-range-sheet`
- [x] 2.3 Area chip: shows the current area name; tap opens the existing `user-home-selector` (session-only override, unchanged persistence semantics)
- [x] 2.4 Remove all inline-expansion markup/CSS so the filter area is a fixed-height single row and the timetable height is never reduced
- [x] 2.5 Retire the old `date-preset-selector` component (and its inline custom-range block) once the chip + sheet replace it

## 3. Localized Japanese copy

- [x] 3.1 Audit `allNearby.*` i18n keys (ja + en) — mode title/toggle, area prompt, empty state, preset labels, range hint — and rewrite the Japanese into natural, native phrasing
- [x] 3.2 Ensure ja/en key parity (every `allNearby.*` key exists in both bundles); add any keys the new sheet/chip need
- [x] 3.3 Confirm all date/range display uses `Intl.DateTimeFormat('ja-JP')`, not the native input format

## 4. Verification & tests

- [x] 4.1 Update/add unit tests: preset date math, range validation (inverted + >30 days), localized label formatting; update any tests asserting old strings/markup
- [x] 4.2 Run `make check` (biome, stylelint, template tsc, no-inline-style guard, i18n parity, vitest, build) — all green
- [x] 4.3 Verify on the dev server (headless browser): one-tap sheet open, preset apply+close, custom edit+apply, localized chip label, 30-day guard, timetable height unchanged across all states

## 5. PR, release & prod verification

- [x] 5.1 Open the frontend PR (#520); Visual Regression passed as-is (no baseline conflict), all CI green
- [x] 5.2 Merge the PR (#520 → main a39ee7e)
- [x] 5.3 GH Release v1.40.0 → dispatch-prod-pin (CP 8a0d01e) → ArgoCD synced web-app to v1.40.0
- [x] 5.4 Prod (liverty-music.app v1.40.0) verified: 2-chip bar (東京都 + 7日以内), one-tap sheet (今週末/7日以内/30日以内 + 開始日/終了日), custom 8/15〜8/22 localized, natural JA copy, 0 console errors
