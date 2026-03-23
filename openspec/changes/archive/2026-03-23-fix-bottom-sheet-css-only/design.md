## Context

The `<bottom-sheet>` component currently uses `requestAnimationFrame` + `scrollTo({ top: scrollHeight })` in `openChanged()` to position the sheet-body at the bottom of the viewport after `showPopover()`. This JS-based approach has two problems:

1. **Timing fragility**: rAF 1-frame delay may not be sufficient for all browsers to complete top-layer layout
2. **dismissable=false bug**: When `dismissable=false`, the dismiss-zone is removed from the DOM via `if.bind`, leaving no scroll content — sheet-body renders at the top of the viewport instead of the bottom

The [pure-web-bottom-sheet](https://github.com/viliket/pure-web-bottom-sheet) library demonstrates a production-proven CSS-only pattern using "Snappy Scroll-Start" — a CSS animation that temporarily disables all scroll-snap-align values except the initial snap point, triggering the browser's native re-snap mechanism.

## Goals / Non-Goals

**Goals:**
- Remove all JS-based scroll positioning (`rAF`, `scrollTo`) from `openChanged()`
- Fix the `dismissable=false` layout bug (sheet-body at top)
- Keep dismiss-zone always in the DOM, controlled by CSS only
- Use the "Snappy Scroll-Start" CSS pattern for initial position

**Non-Goals:**
- Multiple snap points (not needed for our use case — we only need open/dismissed)
- Nested scroll mode or expand-to-scroll (our sheet content is always short)
- SSR / Declarative Shadow DOM support

## Decisions

### D1: Keep dismiss-zone always in DOM, control via CSS attribute

**Choice**: Remove `if.bind="dismissable"` from the dismiss-zone. Instead, use a `data-dismissable` attribute on the dialog and control `scroll-snap-align` via CSS.

```css
.dismiss-zone {
  scroll-snap-align: var(--snap-align, start);
}

dialog:not([data-dismissable]) .dismiss-zone {
  scroll-snap-align: none;
  pointer-events: none;
}
```

**Alternative**: Keep `if.bind` and use `align-content: end` for `dismissable=false` case.

**Rationale**: Keeping a consistent DOM structure eliminates the class of bugs where layout changes between dismissable modes. The pure-web-bottom-sheet reference implementation uses this exact pattern (`swipe-to-dismiss` attribute toggles CSS, DOM stays the same). CSS-only control is more performant and predictable than conditional DOM rendering.

### D2: "Snappy Scroll-Start" CSS animation for initial position

**Choice**: Use a `@keyframes` animation that temporarily sets `--snap-align: none` on all snap points, except `.sheet-body` which overrides with `scroll-snap-align: end`. The browser's "Re-snapping After Layout Changes" spec behavior positions the scroll container at the sheet-body automatically.

```css
@keyframes initial-snap {
  from, to {
    --snap-align: none;
  }
}

dialog {
  animation: initial-snap 0.01s backwards;
}

.sheet-body {
  scroll-snap-align: end;  /* Always end, not via variable */
}

.dismiss-zone {
  scroll-snap-align: var(--snap-align, start);
}
```

When the animation runs: dismiss-zone's snap is `none`, sheet-body's snap is `end` → browser snaps to sheet-body (bottom). After animation ends: dismiss-zone's snap reverts to `start` → user can now swipe to dismiss.

**Alternative**: JS `scrollTo` with double-rAF for reliability.

**Rationale**: This follows the CSS Scroll Snap Level 1 spec's ["Re-snapping After Layout Changes"](https://drafts.csswg.org/css-scroll-snap-1/#re-snap) behavior — a well-defined browser mechanism. Zero JS, zero timing issues. The pure-web-bottom-sheet library has validated this across Chrome, Safari, and Firefox.

### D3: openChanged() simplification

**Choice**: After removing rAF + scrollTo, `openChanged()` becomes:

```ts
if (isOpen) {
  this.triggerElement = document.activeElement
  this.sheetElement.showPopover()
} else {
  this.sheetElement.hidePopover()
}
```

The CSS animation handles initial positioning automatically when the popover transitions from `display: none` to `display: block` (the animation re-runs via `@starting-style` or popover toggle).

**Rationale**: Maximum simplicity. The component's JS is only responsible for popover lifecycle, not layout.

## Risks / Trade-offs

- **[D2] Safari animation behavior**: Safari requires `display: inherit` on the host and a brief `scroll-snap-type: none` reset after the initial snap animation to prevent scroll position reset. The pure-web-bottom-sheet handles this with a `@supports (-webkit-touch-callout: none)` override. We should include the same Safari workaround.
- **[D1] dismiss-zone in non-dismissable mode**: The dismiss-zone is in the DOM but invisible and non-interactive. If a user somehow reaches it via programmatic scroll, the `scrollend` handler must check `dismissable` before closing. Current `onScrollEnd` already checks scroll ratio, and since dismiss-zone has `scroll-snap-align: none`, the browser won't snap to it.
