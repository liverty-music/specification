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

Implementation note: the two places that apply the account's language after sign-in (`user-hydration-task.ts` at boot, `auth-callback-route.ts` mid-session) also write the key explicitly after a successful `setLocale`, for the same reason as `changeLocale`.

### D2. The caller passes the language to `AuthService`

`signIn` and `signUp` gain an optional `uiLocales?: string` option, forwarded as `ui_locales` to `signinRedirect`. Each caller resolves the language it is showing:

- **Fan.** Settings Login/Sign up and `auth-status` use `I18N.getLocale()` normalized by `normalizeToSupportedLanguage`. If the Welcome page has its own Login/Sign up path, it gets the same treatment.
- **Organizer.** `auth-hook` and the unrecoverable-expiry `onUnrecoverable` in `organizer-auth-retry-interceptor` use `IConsoleLanguage.current`.

Implementation note: "every redirect" also covers the fan sign-ups on Event, My Artists and Dashboard, and the organizer's wrong-organization re-auth (`org-enforcement.ts`) and callback state-miss retry. The fan call sites use `currentLanguage(i18n)` (`src/util/change-locale.ts`). The organizer transport factory takes `IConsoleLanguage` as a parameter, so the retry interceptor reads `current` when the sign-in starts.

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

### D5. Fan `<html lang>` follows the shown language

The fan page hard-codes `<html lang="ja">` in `index.html`. Nothing updates it, so an English page declares Japanese.

Fix it the way the organizer console does (`syncDocumentLanguage` in `organizer/i18n/console-language.ts`): an activating `AppTask` in the fan app does three things:

- awaits `i18n.initPromise`;
- sets `document.documentElement.lang` to `normalizeToSupportedLanguage(i18n.getLocale())`;
- re-applies it on `Signals.I18N_EA_CHANNEL`.

The channel fires after every `setLocale`: a guest switch, hydration applying the account language, and a Settings switch. One subscriber therefore covers every path.

The static `lang="ja"` in `index.html` stays as the pre-boot value. Changing it to `en` would make the pre-boot page declare English on a Japanese browser.

Alternative: set `lang` inside `changeLocale` and the hydration task. Rejected: that is two call sites to keep in sync instead of one subscriber, and it would miss the initial detection.

Implementation note: the fan's i18n options moved from `src/main.ts` into `FanI18nConfiguration` (`src/lib/i18n/fan-i18n-configuration.ts`), which also registers this `AppTask`, mirroring the organizer's `ConsoleI18nConfiguration`, so unit tests boot the real configuration.

Also outside the language rule: `shared/ui/circular-progress` reads `<html lang>`, so in the fan app it now follows the shown language too.

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
   - same on the organizer console;
   - DevTools shows `<html lang>` following the shown language on the fan app.

Rollback: revert either PR. The two are independent. Without the frontend change the Zitadel setting is a no-op, and without the Zitadel setting `ui_locales` still applies whenever no cookie exists.

## Manual verification

Verified by hand in prod on 2026-10-17, on a browser whose first language is English, after cloud-provisioning#658 and frontend v1.97.2 rolled out (tasks.md 5.2, checks (a)–(d) all passed).

@spec-manual components/infrastructure/fan/web/global/hosted-login "App language wins over the browser language" -- check (a): Welcome switched to 日本語, Login → the hosted login opened in Japanese.
@spec-manual components/infrastructure/fan/web/global/hosted-login "App language wins over a language remembered from an earlier visit" -- check (c): English picked with the in-login selector, aborted, Login again from the app in Japanese → the hosted login opened in Japanese.
@spec-manual components/infrastructure/fan/web/global/hosted-login "No language requested" -- by the Login v2 v4.19.4 source, not by hand: with no `ui_locales` and no cookie, `apps/login/src/i18n/request.ts` takes the first `accept-language` tag that `allowedLanguages` contains. This change does not touch that path; the admin app follows it.
@spec-manual components/infrastructure/fan/web/global/hosted-login "Unsupported browser language and no request" -- by the same source, not by hand: an `accept-language` tag outside `allowedLanguages` falls through to the instance `defaultLanguage`, which is `en`.
@spec-manual components/infrastructure/fan/web/global/hosted-login "App in English on a browser in another supported language" -- same path as checks (a) and (c) with `ui_locales=en`: unit tests assert the fan app sends `en` when it shows English (`test/components/auth-status.spec.ts`, `test/routes/settings-route.spec.ts` "Sign up in English"), and the override flag lets it win over `accept-language` and the cookie. Not repeated by hand on a German browser.
