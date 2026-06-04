## Why

A guest (unauthenticated) user sees the Settings/Welcome language selector highlight **日本語** while the entire UI renders in **English**. The anonymous locale is stored in two decoupled `localStorage` keys — `language` (the i18next detector cache that drives the rendered locale) and `guest.language` (UserStore-owned, drives only the selector highlight) — and nothing reconciles them on a guest boot. When the two keys drift, the selector and the rendered UI disagree. The second key is redundant: UserStore already exposes a reactive mirror of the active locale (`i18nLocale`), so a single source of truth both fixes the bug and removes code.

## What Changes

- **BREAKING (storage)**: Remove the `guest.language` localStorage key and all of its plumbing — `KEY_LANGUAGE`, `saveLanguage`, `loadLanguage` in `guest-storage.ts`; the `guestLanguage` `@observable`, `setGuestLanguage`, and `guestLanguageChanged` in `UserStore`.
- `UserStore.currentLanguage` (guest branch) returns the existing reactive `i18nLocale` mirror, which always equals the active i18n locale — so the selector highlight can never drift from the rendered UI.
- `changeLocale` anonymous path persists the new locale by calling `i18n.setLocale(lang)` **and** an explicit `localStorage.setItem('language', lang)`, matching the existing `frontend-i18n` "Anonymous caller path" requirement verbatim instead of relying on the detector's implicit cache side-effect.
- `UserStore.clearGuest` clears only the guest home + help-seen flags; it never touches the locale. The single `language` key persists naturally, preserving the cancelled-login behavior with no decoupling needed.
- One-time migration in `migrateStorageKeys()`: if a legacy `guest.language` value exists, treat it as the user's explicit choice (higher intent than the detector cache), copy it into `language` when they differ, then delete `guest.language`. This removes the redundant key for all existing installs and honors the affected guest's Japanese choice on their next boot.
- Update `change-locale.spec.ts` and the `UserStore` tests to the single-source assertions.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `frontend-i18n`: The anonymous locale is a single source of truth (`localStorage['language']`); add a requirement that the language selector highlight reflects the active i18n locale (so it can never disagree with the rendered UI), and a requirement for the one-time `guest.language` → `language` migration precedence (explicit guest choice wins, then the legacy key is removed).

## Impact

- **Frontend only** — no proto, no backend, no BSR generation, no release coordination.
- Affected code: `src/adapter/storage/guest-storage.ts`, `src/constants/storage-keys.ts` (`migrateStorageKeys`), `src/services/user-store.ts`, `src/util/change-locale.ts`, and the tests `src/util/change-locale.spec.ts`, `src/services/user-store.spec.ts` (and any UserStore guest-language tests).
- No change to the authenticated locale path (DB-sourced `preferred_language` via `user-profile-hydration` / `user-account-sync`) or to the i18next detection chain config in `main.ts`.
- Unwinds the two-key design introduced by the `introduce-entity-store-layer` change; the reactivity goal of that change is retained via the `i18nLocale` observable.
