## Context

See proposal.md (Why) for the two symptoms. The current mechanics, verified in code and in Zitadel v4.19.4 source:

- **Fan app detection.** The fan app detects its boot locale with i18next-browser-languagedetector:
  - Detection order is `querystring → localStorage → navigator`, the key is `language`, and `caches: ['localStorage']`.
  - `fallbackLng` is `'ja'` (`frontend/src/main.ts`).
  - The detector writes the detected language to the key on init, and i18next writes it again on every `changeLanguage`.
- **Fan hydration removes the key.** `frontend/src/services/user-hydration-task.ts` removes the key after applying the account's `preferredLanguage`, and after a successful backfill. The OIDC sign-out (`signoutRedirect`, `post_logout_redirect_uri = /`) reloads the app, so the next boot finds no key and detects from `navigator`.
- **Organizer detection.** The organizer console detects with `order: ['localStorage', 'navigator']`, the key is `organizer.language`, and `caches: []`. Only an explicit switch saves the key. Unsupported languages fall back to `ja` (`fallbackLng`, `toConsoleLocale`, `ConsoleLanguage.current` initial value).
- **Sign-in sends no language.** `shared/services/auth-service.ts` `signIn`/`signUp` call `userManager.signinRedirect` without `ui_locales`. oidc-client-ts 3.x accepts `ui_locales` in `SigninRedirectArgs`.
- **How Zitadel Login v2 (v4.19.4) picks its language:**
  - `apps/login/src/i18n/request.ts` resolves `defaultLanguage` (instance: `en`), then the first `accept-language` tag, then the `NEXT_LOCALE` cookie, each filtered by `allowedLanguages`. The cookie wins.
  - `apps/login/src/lib/server/flow-initiation.ts:252-257` writes `ui_locales` into `NEXT_LOCALE`, but only when no cookie exists, unless `ZITADEL_UI_LOCALES_OVERRIDE_COOKIE=true` (`apps/login/src/lib/i18n.ts:72-74`).
  - The archived change `fix-zitadel-login-ja-i18n` (2026-06) recorded that "`ui_locales` is NOT used". That is no longer true at v4.19.4.
- **Login v2 configuration.** The Login v2 deployment reads its configuration from the `login-config-dotenv` ConfigMap (`login.customConfigmapConfig` in `cloud-provisioning/k8s/namespaces/zitadel/base/values.yaml`). The image entrypoint sources it with allexport, and container `env` cannot override it.

## Goals / Non-Goals

**Goals:**

- **One language rule** (app choice > supported browser language > English) in the fan app, the organizer console and the hosted login, with the app's choice carried across sign-in and sign-out.

**Non-Goals:**

- **Admin app.** It has no language switch. Its sign-in keeps sending no `ui_locales`, so the hosted login uses the browser language and then English.
- **Fan `<html lang>`.** The fan page always declares `lang="ja"`; only the organizer console syncs it. This is a separate accessibility gap; see Open Questions.
- **Sign-out page language.** Zitadel's end-session page is not given a language (`ui_locales` on end-session). The sign-out redirect passes through without a page the user reads.

## Decisions

### D1. Keep the fan language key instead of rewriting it on sign-out

Hydration stops removing `localStorage['language']`. The key then always holds the last applied locale:

- The detector writes it on init and on every `changeLanguage`.
- `changeLocale` also writes it explicitly after a successful `setLocale` in **both** branches. Today only the guest branch writes it. With the explicit write, persistence does not depend on a library side effect, and unit tests can assert it.

Alternative: a `SignedOut` subscriber that writes the current locale. Rejected for two reasons:

- It adds a mechanism instead of removing one.
- It is wrong for an involuntary logout at boot. That can fire before hydration has applied the account language, so it would save the tentative `navigator` locale.

Keeping the key is also why the authed boot shows the account language on first paint in the common case: the key already equals the account value.

### D2. The caller passes the language to `AuthService`

`signIn` and `signUp` gain an optional `uiLocales?: string` option, forwarded as `ui_locales` to `signinRedirect`. Each caller resolves the language it is showing:

- **Fan.** Settings Login/Sign up and `auth-status` use `I18N.getLocale()` normalized by `normalizeToSupportedLanguage`. If the Welcome page has its own Login/Sign up path, it gets the same treatment.
- **Organizer.** `auth-hook` and the unrecoverable-expiry `onUnrecoverable` in `organizer-auth-retry-interceptor` use `IConsoleLanguage.current`.

Alternatives considered:

- **`AuthService` resolves `I18N` itself.** Rejected. `AuthService` is shared by three apps, and the admin app has no i18n registration.
- **`AuthService` reads `<html lang>`.** Rejected. The fan app does not keep it in sync (see Non-Goals), so this would silently send `ja`.

### D3. `ZITADEL_UI_LOCALES_OVERRIDE_COOKIE="true"` in the Login v2 dotenv

Add the line to `login.customConfigmapConfig`. Without it, a `NEXT_LOCALE` cookie left by an earlier visit, or by the in-login selector, wins over `ui_locales`. The app's choice would then lose, which breaks the spec rule.

The cookie stays Zitadel's own. The apps never read or write it.

The setting is instance-wide, because there is one Login v2 deployment. The admin app sends no `ui_locales`, so its behavior does not change.

### D4. English fallback in both apps

- **Fan:**
  - `fallbackLng: 'en'`.
  - `normalizeToSupportedLanguage` returns `'en'` for unsupported input. This is also the value sent on `UserService.Create` and backfill.
- **Organizer:**
  - `fallbackLng: 'en'`.
  - `toConsoleLocale` maps anything that is not Japanese to `'en'`, i.e. `startsWith('ja') ? 'ja' : 'en'`.
  - `ConsoleLanguage.current` initial value becomes `'en'`.

This matches Zitadel's instance `defaultLanguage = en`, so a browser in an unsupported language sees one language end to end.

## Risks / Trade-offs

- **Devices that already lost the key.** On devices where hydration already removed the key, the first guest open after this deploy still detects from `navigator`, once. → Accepted, see the REMOVED requirement's Migration. A signed-in boot after the deploy rewrites the key from the account value, so the next sign-out is already correct.
- **Stale key from another device.** A key written on one device can briefly disagree with an account language changed on another device: one tentative-locale flash, then hydration applies the account value and the key follows. → Same as today's "Brief locale flicker" scenario. No new behavior.
- **The in-login selector is overridden on the next login.** With the override on, a user who picks a language in the in-login selector sees it overridden by the app's language on the next login. → Intended by the rule. The app's language switch is the place to change it.
- **Accounts created from unsupported browser languages.** New accounts from unsupported browser languages are created with `en` instead of `ja`. Existing rows are untouched. → Only the owner and one tester use prod; both use Japanese browsers.

## Migration Plan

1. **cloud-provisioning PR** (D3). It merges independently. With no `ui_locales` sent yet, the setting has no effect.
2. **frontend PR** (D1, D2, D4). One PR. Prod deploy follows the normal frontend release.
3. **Verify in prod** (the dev environment is stopped), on a browser whose first language is English:
   - choose Japanese on Welcome, then Login: the hosted login is in Japanese;
   - sign in, reload, sign out: Welcome is in Japanese;
   - same on the organizer console.

Rollback: revert either PR. The two are independent. Without the frontend change the Zitadel setting is a no-op, and without the Zitadel setting `ui_locales` still applies whenever no cookie exists.

## Open Questions

- **Fan `<html lang>`.** Should the fan page sync `<html lang>` like the organizer console does? It does not affect this change's rule, so it is left for a separate change if wanted.
