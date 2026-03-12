## 1. Detail Sheet: Dynamic popover mode + popstate handling

- [x] 1.1 Add `@bindable` or constructor-injected `IOnboardingService` to `event-detail-sheet.ts` to read onboarding state
- [x] 1.2 In `open()`, set `this.sheetElement.popover` to `"manual"` if onboarding Step 4, otherwise `"auto"`, before calling `showPopover()`
- [x] 1.3 Remove the manual `onKeyDown` Escape listener from `open()`, `close()`, and `detaching()` (popover="auto" handles Escape natively; manual mode should not allow Escape)
- [x] 1.4 Remove `onBackdropClick()` method and `click.trigger="onBackdropClick($event)"` from `<dialog>` (popover="auto" handles light dismiss natively; manual mode blocks all dismiss)
- [x] 1.5 Add `popstate` event listener in `open()` that calls `close()` when the user navigates back; skip `history.replaceState` inside `close()` when triggered by popstate
- [x] 1.6 Remove `popstate` listener in `close()` and `detaching()` to prevent leaks
- [x] 1.7 Add `toggle` event listener on the `<dialog>` to detect when `popover="auto"` light-dismisses the sheet, and run cleanup (URL revert, state reset) in that handler
- [x] 1.8 Disable swipe-down during onboarding Step 4 by guarding `onTouchStart`/`onTouchMove`/`onTouchEnd` with an `isDismissable` check

## 2. Coach Mark: Top-layer re-ordering

- [x] 2.1 Add `bringToFront()` public method to `coach-mark.ts` that calls `hidePopover()` then `showPopover()` on `overlayEl`, wrapped in `requestAnimationFrame` to batch repaints
- [x] 2.2 Expose `bringSpotlightToFront()` on `IOnboardingService` that delegates to the coach mark's `bringToFront()` (or emits an event the coach mark listens for)

## 3. Dashboard: Coordinate Step 4 stacking order

- [x] 3.1 In `onTutorialCardTapped()`, after calling `activateSpotlight(...)`, call `onboarding.bringSpotlightToFront()` to re-insert the coach mark popover above the detail sheet in the top layer
- [x] 3.2 In `loading()` Step 4 recovery path, also call `bringSpotlightToFront()` after `activateSpotlight()` to handle page reload case

## 4. CSS Cleanup

- [x] 4.1 Remove `event-detail-sheet.css` rule for `.event-detail-sheet:popover-open::backdrop` background/blur styles (popover="auto" provides built-in backdrop handling; keep only transition rules if needed)
- [x] 4.2 Verify `event-detail-sheet` animation transitions (`@starting-style`, `:popover-open`, `:not(:popover-open)`) still work correctly with `popover="auto"`

## 5. Verification

- [x] 5.1 Test onboarding Step 3→4 flow: concert card tap opens detail sheet, coach mark appears ABOVE sheet targeting My Artists tab, tapping My Artists advances to Step 5
- [x] 5.2 Test normal (non-onboarding) detail sheet dismiss: tap outside closes sheet, Escape closes sheet, swipe down closes sheet, browser back closes sheet
- [x] 5.3 Test page reload during Step 4: coach mark re-appears above detail sheet, My Artists tab is tappable
- [x] 5.4 Run `make check` to verify lint, typecheck, and tests pass
