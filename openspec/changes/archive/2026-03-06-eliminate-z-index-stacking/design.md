## Context

The Liverty Music frontend contains 26 `z-index` declarations across 11 files. The `onboarding-guidance` spec explicitly prohibits z-index in the discovery page CSS, yet 7 instances remain. Three components use Tailwind `z-40`/`z-50`/`z-[60]`/`z-[70]`/`z-[100]` utilities for modal overlays via fixed-position `<div>` elements. Two persistent UI elements (`bottom-nav-bar`, `toast-notification`) use `z-30`/`z-50` for layering. The `coach-mark` uses `z-9999` for tutorial spotlight overlays with JS-calculated positioning.

Modern Web Platform APIs (all Baseline 2026) eliminate the need for any z-index:

- **Popover API** (`popover="manual"`) — Top Layer promotion without focus trapping, for persistent non-modal elements
- **CSS Anchor Positioning** — Declarative positioning relative to anchor elements, replacing `getBoundingClientRect()` JS calculations
- **`<dialog>` + `showModal()`** — Modal overlays in Top Layer with native `::backdrop`, focus trapping, ESC handling
- **`isolation: isolate`** — Explicit stacking context for component-internal layering without z-index

The `fix-area-dialog-overlap` change previously established the `<dialog>` + `@starting-style` pattern. This change extends that to all remaining z-index usages and achieves **zero z-index exceptions**.

## Complete z-index Inventory

| # | File | Selector / Class | z-index | Category | Migration |
|---|------|-------------------|---------|----------|-----------|
| 1 | `discover-page.css` | `.container::before` | 0 | Internal | `isolation: isolate` |
| 2 | `discover-page.css` | `.search-bar` | 20 | Internal | `isolation: isolate` |
| 3 | `discover-page.css` | `.genre-chips` | 15 | Internal | `isolation: isolate` |
| 4 | `discover-page.css` | `.orb-label` | 15 | Internal | `isolation: isolate` |
| 5 | `discover-page.css` | `.search-results` | 10 | Internal | `isolation: isolate` |
| 6 | `discover-page.css` | `.onboarding-hud` | 20 | Internal | `isolation: isolate` |
| 7 | `discover-page.css` | `.complete-button-wrapper` | 20 | Internal | `isolation: isolate` |
| 8 | `loading-sequence.css` | Various (6 instances) | 0, 1 | Internal | `isolation: isolate` |
| 9-14 | (counted as 6 in #8) | | | | |
| 15 | `event-detail-sheet.html` | backdrop `<div>` | z-40 | Modal | `<dialog>` |
| 16 | `event-detail-sheet.html` | sheet panel | z-50 | Modal | `<dialog>` |
| 17 | `my-artists-page.html` | context menu | z-50 | Modal | `<dialog>` |
| 18 | `my-artists-page.html` | passion selector | z-50 | Modal | `<dialog>` |
| 19 | `my-artists-page.html` | passion explanation | z-[60] | Modal | `<dialog>` |
| 20 | `tickets-page.html` | proof generation | z-50 | Modal | `<dialog>` |
| 21 | `tickets-page.html` | QR modal | z-50 | Modal | `<dialog>` |
| 22 | `signup-modal.html` | modal wrapper | z-[70] | Modal | `<dialog>` |
| 23 | `error-banner.html` | banner wrapper | z-[100] | Modal | `<dialog>` |
| 24 | `bottom-nav-bar.html` | nav container | z-30 | Persistent | `popover="manual"` |
| 25 | `toast-notification.html` | toast wrapper | z-50 | Persistent | `popover="manual"` |
| 26 | `coach-mark.css` | `.coach-mark-overlay` | z-9999 | Tutorial | `popover="manual"` + Anchor Positioning |

**Live-highway sticky date separator** (`z-20` in `live-highway.html` line 18) uses `isolation: isolate` on the scroll container to contain stacking.

## Goals / Non-Goals

**Goals:**
- Eliminate ALL z-index from the codebase (26 instances across 11 files to 0)
- Zero z-index exceptions — every use case has a modern API replacement
- Use `isolation: isolate` for component-internal stacking (discover-page, loading-sequence, live-highway)
- Use `<dialog>` + `showModal()` for all modal overlays (7 components)
- Use `popover="manual"` for persistent non-modal elements (bottom-nav-bar, toast-notification, coach-mark)
- Use CSS Anchor Positioning for coach-mark tooltip placement (replacing `getBoundingClientRect()` JS)
- Follow the established `<dialog>` + `@starting-style` animation pattern
- Maintain existing UX behavior (slide-up, backdrop dimming, swipe-to-dismiss, ESC-to-close)

**Non-Goals:**
- Creating a shared/generic bottom-sheet component (keep each component self-contained)
- Refactoring coach-mark spotlight rendering (canvas remains; only overlay stacking and tooltip positioning change)

## Decisions

### Decision 1: `isolation: isolate` for component-internal stacking (discover-page, loading-sequence, live-highway)

**Choice**: Add `isolation: isolate` to the component's root container to create an explicit stacking context. Remove all `z-index` declarations within the component. Elements stack by DOM source order within the isolated context.

**discover-page.css** (7 instances):
- Add `isolation: isolate` to `.container`
- Remove `z-index` from all 7 selectors
- Shadow DOM boundary already provides an isolated stacking context; `isolation: isolate` makes it explicit
- DOM source order: starfield `::before` < canvas < search bar < genre chips < onboarding HUD < complete button

**loading-sequence.css** (6 instances):
- Add `isolation: isolate` to the root wrapper
- Remove all 6 `z-index: 0` / `z-index: 1` declarations
- All elements are within a Shadow DOM component; no external stacking conflicts

**live-highway.html** (1 instance, `z-20` sticky date separator):
- Add `isolation: isolate` to the scroll container parent
- Remove `z-20` from the sticky date separator
- `position: sticky` elements paint above scrolled siblings naturally within an isolated stacking context

**Rationale**: `isolation: isolate` creates an explicit stacking context boundary. Within this boundary, elements stack by DOM order (later = on top) without needing z-index. This is the correct pattern for component-internal layering.

### Decision 2: `<dialog>` + `showModal()` for all modal overlays

**Choice**: Replace all fixed-position `<div>` + z-index overlays with native `<dialog>` elements promoted to the Top Layer via `showModal()`.

**Components migrated** (7 total):

| Component | Current | After |
|-----------|---------|-------|
| `event-detail-sheet` | `z-40` backdrop + `z-50` sheet | Single `<dialog>` + `::backdrop` |
| `my-artists-page` context menu | `z-50` overlay | `<dialog>` + `::backdrop` |
| `my-artists-page` passion selector | `z-50` overlay | `<dialog>` + `::backdrop` |
| `my-artists-page` passion explanation | `z-[60]` overlay | `<dialog>` + cancel suppression |
| `tickets-page` QR modal | `z-50` + manual `role="dialog"` | `<dialog>` (native a11y) |
| `tickets-page` proof generation | `z-50` + `role="alert"` | `<dialog>` + cancel suppression |
| `signup-modal` | `z-[70]` non-dismissible | `<dialog>` + cancel suppression |
| `error-banner` | `z-[100]` | `<dialog>` + auto-dismiss |

**Implementation pattern** (established by `fix-area-dialog-overlap`):
- `ref="dialogElement"` for DOM reference
- `showModal()` to open, `close()` to dismiss
- `::backdrop` pseudo-element for dimming (`background: oklch(0% 0 0 / 0.6); backdrop-filter: blur(4px)`)
- `@starting-style` for entry animations (slide-up or fade-in, 300ms ease-out)
- Click-outside-to-close: `event.target === dialogElement` check
- Non-dismissible dialogs: suppress `cancel` event to block ESC

**Why `<dialog>` not `popover`**: Modal overlays require focus trapping and backdrop dimming — `<dialog>` provides both natively. `popover` does not trap focus or provide `::backdrop`.

### Decision 3: `popover="manual"` for bottom-nav-bar

**Choice**: Replace `z-30` with `popover="manual"` to promote the nav bar to the Top Layer.

**Implementation**:
- Add `popover="manual"` attribute to the nav container element
- Call `this.navElement.showPopover()` on component `attached()` to promote to Top Layer
- Remove `z-30` class
- The nav bar remains always-visible; `popover="manual"` does not auto-dismiss on click-outside or ESC
- Top Layer elements paint above all non-Top-Layer content without z-index

**Why `popover="manual"`**: The nav bar is persistent and non-modal. It must sit above scrolling page content but must not trap focus or show a backdrop. `popover="manual"` provides Top Layer promotion with no auto-dismiss behavior and no focus trapping — exactly the semantics needed.

**Top Layer ordering**: The nav bar's `showPopover()` is called at app startup. Subsequent `showModal()` calls (for dialogs) are inserted later into the Top Layer stack, so they naturally paint above the nav bar. When the dialog closes, the nav bar is visible again. No z-index needed.

### Decision 4: `popover="manual"` for toast-notification

**Choice**: Replace `z-50` with `popover="manual"` to promote toasts to the Top Layer.

**Implementation**:
- Add `popover="manual"` attribute to the toast container
- Call `showPopover()` when a toast is displayed, `hidePopover()` when dismissed
- Remove `z-50` class
- Retain `pointer-events: none` on the container with `pointer-events: auto` on individual toast items (allows click-through around toasts)
- Toasts in Top Layer paint above the nav bar (later insertion = higher in stack)

**Why not `<dialog>`**: Toasts are non-modal, non-interactive (no focus trapping), and must allow click-through. `popover="manual"` matches these semantics.

### Decision 5: `popover="manual"` + CSS Anchor Positioning for coach-mark

**Choice**: Replace `z-9999` with `popover="manual"` for the overlay, and replace `getBoundingClientRect()` JS calculations with CSS Anchor Positioning for tooltip placement.

**Overlay (Top Layer promotion)**:
- Add `popover="manual"` to `.coach-mark-overlay`
- Call `showPopover()` when the coach mark activates, `hidePopover()` when dismissed
- Remove `z-index: 9999` from `.coach-mark-overlay` in `coach-mark.css`
- Top Layer promotion ensures the overlay paints above everything including the nav bar popover (later insertion order)
- The overlay canvas is a full-viewport element; `pointer-events: none` SHALL be applied to it so it does not intercept clicks
- `pointer-events: auto` is re-enabled on dismiss/next buttons within the overlay
- Click-through to the spotlighted element is handled by `elementFromPoint()` delegation: the overlay listens for clicks, temporarily hides itself, calls `document.elementFromPoint(x, y)` to find the underlying element, and forwards the event

**Tooltip positioning (CSS Anchor Positioning)**:
- Target element gets `anchor-name: --coach-target` (set dynamically via `style.anchorName`)
- Tooltip uses `position-anchor: --coach-target` with `position-area` for placement
- Use `position-try-fallbacks: flip-block, flip-inline` for viewport edge handling
- Remove `updatePosition()` JS method that currently uses `getBoundingClientRect()`
- Remove `ResizeObserver` that recalculates position on layout changes (CSS Anchor Positioning handles this automatically)

**Spotlight cutout**: The canvas-based spotlight rendering remains unchanged — it still uses `getBoundingClientRect()` to calculate the cutout position on the overlay canvas. Only the tooltip positioning migrates to CSS Anchor Positioning.

**Browser support**: CSS Anchor Positioning is Baseline Newly Available (2026/01) — Chrome 125+, Firefox 147+, Safari 26+. Our PWA targets modern mobile browsers.

### Decision 6: `isolation: isolate` for live-highway sticky date separator

**Choice**: Add `isolation: isolate` to the `live-highway` scroll container. Remove `z-20` from the sticky date separator.

**Rationale**: `position: sticky` elements within an `isolation: isolate` container paint above scrolled content naturally. The sticky element's stacking is relative to its scroll container, not the page — `isolation: isolate` formalizes this boundary.

### Decision 7: Top Layer architecture — stacking by insertion order

**Choice**: Document the intended Top Layer insertion order and the enforcement mechanism replacing z-index.

The Top Layer is a strict last-in-on-top stack. Order depends entirely on JS call sequence, not element type. The intended visual layering is:

```
Top Layer Stack (last = on top):
─────────────────────────────────
  coach-mark popover     ← highest priority
  toast-notification     ← must appear above dialogs
  <dialog> modals        ← above nav bar
  bottom-nav-bar         ← base layer
─────────────────────────────────
  Normal stacking context (isolation: isolate per component)
```

**Enforcement mechanism** (required because Top Layer order is insertion-order, not declarative):

- **Bottom-nav**: `showPopover()` called once at app startup. Always at the bottom of the Top Layer.
- **Dialogs**: `showModal()` called on user action. Inserted after nav, so they paint above it.
- **Toasts**: When a toast fires while a dialog is open, the toast is already below the dialog in the stack. The toast service SHALL call `hidePopover()` + `showPopover()` to re-insert itself at the top of the Top Layer stack, ensuring it paints above any open dialog.
- **Coach-mark**: `showPopover()` called on tutorial activation. During tutorials, no dialogs or toasts are expected. If a toast fires during a tutorial, the coach-mark SHALL also re-insert itself (`hidePopover()` + `showPopover()`) to maintain top position.

If ordering conflicts arise, the fix is re-insertion (`hidePopover()` + `showPopover()`) to move the element to the top of the stack, not adding z-index.

## Risks / Trade-offs

- **CSS Anchor Positioning browser support**: Newly Available as of 2026/01. Safari 26+ required. If targeting older Safari, the coach-mark tooltip falls back to existing JS positioning (progressive enhancement).
- **`popover="manual"` on bottom-nav-bar**: The nav bar in the Top Layer is removed from normal document flow visually but remains in DOM flow. CSS `position: fixed` + `popover` may require testing across mobile browsers to ensure no layout shifts.
- **Swipe-to-dismiss in `<dialog>`**: Touch event handlers on `event-detail-sheet` must work within the `<dialog>` element. Touch targets change from the fixed `<div>` to the `<dialog>` content area. Mobile Safari and Chrome testing required.
- **`@starting-style` browser support**: Baseline 2026 — Chrome 117+, Safari 17.5+, Firefox 129+. The `<dialog>` is fully functional without animation; `@starting-style` is progressive enhancement.
- **Test updates**: Tests querying `<div role="dialog">`, checking z-index classes, or verifying `class="fixed"` need updating to query `<dialog>` elements and check `[open]` attribute.
- **Top Layer ordering is implicit**: No CSS property controls Top Layer order — it depends on JS call sequence. Document the intended order (Decision 7) and test for regressions if component initialization order changes.
