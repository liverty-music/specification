## 1. Extend Toast Event Class

- [ ] 1.1 Define `ToastOptions` interface (`duration?: number`, `action?: { label: string, callback: () => void }`) and `ToastHandle` interface (`dismiss(): void`) in `toast.ts`
- [ ] 1.2 Change `Toast` constructor from `(message, severity?, durationMs?)` to `(message, severity?, options?)` and add a `handle: ToastHandle | null` property
- [ ] 1.3 Update `ToastNotification` element to read `action` from the `Toast` event and populate `toast.handle` on subscribe
- [ ] 1.4 Implement `ToastHandle.dismiss()` — triggers fade-out and cancels auto-dismiss timer
- [ ] 1.5 When action callback is invoked, dismiss the toast and cancel auto-dismiss

## 2. Update Toast Template

- [ ] 2.1 Add conditional action button to `toast-notification.html` — render `<button>` when `toast.action` exists
- [ ] 2.2 Style action button (font-semibold, uppercase, right-aligned, distinct from message text)
- [ ] 2.3 Add `onAction(toast)` handler in TS that calls `toast.action.callback()` and dismisses

## 3. Migrate Existing Callers

- [ ] 3.1 Update all existing `new Toast(msg, severity, durationMs)` calls to use `new Toast(msg, severity, { duration: durationMs })` (search all `.ts` files)

## 4. Replace MyArtists Undo Toast

- [ ] 4.1 Remove `undoVisible`, `undoTimer`, `clearUndoTimer()` from `my-artists-page.ts`
- [ ] 4.2 Add `undoHandle: ToastHandle | null` property
- [ ] 4.3 Rewrite `unfollowArtist()` to use `ea.publish(new Toast(...))` with action
- [ ] 4.4 Update `undo()` to call `undoHandle.dismiss()`
- [ ] 4.5 Remove `commitPendingUnfollow()` and `clearUndoTimer()` — timer management is handled by toast auto-dismiss
- [ ] 4.6 Remove undo toast `<div>` from `my-artists-page.html`
- [ ] 4.7 Remove the `popover="manual"` undo toast added by Change A (if already merged)

## 5. Verification

- [ ] 5.1 Run `make check` (lint + test) and fix any failures
- [ ] 5.2 Verify undo toast appears with "Undo" button after unfollowing an artist
- [ ] 5.3 Verify tapping "Undo" restores the artist and dismisses the toast
- [ ] 5.4 Verify toast auto-dismisses after 5 seconds and commits the unfollow
- [ ] 5.5 Verify undo toast is visible above open dialogs (passion selector, context menu)
- [ ] 5.6 Verify existing toast callers (discover page, error toasts) still work correctly
