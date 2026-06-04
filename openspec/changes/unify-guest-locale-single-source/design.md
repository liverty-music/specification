## Context

The anonymous (guest) UI locale is currently persisted in **two** decoupled `localStorage` keys:

- `language` — the `i18next-browser-languagedetector` cache (`lookupLocalStorage: 'language'`, `caches: ['localStorage']`). This drives the **actually rendered** locale via the i18next detection chain at boot.
- `guest.language` — owned exclusively by `UserStore`. `UserStore.currentLanguage` (guest branch) returns `guestLanguage ?? i18nLocale`, and the Settings/Welcome selector binds its highlight to that value.

There is no boot-time reconciliation for guests: `UserHydrationTask.runUserHydration()` returns early on `!auth.isAuthenticated`, and no other code path applies `guest.language` to i18n. When the two keys drift (e.g. the authed hydration cleanup removes `language`, a later guest reload re-detects `navigator='en-US'` → `language='en'`, while an earlier explicit choice left `guest.language='ja'`), the selector highlights 日本語 while the UI renders English.

`guest.language` was introduced by the `introduce-entity-store-layer` change to fix a selector-reactivity bug (the highlight was previously driven by an unobservable render-time `i18n.getLocale()` read). But that same change also added `UserStore.i18nLocale`, an `@observable` mirror of the active locale kept in sync via the `Signals.I18N_EA_CHANNEL` event. The reactive mirror alone is sufficient for a reactive selector, which makes `guest.language` redundant — and the redundancy is the drift's root cause.

Verified during exploration: `guest.language` has exactly one reader (`UserStore`); no E2E or other module seeds/reads it; and the `clearGuest` "don't reset the visible language on login" decoupling exists solely to undo a side-effect that `clearGuest` itself introduces by clearing `guestLanguage`. Language participates in no signup/login heuristic (only `guestHome` does).

## Goals / Non-Goals

**Goals:**
- The guest selector highlight can never disagree with the rendered UI (eliminate the bug as a class, not an instance).
- Reduce code: one source of truth for the anonymous locale.
- Bring the implementation back into alignment with the existing `frontend-i18n` spec (single `language` key model).
- Migrate existing installs off `guest.language` without losing a guest's explicit choice.

**Non-Goals:**
- No change to the authenticated locale path (DB-sourced `preferred_language` via `user-profile-hydration` / `user-account-sync`).
- No change to the i18next detection-chain configuration in `main.ts`.
- No proto / backend / BSR work — frontend only.

## Decisions

### Decision 1: Remove `guest.language` entirely; derive the guest locale from `i18nLocale`

`UserStore.currentLanguage` (guest branch) returns `this.i18nLocale` instead of `guestLanguage ?? i18nLocale`. `i18nLocale` is already an `@observable` seeded from `i18n.getLocale()` and updated on every `setLocale` via the i18n EA channel, so it is both reactive AND always equal to the active locale. The selector highlight therefore tracks the rendered locale by construction.

Removed surface: `KEY_LANGUAGE` / `saveLanguage` / `loadLanguage` (`guest-storage.ts`); `guestLanguage` `@observable`, `setGuestLanguage`, `guestLanguageChanged` (`UserStore`).

**Alternative considered — keep two keys, reconcile on guest boot** (extend `runUserHydration`'s `!auth.isAuthenticated` branch to apply `guest.language` to i18n). Rejected: it entrenches a redundant key, requires a new MODIFIED spec requirement documenting the two-key model, and leaves a structure that can still drift between the apply and the next navigator re-detection. Single-source removes the failure mode rather than patching it.

### Decision 2: `changeLocale` anonymous path writes `language` explicitly

The anonymous path becomes `i18n.setLocale(lang)` followed by an explicit `localStorage.setItem('language', lang)`, matching the `frontend-i18n` "Shared Language Switching Utility → Anonymous caller path" requirement verbatim. We no longer rely on the detector's implicit `languageChanged` cache side-effect to persist the choice — the persistence is explicit and ordering-independent.

### Decision 3: `clearGuest` no longer touches the locale

`clearGuest` clears guest home + help-seen only. With `guest.language` gone there is nothing locale-related to clear, and the single `language` key persists across the Login reset — the cancelled-login behavior is preserved trivially, with no decoupling to reason about.

### Decision 4: One-time migration in `migrateStorageKeys()`, explicit choice wins

`migrateStorageKeys()` (already the home for idempotent legacy key migrations) gains a step: if `guest.language` exists, copy it into `language` when the two differ (the explicit guest choice outranks the detector cache), then remove `guest.language`. Idempotent and safe on every startup. This converges all existing installs and, for the user who reported the bug, honors their Japanese choice on the next boot before the redundant key is dropped.

**Alternative considered — let `language` win / just delete `guest.language`.** Rejected: `guest.language` was only ever written on an explicit user selection, whereas `language` may be an auto-detected navigator value, so deleting `guest.language` outright could silently discard a real preference (exactly the reporter's case).

## Risks / Trade-offs

- **[A guest who relied on the drift loses the stale `ja` highlight]** → By design: after migration the explicit `ja` is promoted into `language`, so the UI renders Japanese AND the selector highlights Japanese — the consistent, intended end-state. No preference is lost.
- **[Existing tests assert the old two-key behavior]** (`change-locale.spec.ts` asserts `setGuestLanguage`; UserStore tests reference `guestLanguage`) → Update them to the single-source assertions (anonymous path asserts `i18n.setLocale` + `localStorage.setItem('language', ...)`; `currentLanguage` guest branch asserts it tracks `i18nLocale`). The spec scenarios in this change are the test contract.
- **[Migration runs on every startup]** → It is a cheap, idempotent `getItem`/conditional-`setItem`/`removeItem` triple; after the first run `guest.language` is absent and it short-circuits.
- **[Rollback]** → Pure frontend change with no persisted-schema or backend coupling; reverting the commit restores the prior behavior. The migration is one-directional (it deletes `guest.language`), but since that key is being abandoned, a rollback simply returns to reading a now-absent key — equivalent to a fresh guest, which the code already handles.
