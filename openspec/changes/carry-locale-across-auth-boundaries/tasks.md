# Tasks

## 1. Hosted login (cloud-provisioning; components/infrastructure/fan/web/global/hosted-login)

- [ ] 1.1 Add `ZITADEL_UI_LOCALES_OVERRIDE_COOKIE="true"` to `login.customConfigmapConfig` in `k8s/namespaces/zitadel/base/values.yaml`, with a comment citing `apps/login/src/lib/server/flow-initiation.ts` / `apps/login/src/lib/i18n.ts` at v4.19.4 (design D3). Also note on the chart-upgrade re-check comment that this line is ours. Verify with `make` rendering (`kustomize build --enable-helm --load-restrictor=LoadRestrictionsNone`) for the prod and dev overlays: the rendered `login-config-dotenv` ConfigMap contains the line.
- [ ] 1.2 Open the cloud-provisioning PR citing this change. After merge and the prod rollout, verify by read-only checks: `kubectl get configmap` of the login dotenv in prod shows the line, and the `zitadel-api-login` Deployment rolled out (`kubectl rollout status`). Quote both outputs here.

## 2. Shared sign-in (frontend shared/)

- [ ] 2.1 Add an optional `uiLocales` option to `AuthService.signIn` and `AuthService.signUp`, forwarded as `ui_locales` to `signinRedirect` only when given (design D2). Verify with unit tests: the redirect args carry `ui_locales` when given and omit it otherwise, for both methods.

## 3. Fan app (frontend src/; components/infrastructure/fan/web/global/i18n)

- [ ] 3.1 Change the fan fallback to English: `fallbackLng: 'en'` in `src/main.ts`, and `normalizeToSupportedLanguage` returns `'en'` for unsupported input; update its doc comment (design D4). Verify with unit tests annotated `@spec` for "Fallback to English" and "New account from an unsupported browser language" (normalization result `en` is what Create receives), and update existing `change-locale` tests that expect `'ja'`.
- [ ] 3.2 Stop removing the saved language in `src/services/user-hydration-task.ts` (both the post-apply and the post-backfill `removeItem`), and drop the comments that justify the removal. Verify with unit tests annotated `@spec`:
  - "Saved language differs from the account's language": after hydration applies `ja` over a saved `en`, the key holds `ja`.
  - "Sign-out after a reload keeps the language": after hydration the key is present.
- [ ] 3.3 Make `changeLocale` write the saved language after a successful `setLocale` in the authenticated branch too, and leave it unchanged when the RPC fails (design D1). Verify with unit tests annotated `@spec` for:
  - "Switching language mid-session as an authenticated user"
  - "Authenticated caller path"
  - "Authenticated language switch RPC failure"
  - "Language switched while signed in survives sign-out"
- [ ] 3.4 Pass the current language (`normalizeToSupportedLanguage(i18n.getLocale())`) as `uiLocales` from every fan sign-in/sign-up call site: `src/routes/welcome/welcome-route.ts`, `src/routes/settings/settings-route.ts` (Login and Sign up), `src/components/auth-status.ts`. Verify with unit or fixture tests annotated `@spec` "Login from the Welcome page in Japanese" and "Sign up in English": the call carries the active locale.
- [ ] 3.5 Update the remaining fan tests that assert the key is removed during authenticated sessions (hydration, auth-callback, settings sign-out fixture), so they assert the new behavior. Verify with `make check` in frontend passing.
- [ ] 3.6 Add a Playwright test for sign-out: with a mocked authenticated session and account language `ja` on an English browser locale, run sign-out and land on Welcome. Verify that Welcome renders Japanese, annotated `@spec` "Welcome after sign-out keeps the account's language" and "Involuntary logout keeps the language". If the OIDC redirect cannot be driven in E2E, cover the post-redirect boot (key present, `navigator` English → Japanese) instead, and record the gap under this task.

## 4. Organizer console (frontend organizer/; components/infrastructure/organizer/web/global/i18n)

- [ ] 4.1 Change the organizer fallback to English: `fallbackLng: 'en'`, `toConsoleLocale` returns `'ja'` only for Japanese and `'en'` otherwise, `ConsoleLanguage.current` starts at `'en'` (design D4). Verify with unit tests annotated `@spec` "Browser in another language" (French → English, page declares English) and "First open on a Japanese browser".
- [ ] 4.2 Pass `IConsoleLanguage.current` as `uiLocales` from `organizer/hooks/auth-hook.ts` and from the `onUnrecoverable` sign-in in `organizer/services/organizer-auth-retry-interceptor.ts`. Verify with unit tests annotated `@spec` "Operator who chose Japanese on an English browser" and "Operator who chose English on a Japanese browser".

## 5. Release and production verification

- [ ] 5.1 Open the frontend PR citing this change (groups 2-4). Merge when CI is green, and confirm the prod release rolled out.
- [ ] 5.2 Verify by hand in prod on a browser whose first language is English, then record here with the date. Mark the hosted-login scenarios `@spec-manual` in design.md (Manual verification):
  - (a) Welcome → switch to 日本語 → Login: hosted login in Japanese.
  - (b) Sign in, reload, sign out: Welcome in Japanese.
  - (c) Pick English with the in-login selector, abort, return to the app in Japanese, Login again: hosted login in Japanese.
  - (d) Organizer console switched to 日本語, sign out, sign in: hosted login in Japanese.

  These cover the `components/infrastructure/fan/web/global/hosted-login` scenarios:
  - "App language wins over the browser language" (a)
  - "App language wins over a language remembered from an earlier visit" (c)
  - "No language requested" and "Unsupported browser language and no request": the admin app, or `accept-language` reasoning from the v4.19.4 source; state which
  - "App in English on a browser in another supported language"
