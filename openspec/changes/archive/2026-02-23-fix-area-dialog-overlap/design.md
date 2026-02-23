## Context

The area selection bottom sheets (`region-setup-sheet` and `area-selector-sheet`) use `position: fixed; bottom: 0` with Tailwind z-index utilities (`z-40` backdrop, `z-50` panel) to overlay the page. The `bottom-nav-bar` uses `z-30`. This z-index stacking approach is fragile — any new fixed-position element introduces ordering conflicts — and the area dialog currently clips behind the nav bar on certain mobile viewports (issue #73).

Both sheets share the same visual pattern: a slide-up panel with a backdrop overlay, handle bar, and content area.

## Goals / Non-Goals

**Goals:**
- Fix the overlap between area selection dialogs and the bottom navigation bar
- Eliminate z-index utilities from the sheet components by using the native `<dialog>` Top Layer
- Preserve the existing slide-up bottom sheet visual behavior and animation
- Maintain accessibility (focus trapping, ESC to close, screen reader semantics)

**Non-Goals:**
- Refactoring all z-index usage across the entire app (discover-page, artist-discovery, etc.)
- Changing the bottom-nav-bar's own positioning strategy
- Modifying the area selection business logic or data flow
- Creating a shared/generic bottom-sheet primitive (keep each component self-contained for now)

## Decisions

### Decision 1: Use `<dialog>` with `showModal()` instead of fixed-position `<div>` + z-index

**Choice**: Native `<dialog>` element with `showModal()` API.

**Rationale**: `showModal()` promotes the element to the browser's Top Layer, which sits above all other stacking contexts — no z-index needed. It also provides a native `::backdrop` pseudo-element, built-in focus trapping, and ESC-to-close behavior.

**Alternatives considered**:
- **Popover API** (`popover` attribute): Designed for lightweight popovers, not modal dialogs. Doesn't trap focus or provide `::backdrop` by default. Not the right semantic fit for a full-screen bottom sheet.
- **Increase z-index values**: Band-aid fix that perpetuates the z-index war. Rejected per project Web Platform Baseline 2026 standards.

### Decision 2: CSS-only slide-up animation using `@starting-style` and `allow-discrete` transitions

**Choice**: Use the `@starting-style` CSS at-rule combined with `transition-behavior: allow-discrete` to animate the `<dialog>` open/close.

**Rationale**: The `<dialog>` element toggles between `display: none` and `display: block`. Traditional CSS transitions can't animate from `display: none`. The `@starting-style` rule (Baseline 2026) defines the initial state for the entry animation. Combined with `allow-discrete`, this enables smooth slide-up and fade-in on open, and slide-down/fade-out on close — all in CSS, no JavaScript animation logic needed.

**Animation spec**:
- Entry: `translate-y-full` + `opacity: 0` → `translate-y-0` + `opacity: 1`, 300ms ease-out
- Exit: reverse, 300ms ease-out
- `::backdrop`: opacity fade 0 → 0.6, 300ms

### Decision 3: Keep `<dialog>` bottom-anchored via CSS, not Anchor Positioning

**Choice**: Position the `<dialog>` at the bottom of the viewport using flexbox on the `<dialog>` itself (`align-items: flex-end`) combined with `margin: 0; max-height: 80vh`.

**Rationale**: CSS Anchor Positioning is designed for anchoring one element to another (e.g., tooltip to button). A full-width bottom sheet doesn't have an anchor element — it's viewport-relative. Simple flexbox alignment is the correct primitive here.

### Decision 4: Style `::backdrop` for dark blur overlay

**Choice**: Apply `background: oklch(0% 0 0 / 0.6); backdrop-filter: blur(4px)` to `::backdrop`.

**Rationale**: Replaces the manual `<div>` backdrop. Uses OKLCH per project color standards. Click-to-dismiss is achieved by listening for clicks on the `<dialog>` element itself (outside the inner content panel) via the `<dialog>` click event with target check.

### Decision 5: Aurelia 2 lifecycle integration

**Choice**: Call `this.dialogElement.showModal()` in `open()` and `this.dialogElement.close()` in `close()`, with `ref="dialogElement"` binding.

**Rationale**: Aurelia 2's `ref` binding provides direct element access. The `<dialog>` `close` event is used to sync the component's `isOpen` state. The `cancel` event (triggered by ESC) is handled to allow closing and running cleanup (e.g., resetting selected region in area-selector-sheet).

## Risks / Trade-offs

- **`@starting-style` browser support**: Baseline 2026 — supported in Chrome 117+, Safari 17.5+, Firefox 129+. Our target audience (mobile PWA users) will have these versions. → Mitigation: The dialog is fully functional without animation; `@starting-style` is progressive enhancement.
- **Test updates required**: Tests that query for `<div role="dialog">` or check z-index classes will need updating to query `<dialog>` elements. → Mitigation: Straightforward find-and-replace in test files.
- **Click-outside-to-close pattern change**: The `::backdrop` pseudo-element doesn't directly receive click events in all browsers. → Mitigation: Use the standard pattern of listening for `click` on the `<dialog>` itself and checking if `event.target === dialogElement` (click was on the backdrop area, not the inner content).
