## Context

The toast notification component (`src/components/toast-notification/`) uses a single `popover="manual"` container div that holds multiple toast items as child divs. Entry/exit animations are managed via CSS transitions on `transform`/`opacity`, with `transitionend` events driving DOM cleanup. When multiple toasts overlap (common during rapid artist follows on the Discover page), the container's `hidePopover()`/`showPopover()` re-insertion into the Top Layer interrupts in-flight transitions, causing `transitionend` to never fire and dismissed toasts to remain as invisible zombies.

The 2025 Web Platform Baseline provides native tools for this exact problem: per-element popover lifecycle, `:popover-open` pseudo-class, `@starting-style`, and `display`/`overlay` discrete transitions via `allow-discrete`.

## Goals / Non-Goals

**Goals:**

- Eliminate the zombie toast bug by removing `transitionend` dependency entirely.
- Each toast independently managed as its own `popover="manual"` element — no shared lifecycle.
- Declarative CSS-only entry/exit animations using `@starting-style`, `:popover-open`, and `allow-discrete`.
- Simplify the ViewModel by delegating animation lifecycle to the browser.
- Preserve the existing public API (`Toast` event class, `ToastHandle.dismiss()`).
- Align CSS with CUBE CSS methodology (block layer, `data-*` exceptions, under 80 lines).

**Non-Goals:**

- Changing the toast visual design (colors, typography, layout).
- Adding new toast features (swipe-to-dismiss, progress bar, stacking limits).
- Modifying any toast consumer code (`discover-page.ts`, `my-artists-page.ts`, etc.).

## Decisions

### Decision 1: Individual popover per toast item

**Choice:** Each toast item is a `popover="manual"` element. A plain `position: fixed` div serves as a layout-only stack container.

**Alternatives considered:**
- **Keep single container popover, add setTimeout fallback:** Fixes the immediate bug but preserves the fragile architecture. The `transitionend` listener remains as dead code alongside the fallback timer. Doesn't leverage the platform.
- **Use Web Animations API (`element.animate()`):** Reliable `finished` promise, but moves animation definition from CSS to JS, conflicting with the CUBE CSS approach of keeping visual concerns in stylesheets.

**Rationale:** The Popover API was designed for exactly this — independent elements entering/leaving the Top Layer. Using it as intended eliminates the entire class of bugs caused by shared container lifecycle. Each toast's `showPopover()`/`hidePopover()` is atomic and doesn't affect siblings.

### Decision 2: CSS `display`/`overlay` discrete transitions for exit animations

**Choice:** Toast CSS includes `transition: ... display allow-discrete, overlay allow-discrete`. When `hidePopover()` is called, the browser:
1. Removes `:popover-open` → triggers CSS transition to exit state
2. `overlay allow-discrete` keeps the element in the Top Layer until transition completes
3. `display allow-discrete` transitions `display: none` at the end
4. No JS event listener needed for animation completion

**Alternatives considered:**
- **`transitionend` event:** Current approach — unreliable when transitions are interrupted.
- **`setTimeout` matching animation duration:** Works but couples JS timer to CSS duration value. Any duration change requires updating both.

**Rationale:** This is the Web Platform's intended mechanism for animating elements in/out of the Top Layer. Zero JS animation management code.

### Decision 3: `toggle` event for DOM cleanup

**Choice:** Listen for the `toggle` event on each toast popover element. When `newState === 'closed'`, remove the toast from the `toasts[]` array (which triggers Aurelia to remove the DOM node).

**Why not just let CSS handle everything?** The toast item needs to be removed from Aurelia's `toasts[]` array to clean up the repeater. CSS handles the visual exit; the `toggle` event tells us when the popover has fully closed (after transition completes when using `allow-discrete`).

**Alternatives considered:**
- **`transitionend` on opacity:** Current approach — fragile.
- **`setTimeout` after `hidePopover()`:** Works but doesn't account for actual transition completion timing.

**Rationale:** `toggle` is the Popover API's dedicated lifecycle event. It fires after the full close sequence (including any CSS transitions when `allow-discrete` is used), making it the semantically correct signal for cleanup.

### Decision 4: DOM structure simplification

**Choice:**

```
Before (current):
  <div popover="manual" class="toast-popover">     ← single popover container
    <div class="toast-item" data-state="...">       ← plain div, no popover
    <div class="toast-item" data-state="...">
  </div>

After:
  <div class="toast-stack">                          ← plain fixed div (layout only)
    <div popover="manual" class="toast-item"          ← each is a popover
         data-severity="info">
    <div popover="manual" class="toast-item"
         data-severity="error">
  </div>
```

The stack container is a regular fixed-position div. It does not use the Popover API. Its only job is flex-column layout with gap for stacking multiple toasts. `pointer-events: none` on the container, `pointer-events: auto` on individual items — same as current.

### Decision 5: Remove `data-state` attribute, use `:popover-open` instead

**Choice:** Replace the `data-state="entering"/"exiting"` exception attribute with the native `:popover-open` pseudo-class.

```css
/* Entry: @starting-style inside :popover-open */
.toast-item:popover-open {
  opacity: 1;
  transform: translateY(0);

  @starting-style {
    opacity: 0;
    transform: translateY(-1rem);
  }
}

/* Exit: base state (when not :popover-open) */
.toast-item:not(:popover-open) {
  opacity: 0;
  transform: translateY(-1rem);
}
```

**Rationale:** `data-state` was a manual proxy for what `:popover-open` provides natively. Removing it eliminates the `toastState()` method in the ViewModel and the Aurelia binding that drives it.

## Risks / Trade-offs

**[Browser support]** → `allow-discrete` and `@starting-style` are Baseline 2025 (Chrome 117+, Safari 17.5+, Firefox 129+). The app already uses `@starting-style` in `my-artists-page.css` (bottom-sheet dialog). Acceptable for this PWA's target audience.

**[Top Layer stacking with dialogs]** → The current `hidePopover()`/`showPopover()` re-insertion exists to ensure toasts paint above open dialogs. With individual popovers, each `showPopover()` call inserts that toast at the top of the Top Layer stack. If a dialog is already open, the toast still appears above it because `showPopover()` always appends to the top. No additional handling needed.

**[Aurelia `repeat.for` and popover lifecycle]** → When Aurelia removes a DOM node from `repeat.for`, it may not call `hidePopover()`. We handle this by calling `hidePopover()` in the `dismiss()` method before the `toggle` event triggers removal. The flow is: `hidePopover()` → CSS exit transition → `toggle` event → splice from array → Aurelia removes DOM.

**[Test changes]** → Tests currently mock `transitionend` events. They need to be rewritten to mock `toggle` events instead. The mock pattern is simpler (no `propertyName` filtering needed).
