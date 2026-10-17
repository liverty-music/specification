## Why

A language the user chose in the app is lost each time they cross a sign-in or sign-out, and the user then sees the browser's language instead:

- **Signing out of the fan app.** The fan app switches from Japanese to English on the Welcome page after sign-out. Hydration of a signed-in session removes `localStorage['language']`. The OIDC sign-out redirect reloads the app, and the detector then falls back to `navigator` (`en-US` on an English-first browser).
- **Opening the hosted login (Zitadel Login v2).** Hosted login opens in English for a user who chose Japanese in the app. Neither the fan app nor the organizer console sends OIDC `ui_locales`, so Login v2 uses `accept-language`, or a `NEXT_LOCALE` cookie that a past visit may have left behind.

Separately, the fan app and the organizer console fall back to Japanese for a browser language they do not support. Zitadel falls back to English, so a French browser sees Japanese in the app and English on the login screen.

## What Changes

- One language rule, applied the same way in the fan app, the organizer console and the hosted login: **the language chosen in the app > the browser language (when supported: `ja`, `en`) > English**.
- **Fan app: keep the language across sign-out.** `localStorage['language']` is kept and always holds the language last applied, in every auth state. Hydration no longer removes it. While signed in, the account's `preferredLanguage` still wins over it as soon as hydration resolves. **BREAKING (spec):** this replaces the requirement "Remove Legacy localStorage Language Key After Authenticated Session Begins".
- **Fan app and organizer console: send the language to hosted login.** Every sign-in and sign-up redirect sends the language shown in the app as OIDC `ui_locales`. This covers fan Login/Sign up, organizer sign-in, and forced re-authentication.
- **Hosted login: let `ui_locales` win over an old cookie.** The Login v2 deployment sets `ZITADEL_UI_LOCALES_OVERRIDE_COOKIE=true`. Without it, an existing `NEXT_LOCALE` cookie wins over `ui_locales`.
- **Fan app: the page declares the language shown.** The fan page always declares `lang="ja"` today, whatever it shows. It now follows the shown language, as the organizer console already does.
- **Fallback changes from Japanese to English** in the fan app and the organizer console. **BREAKING (visible):** a first visit from an unsupported browser language (e.g. French) now shows English instead of Japanese. Browsers set to Japanese or English are not affected. This also changes the language stored on accounts created from such a browser.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `components/infrastructure/fan/web/global/i18n`:
  - "Locale Detection" is replaced by "Language Chosen on First Open": the three-step rule with an English fallback.
  - "Locale Sourced from Backend User Entity for Authenticated Sessions" is replaced by "Account Language Wins While Signed In".
  - "Remove Legacy localStorage Language Key After Authenticated Session Begins" is removed. New requirement: "Language Kept Across Sign-in and Sign-out".
  - "Language Switching" no longer forbids the authenticated switch from updating the saved language.
  - New requirement: "Hosted Login Opens in the App's Language".
  - New requirement: "Page Declares the Language Shown".
- `components/infrastructure/organizer/web/global/i18n`:
  - The first-open fallback becomes English.
  - New requirement: hosted login opens in the console's language.
- `components/infrastructure/fan/web/global/hosted-login`: Localize Login UI Text gains `ui_locales` precedence over the browser and an old language cookie.

No entity, usecase or adapter changes. `User.preferredLanguage` and `UserService.SetPreferredLanguage` keep their contract; only the value a new account gets from an unsupported browser language changes (`en` instead of `ja`).

## Impact

- **frontend**
  - `shared/services/auth-service.ts`: `signIn`/`signUp` accept and forward `ui_locales`.
  - Fan:
    - `src/main.ts`: `fallbackLng`, and keeping `<html lang>` in sync.
    - `src/util/change-locale.ts`: `normalizeToSupportedLanguage` fallback.
    - `src/services/user-hydration-task.ts`: stop removing the key.
    - Sign-in/sign-up call sites: `src/routes/settings/settings-route.ts`, `src/components/auth-status.ts`.
  - Organizer:
    - `organizer/i18n/console-language.ts`: `fallbackLng`, `toConsoleLocale`, `ConsoleLanguage.current` default.
    - Sign-in call sites: `organizer/hooks/auth-hook.ts`, `organizer/services/organizer-auth-retry-interceptor.ts`.
  - Related unit tests.
- **cloud-provisioning**: `k8s/namespaces/zitadel/base/values.yaml`, `login.customConfigmapConfig`: add `ZITADEL_UI_LOCALES_OVERRIDE_COOKIE="true"`. This applies to the one shared Login v2 deployment, which also serves the admin app's login.
- **backend**: none.
