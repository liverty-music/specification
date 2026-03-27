## 1. Fix BottomSheet pre-attach showPopover error

- [x] 1.1 Add try-catch around `this.host.showPopover()` in `BottomSheet.openChanged()` (`frontend/src/components/bottom-sheet/bottom-sheet.ts`) — matching the existing `hidePopover()` catch pattern
- [x] 1.2 Add unit test: BottomSheet with `open` bound to `true` at creation time opens successfully after `attached()`

## 2. Verify PostSignupDialog opens

- [x] 2.1 Run existing PostSignupDialog tests to confirm no regressions
- [ ] 2.2 Manual verification: signup with a new account on dev environment and confirm PostSignupDialog BottomSheet opens on dashboard
