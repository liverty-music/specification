## Why

The `<bottom-sheet>` component uses a JS hack (`requestAnimationFrame` + `scrollTo`) to set the initial scroll position when opened. This is fragile (timing-dependent) and fails entirely when `dismissable=false` because the dismiss-zone is conditionally removed from the DOM, leaving no scroll content — causing the sheet-body to render at the top of the viewport instead of the bottom. The fix should follow the [pure-web-bottom-sheet](https://github.com/viliket/pure-web-bottom-sheet) pattern: keep the dismiss-zone always in the DOM, control behavior via CSS, and use the "Snappy Scroll-Start" CSS animation to set initial scroll position without JS.

## What Changes

- Remove the `requestAnimationFrame` + `scrollTo` JS hack from `openChanged()`
- Keep the dismiss-zone element always in the DOM (remove `if.bind="dismissable"`)
- Use CSS to disable the dismiss-zone's `scroll-snap-align` when `dismissable=false`
- Implement the "Snappy Scroll-Start" `@keyframes` animation pattern for CSS-only initial scroll position control
- Update the dismiss detection to respect the `dismissable` attribute via CSS rather than DOM presence

## Capabilities

### New Capabilities

(None)

### Modified Capabilities

- `bottom-sheet-ce`: Replace JS-based initial scroll positioning with pure CSS "Snappy Scroll-Start" animation pattern; keep dismiss-zone always in DOM with CSS-controlled behavior

## Impact

- **Frontend only** — no backend or infrastructure changes
- Affected files:
  - `src/components/bottom-sheet/bottom-sheet.ts` — remove rAF + scrollTo from `openChanged()`
  - `src/components/bottom-sheet/bottom-sheet.html` — remove `if.bind="dismissable"` from dismiss-zone
  - `src/components/bottom-sheet/bottom-sheet.css` — add `@keyframes initial-snap`, CSS variable for snap-align control
  - `test/components/bottom-sheet.spec.ts` — update tests for new behavior
