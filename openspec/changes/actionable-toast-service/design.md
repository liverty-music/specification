## Design Decisions

### D1: Extend existing Toast event class, don't create a new one

The `ToastNotification` custom element already handles top-layer rendering, stacking, auto-dismiss, and severity styling via `IEventAggregator` pub/sub. Adding an action button is a natural extension of the `Toast` event class, not a separate concern. A second toast system would create confusion about which to use.

### D2: API shape — optional options object

```typescript
// Current Toast event class
class Toast {
  constructor(
    public message: string,
    public severity: ToastSeverity = 'info',
    public durationMs: number = 2500,
  ) {}
}

// New Toast event class
class Toast {
  constructor(
    public message: string,
    public severity: ToastSeverity = 'info',
    public options?: ToastOptions,
  ) {}
}

interface ToastOptions {
  duration?: number        // ms, default 2500
  action?: {
    label: string          // button text (e.g. "Undo")
    callback: () => void   // invoked on tap
  }
}
```

The third constructor parameter changes from `durationMs: number` to `options?: ToastOptions`. All existing `ea.publish(new Toast(msg, severity, durationMs))` callers need to be updated to `ea.publish(new Toast(msg, severity, { duration: durationMs }))`.

Alternative considered: overloaded signatures. Rejected because a single options object is clearer and more extensible.

### D3: Action button dismisses the toast

When the user taps the action button:
1. Invoke `action.callback()`
2. Immediately dismiss the toast (fade out)
3. Cancel the auto-dismiss timer

This matches Material Design snackbar behavior and Google's UX guidelines for undo patterns.

### D4: Return a dismiss handle

```typescript
// Handle is obtained from the Toast event object, not from publish()
const toast = new Toast('Artist unfollowed', 'info', {
  duration: 5000,
  action: { label: 'Undo', callback: () => this.undo() },
})
this.ea.publish(toast)
this.undoHandle = toast.handle  // set by ToastNotification subscriber

interface ToastHandle {
  dismiss(): void
}
```

Aurelia's `IEventAggregator.publish()` is fire-and-forget (returns `void`). The `Toast` event class exposes a `handle: ToastHandle | null` property that is populated by the `ToastNotification` subscriber when it processes the event. Callers read `toast.handle` after publishing to obtain programmatic dismiss control (e.g., dismissing on navigation).

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
// 3 state properties
private undoArtist: FollowedArtist | null = null
private undoIndex = -1
private undoHandle: ToastHandle | null = null

// 2 methods, no timer management
private unfollowArtist(artist) {
  // ... optimistic removal ...
  this.undoHandle?.dismiss()
  const toast = new Toast(
    this.i18n.tr('myArtists.unfollowed', { name: artist.name }),
    'info',
    {
      duration: 5000,
      action: { label: this.i18n.tr('myArtists.undo'), callback: () => this.undo() },
    },
  )
  this.ea.publish(toast)
  this.undoHandle = toast.handle
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
