## 1. Localization

- [x] 1.1 Add `auth.loginRequired` key to `src/locales/en/translation.json` and `src/locales/ja/translation.json`
- [x] 1.2 Add `common.dismiss` key to `src/locales/en/translation.json` and `src/locales/ja/translation.json`

## 2. Route Guard — isCompleted guest access control

- [x] 2.1 Update `src/hooks/auth-hook.ts` Priority 3: replace blanket `return true` with allowed-route allowlist (`DASHBOARD`, `DISCOVERY`, `MY_ARTISTS`); return `false` with toast for disallowed routes
- [x] 2.2 Fix existing `unauthenticated user` tests in `test/routes/my-artists-route.spec.ts` that fail due to `loading()` early return (populate `sut.artists` manually in `beforeEach`)

## 3. bottom-sheet dismiss fix

- [x] 3.1 Update `src/components/bottom-sheet/bottom-sheet.ts` `onBackdropClick`: replace `event.target !== this.scrollWrapper` with `(event.target as Element).closest('.sheet-page')` check; remove the `maxScroll <= 0` short-circuit added previously

## 4. Guest home selection persistence

- [x] 4.1 Move `store.dispatch({ type: 'guest/setUserHome', code })` outside `if (this.isOnboarding)` in `dashboard-route.ts` `onHomeSelected()` — dispatch for all unauthenticated users

## 5. Signup prompt banner dismiss

- [x] 5.1 Add × dismiss button to `signup-prompt-banner.html` with `svg-icon name="x"`
- [x] 5.2 Add `onDismiss()` method to `signup-prompt-banner.ts` dispatching `banner-dismissed` CustomEvent
- [x] 5.3 Add `.signup-banner-dismiss` styles to `signup-prompt-banner.css`
- [x] 5.4 Add `banner-dismissed.trigger="onBannerDismissed()"` to `my-artists-route.html`
- [x] 5.5 Add `onBannerDismissed()` method to `my-artists-route.ts`

## 6. Verification

- [x] 6.1 Run `make check` in frontend to confirm lint + tests pass
