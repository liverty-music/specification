## Why

The Liverty Music frontend currently hardcodes all UI text in Japanese across 24+ locations (templates, TypeScript files, value converters). To expand the user base beyond Japan, the app needs internationalization support. The initial target is Japanese (JA) + English (EN) bilingual support using `@aurelia/i18n` (wraps i18next), chosen for its official Aurelia 2 integration, mature ecosystem (parser, language detection, lazy loading), and minimal custom code requirement.

## What Changes

- Install `@aurelia/i18n` and configure i18next in the Aurelia 2 DI container
- Create translation resource files (`locales/ja/translation.json`, `locales/en/translation.json`)
- Extract all hardcoded Japanese strings from templates and TypeScript into translation keys
- Replace hardcoded strings with `t` binding attributes and `I18N.tr()` calls
- Add locale detection via `navigator.language` with `?lang=` URL parameter override
- Update `DateValueConverter` to use the active locale instead of hardcoded `ja-JP`
- Add a language switcher UI in the settings page

## Capabilities

### New Capabilities
- `frontend-i18n`: Internationalization infrastructure — i18next setup, translation files, locale detection, language switching, and string extraction conventions

### Modified Capabilities
- `settings`: Add language preference selection to the settings page

## Impact

- **Frontend repo**: All template files with hardcoded Japanese text (~15 HTML files, ~5 TS files)
- **Dependencies**: New packages `@aurelia/i18n`, `i18next-browser-languagedetector`
- **Value converters**: `DateValueConverter` updated to be locale-aware
- **Testing**: Existing tests that assert Japanese text output need updating for locale-parameterized assertions
- **No backend changes**: Language preference is client-side only (localStorage + URL param)
