## 1. CSS Rewrite

- [x] 1.1 Rewrite `toast-notification.css`: replace `.toast-popover[popover]` container styles with a plain `.toast-stack` fixed-position layout container. Move `pointer-events: none`, flex-column, gap, and padding to `.toast-stack`.
- [x] 1.2 Rewrite `.toast-item` styles: add `popover="manual"` selector (`.toast-item:popover-open`), define entry state and `@starting-style` inside `:popover-open`. Define exit state on `.toast-item:not(:popover-open)`.
- [x] 1.3 Add `display allow-discrete` and `overlay allow-discrete` to the `.toast-item` transition shorthand. Keep `transform` and `opacity` transitions as-is.
- [x] 1.4 Remove `data-state="entering"/"exiting"` CSS rules. Severity exceptions (`data-severity`) remain unchanged.
- [x] 1.5 Verify block stays under 80 lines per CUBE CSS constraints.

## 2. HTML Template Update

- [x] 2.1 Replace the `div[popover="manual"].toast-popover` container with a plain `div.toast-stack` (no popover attribute). Keep `ref="containerElement"`.
- [x] 2.2 Add `popover="manual"` attribute to each `repeat.for` toast item div.
- [x] 2.3 Remove `data-state.bind="toastState(toast)"` binding from toast items.
- [x] 2.4 Add `ref` or event binding for `toggle` event on each toast item (e.g., `toggle.trigger="onToggle($event, toast)"`).

## 3. ViewModel Rewrite

- [x] 3.1 Remove `transitionend` event listener setup/teardown from `attached()`/`detaching()`. Remove `boundTransitionEnd` field and `onTransitionEnd()` method.
- [x] 3.2 Remove `visible` field from `ToastItem` interface. Keep `dismissed` for double-dismiss guard. Use DOM query by `data-toast-id` for element access instead of stored reference.
- [x] 3.3 Rewrite `show()`: after Aurelia inserts the DOM node, call `element.showPopover()` on the toast's element. Remove `hidePopover()`/`showPopover()` container re-insertion logic.
- [x] 3.4 Rewrite `dismiss()`: call `element.hidePopover()` on the toast's element. Clear the dismiss timer. Fire `onDismiss` callback.
- [x] 3.5 Add `onToggle(event, toast)` method: when `event.newState === 'closed'`, call `removeToast(toast)`.
- [x] 3.6 Remove `toastState()` method (no longer needed — `:popover-open` replaces `data-state`).
- [x] 3.7 Remove `prefersReducedMotion()` method (browser handles reduced motion via `allow-discrete` — no special JS path needed).
- [x] 3.8 Update `removeToast()`: remove from `toasts[]` array only. No `containerElement.hidePopover()` call needed.

## 4. Tests

- [x] 4.1 Remove `transitionend`-based test helpers and assertions from `toast-notification.spec.ts`.
- [x] 4.2 Add `toggle` event mock helper: create `ToggleEvent` with `newState: 'closed'` for simulating popover close.
- [x] 4.3 Update "should remove toast on transitionend after dismiss" → "should remove toast on toggle event after hidePopover".
- [x] 4.4 Update "should hide container popover when last toast is removed" → verify only `toasts[]` splice (no container `hidePopover` call).
- [x] 4.5 Add test: multiple simultaneous toasts dismiss independently without interfering.
- [x] 4.6 Run `make check` in frontend to verify lint + tests pass.

## 5. Verification

- [x] 5.1 E2E test: 3 rapid toasts appear as popover-open, auto-dismiss without zombies; verify vertical stacking in toast-stack container.
- [x] 5.2 E2E test: unfollow on My Artists page triggers undo toast with action button visible as popover.
- [x] 5.3 E2E test: toast popover renders above open dialog element (Top Layer stacking verified via elementFromPoint).
