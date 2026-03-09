## Design Decisions

### D1: Extend existing service, don't create a new one

The `IToastService` already handles top-layer rendering, stacking, auto-dismiss, and severity styling. Adding an action button is a natural extension, not a separate concern. A second toast system would create confusion about which to use.

### D2: API shape — optional options object

```typescript
// Current signature
show(message: string, severity?: ToastSeverity, durationMs?: number): void

// New signature
show(message: string, severity?: ToastSeverity, options?: ToastOptions): void

interface ToastOptions {
  duration?: number        // ms, default 2500
  action?: {
    label: string          // button text (e.g. "Undo")
    callback: () => void   // invoked on tap
  }
}
```

The third parameter changes from `durationMs: number` to `options?: ToastOptions`. This is a breaking change to the internal API, but all existing callers either omit the third parameter or pass a number — these need to be updated to `{ duration: N }`.

Alternative considered: overloaded signatures. Rejected because a single options object is clearer and more extensible.

### D3: Action button dismisses the toast

When the user taps the action button:
1. Invoke `action.callback()`
2. Immediately dismiss the toast (fade out)
3. Cancel the auto-dismiss timer

This matches Material Design snackbar behavior and Google's UX guidelines for undo patterns.

### D4: Return a dismiss handle

```typescript
show(message: string, severity?: ToastSeverity, options?: ToastOptions): ToastHandle

interface ToastHandle {
  dismiss(): void
}
```

The caller can programmatically dismiss the toast (e.g., if the undo window expires due to a navigation event). This replaces the custom `undoTimer` / `clearTimeout` logic in MyArtistsPage.

### D5: No hover-pause for v1

Pausing auto-dismiss on hover/focus adds complexity (touch vs mouse, focus trap interaction with dialogs). For the undo use case, a 5-second duration is sufficient. This can be added later if needed.

## MyArtistsPage Simplification

### Before

```typescript
// 4 state properties
public undoArtist: FollowedArtist | null = null
public undoVisible = false
private undoTimer: ReturnType<typeof setTimeout> | null = null
private undoIndex = -1

// 3 methods + timer management
private unfollowArtist(artist) { ... 15 lines ... }
public undo() { ... 10 lines ... }
private commitPendingUnfollow() { ... 12 lines ... }
private clearUndoTimer() { ... }
```

### After

```typescript
// 2 state properties
private undoArtist: FollowedArtist | null = null
private undoIndex = -1
private undoHandle: ToastHandle | null = null

// 2 methods, no timer management
private unfollowArtist(artist) {
  // ... optimistic removal ...
  this.undoHandle?.dismiss()
  this.undoHandle = this.toastService.show(
    this.i18n.tr('myArtists.unfollowed', { name: artist.name }),
    'info',
    {
      duration: 5000,
      action: { label: this.i18n.tr('myArtists.undo'), callback: () => this.undo() },
    },
  )
}

public undo() {
  if (!this.undoArtist) return
  this.undoHandle?.dismiss()
  // ... re-insert at original position ...
}
```

Timer management, `undoVisible` state, and the template-level undo div are all eliminated.

## Toast Template Change

```html
<!-- Before -->
<div ...>
  ${toast.message}
</div>

<!-- After -->
<div ...>
  ${toast.message}
  <button
    if.bind="toast.action"
    click.trigger="onAction(toast)"
    class="... font-semibold uppercase tracking-wide ..."
  >
    ${toast.action.label}
  </button>
</div>
```

The action button sits inline after the message text, right-aligned via `ms-auto` or flex gap.
