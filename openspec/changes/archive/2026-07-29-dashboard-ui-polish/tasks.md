## 1. PWA Update Snackbar — Action Button Visual Enhancement

- [x] 1.1 `snack-bar.css`: Add pill shape to `.snack-action-btn` (border: 1.5px solid, border-radius: full, padding, semi-transparent background)
- [x] 1.2 `snack-bar.css`: Add `@keyframes update-pulse` (box-shadow glow, period ≈ 1.8s) and apply to `.snack-action-btn`
- [x] 1.3 `snack-bar.css`: Suppress pulse animation under `@media (prefers-reduced-motion: reduce)` while keeping pill styling

## 2. Spotlight Icon

- [x] 2.1 `svg-icon.html`: Add `case="spotlight"` SVG (light housing rect → trapezoid head → triangle cone → bottom line)

## 3. Beam Effect Toggle

- [x] 3.1 `constants/storage-keys.ts`: Add `beamsEnabled = 'liverty:beams:enabled'` to `StorageKeys` enum
- [x] 3.2 `routes/dashboard/dashboard-route.ts`: Add `showBeams` property initialized from `StorageKeys.beamsEnabled` (default `false`), add `toggleBeams()` method that flips and persists to localStorage
- [x] 3.3 `routes/dashboard/dashboard-route.html`: Change `show-beams="true"` → `show-beams.bind="showBeams"` on `<concert-highway>`
- [x] 3.4 `routes/dashboard/dashboard-route.html`: Add beam toggle `<button>` in `<page-header>` slot between `<artist-filter-bar>` and `<page-help>`, with `data-active.bind`, `aria-pressed.bind`, and `<svg-icon name="spotlight">`
- [x] 3.5 `routes/dashboard/dashboard-route.css` (新規): Add `.beam-toggle` styles matching `.filter-trigger` pill button; active state uses brand color

## 4. Concert Date — Month Boundary Separator

- [x] 4.1 `entities/concert.ts`: Add `isFirstOfMonth: boolean` and `monthSeparatorLabel: string` fields to `DateGroup` interface
- [x] 4.2 `services/concert-store.ts`: In `toDateGroups()`, track `lastMonthKey` (slice 0–7 of `dateKey`); set `isFirstOfMonth` and compute `monthSeparatorLabel` via `toLocaleDateString('ja-JP', { year: 'numeric', month: 'long' })`
- [x] 4.3 `components/live-highway/concert-highway.html`: Inside `repeat.for="group of dateGroups"`, add `<div if.bind="group.isFirstOfMonth" class="month-separator">` before `<header class="date-separator">`
- [x] 4.4 `components/live-highway/concert-highway.css`: Add `.month-separator` styles (flex row with `::before`/`::after` hairlines, muted uppercase text, `var(--space-m)` top padding)
- [x] 4.5 `components/live-highway/concert-highway.spec.ts`: Update `DateGroup` fixtures to include `isFirstOfMonth` and `monthSeparatorLabel` fields

## 5. Filter Sheet — Artist List Height Constraint & Section Styling

- [x] 5.1 `components/artist-filter-bar/artist-filter-bar.css`: Add `max-height: 40dvh; overflow-y: auto` to `.artists-list`
- [x] 5.2 `components/artist-filter-bar/artist-filter-bar.css`: Add `border-block-start` hairline between `.filter-facet + .filter-facet`
- [x] 5.3 `components/artist-filter-bar/artist-filter-bar.css`: Add `text-transform: uppercase; letter-spacing: 0.05em` to `.facet-heading`

## 6. Bottom Sheet — Swipe Dismiss Responsiveness

- [x] 6.1 `components/bottom-sheet/bottom-sheet.css`: Change `--_duration: 240ms` → `--_duration: 160ms`
- [x] 6.2 `components/bottom-sheet/bottom-sheet.ts`: In `onSnapChange()`, set `this.scrollArea.style.pointerEvents = 'none'` before calling `requestClose()` when dismiss zone is detected
- [x] 6.3 `components/bottom-sheet/bottom-sheet.ts`: In `onClose()`, reset `this.scrollArea.style.pointerEvents = ''`
- [x] 6.4 `components/bottom-sheet/bottom-sheet.ts`: In `detaching()`, reset `this.scrollArea.style.pointerEvents = ''`
- [x] 6.5 `components/bottom-sheet/bottom-sheet.ts`: Add `onPointerUp()` handler — if `dismissable` and `scrollTop / maxScroll < 0.25`, call `requestClose()`
- [x] 6.6 `components/bottom-sheet/bottom-sheet.html`: Add `pointerup.trigger="onPointerUp()"` on `.scroll-area`

## 7. Verification & Shipping

- [x] 7.1 Run `make check` in `frontend/` and fix any lint/type errors
- [ ] 7.2 Manually verify all 5 UI improvements in the browser (prod build or dev server)
- [x] 7.3 Open PR in `frontend/` with all changes; link this change in the PR description
- [x] 7.4 Merge PR once CI passes → create frontend GitHub Release → ship to prod
