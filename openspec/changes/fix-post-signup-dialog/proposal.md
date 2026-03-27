## Why

The PostSignupDialog fails to display after first-time signup due to a component lifecycle timing bug. `BottomSheet.openChanged()` calls `showPopover()` during the `binding` phase before `attached()` has set the `popover` attribute on the host element, causing an uncaught `InvalidStateError` that prevents the dialog from ever opening. This is the only path where `BottomSheet.open` is `true` at initial bind time (all other consumers open the sheet via user interaction after attach).

## What Changes

- Fix `BottomSheet.openChanged()` to handle the pre-attach case where `showPopover()` is called before the `popover` attribute exists on the host element
- Add defensive error handling in `openChanged()` for the `showPopover()` call (matching the existing `try-catch` pattern already used for `hidePopover()`)

## Capabilities

### New Capabilities

_None_

### Modified Capabilities

- `post-signup-dialog`: Clarify that the dialog MUST reliably open when `active` is bound to `true` at component creation time (not only on subsequent changes)
- `bottom-sheet-ce`: `openChanged()` SHALL handle the case where `showPopover()` is called before `attached()` has initialized the `popover` attribute — the `attached()` fallback (`if (this.open) this.openChanged(true)`) ensures recovery

## Impact

- **Frontend**: `BottomSheet` component (`src/components/bottom-sheet/bottom-sheet.ts`) — single-line fix adding `try-catch` around `showPopover()` in `openChanged()`
- **No API/backend/proto changes required**
- **No breaking changes**
