## 1. Remove the `guest.language` storage surface

- [ ] 1.1 Delete `KEY_LANGUAGE`, `saveLanguage`, and `loadLanguage` from `src/adapter/storage/guest-storage.ts` (including the decoupling-rationale comment block).
- [ ] 1.2 Remove the `guestLanguage` `@observable`, `setGuestLanguage`, and `guestLanguageChanged` from `src/services/user-store.ts`, and drop the now-unused `loadLanguage`/`saveLanguage` imports.

## 2. Single-source the guest locale in UserStore

- [ ] 2.1 Change `UserStore.currentLanguage` (guest branch) to return `this.i18nLocale` instead of `guestLanguage ?? i18nLocale`; verify the authenticated branch is untouched.
- [ ] 2.2 Update `clearGuest` to clear only guest home + help-seen flags; confirm it no longer references any locale state, and refresh its doc comment to drop the decoupling explanation.

## 3. Explicit persistence in the shared locale utility

- [ ] 3.1 Change the anonymous path of `changeLocale` in `src/util/change-locale.ts` to call `i18n.setLocale(lang)` then `localStorage.setItem('language', lang)` (remove the `userStore.setGuestLanguage` write); update the function doc comment to describe the single-key persistence.

## 4. One-time legacy-key migration

- [ ] 4.1 In `migrateStorageKeys()` (`src/constants/storage-keys.ts`), add an idempotent step: if `localStorage['guest.language']` exists, copy it into `localStorage['language']` when the two differ (explicit guest choice wins), then remove `guest.language`. Document the precedence in a comment.
- [ ] 4.2 Lock in that `migrateStorageKeys()` runs before i18next detection: confirm the existing `main.ts` ordering (migration call precedes `new Aurelia()` / `I18nConfiguration` registration / `au.start()`), and if it has regressed, move the call earlier so the promoted `language` value is what the detector reads in the same session. The same-session spec guarantee depends on this ordering.

## 5. Tests

- [ ] 5.1 Update `src/util/change-locale.spec.ts`: anonymous path asserts `i18n.setLocale` + `localStorage.setItem('language', lang)` and issues no RPC; remove `setGuestLanguage` assertions.
- [ ] 5.2 Update `src/services/user-store.spec.ts` (and any UserStore guest-language tests): `currentLanguage` guest branch tracks `i18nLocale`; remove `guestLanguage`/`setGuestLanguage` cases.
- [ ] 5.3 Add `migrateStorageKeys()` tests covering the four spec scenarios: guest.language differs from language (promote + remove), guest.language present while language is absent (promote + remove), equals (remove only), and no guest.language (no-op).
- [ ] 5.4 Run `make check` (lint + typecheck + unit tests) until green.

## 6. Manual verification

- [ ] 6.1 Reproduce the original bug locally: seed `localStorage` with `language=en` + `guest.language=ja`, load the app, confirm post-migration the UI renders Japanese AND the selector highlights 日本語, and `guest.language` is gone.
- [ ] 6.2 Verify the anonymous happy path: switch language in Settings/Welcome, reload, confirm the choice persists with only the `language` key present and the selector matches the UI.
- [ ] 6.3 Verify cancelled-login: as a guest, tap Login then cancel/return; confirm the rendered locale is unchanged.

## 7. Ship

- [ ] 7.1 Open the frontend PR (commit per Liverty-Music convention with `Refs: #<issue>`); drive CI green and merge once all checks pass.
- [ ] 7.2 Confirm the merge deploys to the dev environment (ArgoCD sync / new pod) and smoke-check the guest locale behavior in dev.
- [ ] 7.3 Cut the frontend GitHub Release (prod gate) and confirm the automated prod pin-bump → ArgoCD prod sync completes, then smoke-check in prod.
