## Context

`BottomSheet` is the single dialog primitive used across the app. It manages the HTML Popover API lifecycle:

- `attached()`: Sets `popover` attribute on the CE host element, registers `toggle` listener
- `openChanged(isOpen)`: Calls `showPopover()` / `hidePopover()` on the CE host

All existing consumers open sheets via user interaction (tap → set `open = true`), so `openChanged()` always runs after `attached()`. The PostSignupDialog is the only case where `open` is `true` at initial bind time — the parent `DashboardRoute.loading()` sets `showPostSignupDialog = true` before any child component reaches `attached()`.

Aurelia 2 component lifecycle order:
```
binding → bound → attaching → attached
          ↑                      ↑
   openChanged(true)      popover attribute set
   showPopover() fails    fallback: if(this.open) openChanged(true)
```

`showPopover()` on an element without `popover` attribute throws `InvalidStateError` (DOMException). The `attached()` fallback at line 53-55 should recover, but if the binding-phase error disrupts the lifecycle, `attached()` may not execute.

## Goals / Non-Goals

**Goals:**
- Ensure PostSignupDialog reliably opens when `active` is bound to `true` at component creation time
- Keep the fix minimal and contained to `BottomSheet`

**Non-Goals:**
- Changing PostSignupDialog trigger logic or localStorage flag mechanism
- Changing when `loading()` sets `showPostSignupDialog` (moving to `attached()` would work but couples dashboard logic to component lifecycle details)
- Addressing dialog content visibility conditions (notification `granted` state, PWA `beforeinstallprompt` availability)

## Decisions

### Decision 1: Add try-catch around `showPopover()` in `openChanged()`

**Choice**: Wrap `showPopover()` in a try-catch, matching the existing pattern used for `hidePopover()`.

```typescript
public openChanged(isOpen: boolean): void {
    if (isOpen) {
        this.triggerElement = document.activeElement as HTMLElement | null
        try {
            this.host.showPopover()
        } catch {
            // Pre-attach: popover attribute not yet set.
            // attached() will retry via the if(this.open) guard.
        }
    } else {
        try {
            this.host.hidePopover()
        } catch {
            // Already hidden
        }
    }
}
```

**Why over alternative (move flag check to `attached()`)**: The bug is in `BottomSheet`, not in the consumer. Any future consumer that binds `open` to `true` at creation time would hit the same issue. Fixing it in `BottomSheet` is the correct layered fix.

**Why over alternative (set `popover` attribute in constructor)**: The CE host element may not be fully connected to the DOM in the constructor. Setting attributes in `attached()` is the Aurelia 2 convention for DOM manipulation.

### Decision 2: Rely on existing `attached()` fallback for actual open

The `attached()` method already has:
```typescript
if (this.open) {
    this.openChanged(true)
}
```

With the try-catch in place, the binding-phase call silently fails, and `attached()` retries successfully after the `popover` attribute is set. No new recovery logic needed.

## Risks / Trade-offs

- **[Silent failure masking]** → The try-catch could mask a genuine error in a future code change. Mitigated by: the comment explains the specific pre-attach scenario; `attached()` always retries if `open` is `true`.
- **[Timing of popover open]** → The sheet opens slightly later (at `attached()` instead of `binding`). In practice this is imperceptible — both phases complete within the same microtask/render cycle.
