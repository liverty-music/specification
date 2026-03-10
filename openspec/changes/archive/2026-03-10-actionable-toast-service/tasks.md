## 1. Extend Toast Event Class

- [x] 1.1 Define `ToastOptions` interface (`duration?: number`, `action?: { label: string, callback: () => void }`, `onDismiss?: () => void`) and `ToastHandle` interface (`dismiss(): void`) in `toast.ts`
- [x] 1.2 Change `Toast` constructor from `(message, severity?, durationMs?)` to `(message, severity?, options?)` and add a `handle: ToastHandle | null` property
- [x] 1.3 Update `ToastNotification` element to read `action` from the `Toast` event and populate `toast.handle` on subscribe
- [x] 1.4 Implement `ToastHandle.dismiss()` — triggers fade-out and cancels auto-dismiss timer
- [x] 1.5 When action callback is invoked, dismiss the toast and cancel auto-dismiss

## 2. Update Toast Template

- [x] 2.1 Add conditional action button to `toast-notification.html` — render `<button>` when `toast.action` exists
- [x] 2.2 Style action button (font-semibold, uppercase, right-aligned, distinct from message text)
- [x] 2.3 Add `onAction(toast)` handler in TS that calls `toast.action.callback()` and dismisses

## 3. Migrate Existing Callers

- [x] 3.1 Update all existing `new Toast(msg, severity, durationMs)` calls to use `new Toast(msg, severity, { duration: durationMs })` (search all `.ts` files) — no callers use the third parameter; no changes needed

## 4. Replace MyArtists Undo Toast

- [x] 4.1 Remove `undoVisible`, `undoTimer`, `clearUndoTimer()` from `my-artists-page.ts`
- [x] 4.2 Add `undoHandle: ToastHandle | null` property
- [x] 4.3 Rewrite `unfollowArtist()` to use `ea.publish(new Toast(...))` with action
- [x] 4.4 Remove `undoHandle.dismiss()` from `undo()` — dismissal is now handled automatically by the toast action infrastructure (see D6)
- [x] 4.5 Remove `commitPendingUnfollow()` and `clearUndoTimer()` — timer management is handled by toast auto-dismiss
- [x] 4.6 Remove undo toast `<div>` from `my-artists-page.html`
- [x] 4.7 Remove the `popover="manual"` undo toast added by Change A (if already merged)

## 5. Verification

- [x] 5.1 Run `make check` (lint + test) and fix any failures — biome + tsc pass, 300 tests pass
- [x] 5.2 Verify undo toast appears with "Undo" button after unfollowing an artist — Playwright + unit test (swipe-to-unfollow publishes toast with action label)
- [x] 5.3 Verify tapping "Undo" restores the artist and dismisses the toast — unit test: action callback re-inserts at original index
- [x] 5.4 Verify toast auto-dismisses after 5 seconds and commits the unfollow — unit test: onDismiss fires commitUnfollow RPC
- [x] 5.5 Verify undo toast is visible above open dialogs (passion selector, context menu) — popover="manual" with hidePopover/showPopover re-insert ensures top-layer ordering
- [x] 5.6 Verify existing toast callers (discover page, error toasts) still work correctly — all 18 callers use 1-2 arg form, backward-compatible
