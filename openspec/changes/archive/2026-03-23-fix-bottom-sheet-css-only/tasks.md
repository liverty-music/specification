## 1. CSS Changes

- [x] 1.1 Add `@keyframes initial-snap` animation with `--snap-align: none` to `bottom-sheet.css`
- [x] 1.2 Apply `animation: initial-snap 0.01s backwards` to `dialog` selector
- [x] 1.3 Change `.dismiss-zone` to use `scroll-snap-align: var(--snap-align, start)` instead of hardcoded `start`
- [x] 1.4 Add `dialog:not([data-dismissable])` selector to set dismiss-zone `scroll-snap-align: none` and `pointer-events: none`
- [x] 1.5 Add Safari workaround via `@supports (-webkit-touch-callout: none)` for scroll-snap-type reset after initial-snap animation

## 2. HTML Template Changes

- [x] 2.1 Remove `if.bind="dismissable"` from `.dismiss-zone` element
- [x] 2.2 Add `data-dismissable` attribute binding to `dialog` element (e.g., `data-dismissable.bind="dismissable"`)

## 3. TypeScript Changes

- [x] 3.1 Remove `requestAnimationFrame` and `scrollTo` from `openChanged()` — keep only `showPopover()` / `hidePopover()`
- [x] 3.2 Keep `dismissableChanged()` — still needed for `popover` attribute (`auto`/`manual`) which CSS cannot control
- [x] 3.3 Already implemented — `onScrollEnd()` already has `if (!this.dismissable) return` guard

## 4. Test Updates

- [x] 4.1 Update unit tests for `openChanged()` — verify no `scrollTo` or `rAF` calls
- [x] 4.2 Add test: dismiss-zone is always in DOM regardless of `dismissable`
- [x] 4.3 Skipped — viewport bottom positioning is CSS-only (scroll-snap), not testable in jsdom
- [x] 4.4 Add test: swipe-to-dismiss is blocked when `dismissable=false`

## 5. Verification

- [x] 5.1 Run `make check` — 807/807 tests pass, lint warnings are pre-existing (user-client.ts TS error, CSS property order in original code)
- [x] 5.2 Browser verification: `dismissable=true` — sheet opens at bottom, swipe-down dismisses
- [x] 5.3 Browser verification: `dismissable=false` — sheet opens at bottom, cannot dismiss
