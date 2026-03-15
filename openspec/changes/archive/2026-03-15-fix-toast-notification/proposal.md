## Why

Toast notifications fail to auto-dismiss when multiple toasts fire in quick succession (e.g., follow several artists on the Discover page). The root cause is a fragile architecture: a single `popover="manual"` container manages multiple toast children via CSS transitions and `transitionend` events. When the container is re-inserted into the Top Layer (`hidePopover()`/`showPopover()`) for a new toast, in-flight exit transitions on existing toasts are interrupted, `transitionend` never fires, and dismissed toasts remain in the DOM indefinitely as invisible zombies.

The current implementation predates the 2025 Web Platform Baseline, which provides `display`/`overlay` discrete transitions and the `:popover-open` pseudo-class — making the entire `transitionend`-based cleanup pattern unnecessary.

## What Changes

- Redesign the toast notification component so each toast item is an independent `popover="manual"` element, replacing the current single-container architecture.
- Use the Popover API lifecycle (`showPopover()`/`hidePopover()`, `:popover-open`, `toggle` event) for entry/exit management instead of manual `transitionend` event listeners.
- Use CSS `display`/`overlay` `allow-discrete` transitions with `@starting-style` for declarative entry/exit animations — no JS animation management needed.
- Simplify DOM structure: remove the wrapper `div[popover]` container; use a plain fixed-position stack container for layout only.
- Align CSS with CUBE CSS methodology: push animation concerns to the block layer, use `data-severity` exceptions, keep the block under 80 lines.

## Capabilities

### New Capabilities

_None — this is a bug fix and modernization of an existing capability._

### Modified Capabilities

- `design-system`: Toast notification component contract changes (individual popover elements instead of container-managed children). Dismiss mechanism changes from `transitionend`-based to Popover API `toggle` event-based.

## Impact

- **Frontend**: `src/components/toast-notification/` — all four files (`.ts`, `.html`, `.css`, `toast.ts`) will be modified. No changes to the `Toast` event class public API (`message`, `severity`, `options`, `handle`).
- **Tests**: `test/services/toast-notification.spec.ts` — tests need updating to reflect `toggle` event-based cleanup instead of `transitionend`.
- **Consumers**: No breaking changes. All existing `ea.publish(new Toast(...))` call sites remain unchanged. The `ToastHandle.dismiss()` API is preserved.
