## 1. CSS: Hide trash column on touch devices

- [x] 1.1 Add `@media (pointer: coarse)` rule to hide `.artist-unfollow-col` and its `<th>` header
- [x] 1.2 Add `touch-action: pan-y` to `.artist-row` for scroll/swipe coexistence
- [x] 1.3 Fix border-radius: move `border-inline-end` and end-radius rules to `.hype-col:last-child` inside `.artist-row` under the `(pointer: coarse)` query

## 2. HTML: Add inner wrappers and custom attribute binding

- [x] 2.1 Wrap each `<th>` and `<td>` cell content in `<div class="cell-inner">` in `my-artists-route.html`
- [x] 2.2 Add `swipe-to-delete` custom attribute binding to the `<tr repeat.for>` element

## 3. Implement `swipe-to-delete` Custom Attribute

- [x] 3.1 Scaffold `src/custom-attributes/swipe-to-delete.ts` as an Aurelia 2 Custom Attribute with a `callback` bindable
- [x] 3.2 Register the component in `main.ts` (or the relevant DI registration file)
- [x] 3.3 Implement `pointerdown` handler: record start position, call `setPointerCapture()`
- [x] 3.4 Implement `pointermove` handler: direction-lock logic (`|dx| > |dy| * 1.5`), translate `cell-inner` elements via WAAPI
- [x] 3.5 Implement `pointerup` handler: check threshold (40% of row width), either trigger callback or snap back via WAAPI `reverse()`
- [x] 3.6 Implement `pointercancel` handler: immediately reset all `cell-inner` transforms to 0
- [x] 3.7 Clean up all event listeners in `detaching()` lifecycle hook

## 4. CSS: Animate cell-inner wrappers

- [x] 4.1 Add `.cell-inner` base styles (display: contents or flex passthrough so layout is unaffected)
- [x] 4.2 Verify table layout is visually unchanged after adding wrappers

## 5. Verification

- [x] 5.1 Manual test on touch device (or devtools touch emulation): swipe past threshold triggers unfollow + undo toast
- [x] 5.2 Manual test: swipe below threshold snaps back cleanly
- [x] 5.3 Manual test: vertical scroll in artist list is not interrupted
- [ ] 5.4 Manual test on desktop (pointer: fine): trash icon visible, no swipe behavior
- [ ] 5.5 Keyboard test: tab to hidden trash button, Enter triggers unfollow
- [x] 5.6 Run `make check` and fix any lint/type errors

## 6. Decision: Abandoned

- [x] 6.1 Swipe approach abandoned — `<table>` scroll container prevents reliable horizontal swipe
  detection. `overflow-y: auto` on the fieldset ancestor takes pointer precedence over
  `touch-action: none` on `<tr>`. No CSS-native solution exists for this constraint.
  Replaced by: `long-press-unfollow` change (long-press → BottomSheet confirmation).
- [x] 6.2 Rollback: removed `swipe-to-delete.ts`, `cell-inner` wrappers, `touch-action` from CSS.
  CSS-only changes (pointer: coarse hide + border-radius fix) retained in `long-press-unfollow`.
