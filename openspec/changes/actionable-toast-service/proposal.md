## Why

The app has two independent toast implementations:

1. **ToastNotification** — An app-level custom element using `IEventAggregator` pub/sub and `popover="manual"` for top-layer rendering. Supports severity levels (info/warning/error), auto-dismiss, and stacking. Callers publish `Toast` events via `ea.publish(new Toast(...))`.

2. **MyArtists undo toast** — A one-off `position: absolute` div in `my-artists-page.html` with custom show/hide logic, a 5-second timer, and an "Undo" action button.

The undo toast exists as a separate implementation solely because the `Toast` event class has no concept of action buttons. This leads to duplicated positioning logic, inconsistent animation, and a z-index layering bug (the undo toast hides behind `<dialog>` elements).

## What Changes

Extend the `Toast` event class to support an optional action button:

```typescript
ea.publish(new Toast("Artist X unfollowed", "info", {
  action: { label: "Undo", callback: () => this.undo() },
  duration: 5000,
}))
```

Then replace the custom undo toast in MyArtistsPage with a single `ea.publish(new Toast(...))` call.

## Capabilities

### New Capabilities

(none — this is an enhancement to an existing internal component)

### Modified Capabilities

- `frontend-toast-notification`: The `Toast` event class accepts an optional `action` parameter (via `ToastOptions`) with a `label` and `callback`. When provided, the `ToastNotification` element renders an action button alongside the message. Tapping the action button invokes the callback and dismisses the toast.

## Impact

- **Frontend repo only** — no backend or specification changes
- **Files affected**:
  - `src/components/toast-notification/toast.ts` — Extend `Toast` event class constructor with optional `ToastOptions` parameter; add `ToastHandle` interface
  - `src/components/toast-notification/toast-notification.html` — Add conditional action button rendering in toast template
  - `src/routes/my-artists/my-artists-page.html` — Remove inline undo toast div
  - `src/routes/my-artists/my-artists-page.ts` — Replace `undoVisible` / `undoArtist` / undo timer logic with `ea.publish(new Toast(...))` call; simplify undo state
- **No breaking API changes** — `Toast` constructor gains an optional parameter; existing callers are unaffected
- **Depends on**: `fix-shell-layout-popover-banners` (Change A) should be merged first since it fixes the undo toast's popover layering as an interim measure. This change then replaces that interim fix with the proper unified approach.
