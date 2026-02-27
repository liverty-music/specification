## 1. i18n Infrastructure Setup

- [x] 1.1 Install `@aurelia/i18n` and `i18next-browser-languagedetector` dependencies
- [x] 1.2 Create `src/locales/ja/translation.json` and `src/locales/en/translation.json` with empty structures
- [x] 1.3 Register `@aurelia/i18n` in `main.ts` with i18next config (fallbackLng: `ja`, supportedLngs: `['ja', 'en']`, detection priority: querystring → localStorage → navigator)

## 2. Translation Key Extraction — Templates

- [x] 2.1 Extract welcome page strings (`welcome-page.html`) into translation keys and replace with `t` bindings
- [x] 2.2 Extract signup modal strings (`signup-modal.html`, `signup-modal.ts`) into translation keys
- [x] 2.3 Extract region setup sheet strings (`region-setup-sheet.html`, `region-setup-sheet.ts`) including prefecture/city names
- [x] 2.4 Extract dashboard strings (`dashboard.html`) including coach-mark messages
- [x] 2.5 Extract my-artists page strings (`my-artists-page.html`) including coach-mark and notification control text
- [x] 2.6 Extract loading sequence strings (`loading-sequence.ts`)
- [x] 2.7 Extract settings page strings (`settings/`) into translation keys
- [x] 2.8 Extract bottom nav bar labels and any remaining component strings

## 3. Translation Key Extraction — TypeScript

- [x] 3.1 Inject `I18N` service into `auth-hook.ts` and replace hardcoded toast messages with `i18n.tr()` calls
- [x] 3.2 Inject `I18N` service into `welcome-page.ts` and replace error message strings
- [x] 3.3 Inject `I18N` service into `signup-modal.ts` and replace error message strings
- [x] 3.4 Audit all remaining `.ts` files for hardcoded user-facing strings and externalize

## 4. Date and Number Formatting

- [x] 4.1 Replace `DateValueConverter` (hardcoded `ja-JP`) with `@aurelia/i18n`'s locale-aware `df` ValueConverter or refactor to use the active i18next locale
- [x] 4.2 Update `Intl.RelativeTimeFormat` usage to use active locale instead of hardcoded `ja-JP`

## 5. Language Switcher UI

- [x] 5.1 Add "Language" row to the Settings page displaying the current language name
- [x] 5.2 Implement language selection dialog/sheet with options: 日本語, English
- [x] 5.3 Wire selection to `I18N.setLocale()` and persist choice in localStorage `language` key

## 6. English Translations

- [x] 6.1 Write all EN translations in `src/locales/en/translation.json` for welcome, signup, region-setup, dashboard, my-artists, loading, settings, auth, and navigation keys

## 7. Testing and Verification

- [x] 7.1 Update existing tests that assert against Japanese text to be locale-aware or use translation keys
- [x] 7.2 Verify language switching works end-to-end: Settings → change language → all UI updates without reload
- [x] 7.3 Verify `?lang=en` URL parameter correctly overrides the detected locale
- [x] 7.4 Verify fallback behavior when localStorage and URL param are absent (browser detection → JA fallback)
