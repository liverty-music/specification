## Why

The app has two independent toast implementations:

1. **ToastNotification** (`IToastService`) — A centralized service using `popover="manual"` for top-layer rendering. Supports severity levels (info/warning/error), auto-dismiss, and stacking. Used throughout the app for transient notifications.

2. **MyArtists undo toast** — A one-off `position: absolute` div in `my-artists-page.html` with custom show/hide logic, a 5-second timer, and an "Undo" action button.

The undo toast exists as a separate implementation solely because `IToastService` has no concept of action buttons. This leads to duplicated positioning logic, inconsistent animation, and a z-index layering bug (the undo toast hides behind `<dialog>` elements).

## What Changes

Extend `IToastService` to support an optional action button on toasts:

```typescript
toastService.show("Artist X unfollowed", "info", {
  action: { label: "Undo", callback: () => this.undo() },
  duration: 5000,
})
```

Then replace the custom undo toast in MyArtistsPage with a single `IToastService.show()` call.

## Capabilities

### New Capabilities

(none — this is an enhancement to an existing internal component)

### Modified Capabilities

- `frontend-toast-notification`: The `IToastService.show()` method accepts an optional `action` parameter with a `label` and `callback`. When provided, the toast renders an action button alongside the message. Tapping the action button invokes the callback and dismisses the toast. The auto-dismiss timer is paused while the user hovers/focuses the toast (to prevent accidental timeout on actionable toasts).

## Impact

- **Frontend repo only** — no backend or specification changes
- **Files affected**:
  - `src/components/toast-notification/toast-notification.ts` — Extend `IToastService.show()` signature with optional `action` parameter; update `ToastItem` interface
  - `src/components/toast-notification/toast-notification.html` — Add conditional action button rendering in toast template
  - `src/routes/my-artists/my-artists-page.html` — Remove inline undo toast div
  - `src/routes/my-artists/my-artists-page.ts` — Replace `undoVisible` / `undoArtist` / undo timer logic with `IToastService.show()` call; simplify undo state
- **No breaking API changes** — `IToastService.show()` gains an optional parameter; existing callers are unaffected
- **Depends on**: `fix-shell-layout-popover-banners` (Change A) should be merged first since it fixes the undo toast's popover layering as an interim measure. This change then replaces that interim fix with the proper unified approach.
