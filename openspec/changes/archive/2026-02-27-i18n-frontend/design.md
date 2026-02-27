## Context

The Liverty Music frontend (Aurelia 2 + Vite + TailwindCSS v4) hardcodes all UI text in Japanese across ~20 files. There is no internationalization infrastructure. The app needs JA + EN bilingual support with locale detection and a user-facing language switcher.

Aurelia 2 provides an official i18n package (`@aurelia/i18n`) built on top of i18next, which was selected after evaluating FormatJS/ICU MessageFormat (no Aurelia plugin, TC39 proposal stuck at Stage 1) and a custom DIY approach (insufficient for future scaling).

## Goals / Non-Goals

**Goals:**
- Establish i18n infrastructure using `@aurelia/i18n` + i18next
- Extract all hardcoded Japanese strings into structured translation files
- Support JA and EN with automatic locale detection (`navigator.language`) and `?lang=` URL param override
- Make `DateValueConverter` and `Intl` formatting locale-aware
- Add language preference to the Settings page
- Persist language preference in localStorage

**Non-Goals:**
- Server-side locale management or backend changes
- SEO-oriented URL path localization (e.g., `/en/dashboard`)
- Right-to-left (RTL) layout support
- Translation management platform integration (e.g., Crowdin, Lokalise)
- Localizing prefecture/city names beyond simple EN equivalents (Tokyo, Osaka, etc.)

## Decisions

### 1. Library: `@aurelia/i18n` wrapping i18next

**Rationale**: Official Aurelia 2 plugin providing `t` attribute binding, `t` ValueConverter, and `I18N` injectable service. Eliminates custom ValueConverter/binding code. i18next's plugin ecosystem (language detection, HTTP backend) is available through configuration.

**Alternatives considered**:
- FormatJS/intl-messageformat: No Aurelia 2 plugin; requires custom ValueConverter, binding, and detection code. ICU MessageFormat's advanced plural rules are unnecessary for JA+EN.
- Custom DIY layer: Low initial effort but accumulates tech debt as features (interpolation, pluralization, namespacing) are needed.

### 2. Translation file structure: flat JSON, namespaced by page

```
src/locales/
├── ja/
│   └── translation.json
└── en/
    └── translation.json
```

Key naming convention: `<page>.<component>.<element>` (e.g., `welcome.hero.title`, `settings.language.label`).

**Rationale**: Single file per locale keeps things simple for 2 languages. Namespace-by-page convention makes keys discoverable and avoids collisions. Can split into multiple namespace files later via i18next namespaces if files grow large.

**Alternatives considered**:
- One JSON file per page per locale: Over-fragmented for the current ~24 string locations. Can migrate to this later with i18next's `ns` option if translation files exceed ~500 keys.

### 3. Locale detection priority

1. `?lang=` URL query parameter (highest priority)
2. localStorage `language` key (user's explicit choice from Settings)
3. `navigator.language` (browser default)
4. Fallback: `ja` (app's original language)

**Rationale**: URL param enables sharing links in a specific language and debugging. localStorage persists the user's explicit choice. Browser detection provides a reasonable default for first-time visitors.

### 4. Template migration strategy

Replace hardcoded strings using Aurelia 2's `t` attribute binding:

```html
<!-- Before -->
<h1>大好きなあのバンドのライブ、もう二度と見逃さない。</h1>

<!-- After -->
<h1 t="welcome.hero.title"></h1>
```

For TypeScript strings (error messages, toast notifications), inject the `I18N` service:

```typescript
// Before
this.toast.show('ログインが必要です');

// After
this.toast.show(this.i18n.tr('auth.loginRequired'));
```

**Rationale**: `t` attribute is the idiomatic Aurelia 2 pattern per `@aurelia/i18n` docs. It automatically re-renders when locale changes.

### 5. Date/number formatting: use Aurelia i18n's `df` and `nf` ValueConverters

Replace the custom `DateValueConverter` (hardcoded `ja-JP`) with `@aurelia/i18n`'s built-in `df` (date format) and `nf` (number format) ValueConverters, which automatically use the active locale.

**Rationale**: Avoids maintaining a custom converter. `@aurelia/i18n` delegates to `Intl.DateTimeFormat` with the current i18next language, so formatting stays consistent with the selected locale.

### 6. Language switcher placement: Settings page

Add a "Language" row to the Settings page with a select/dialog showing available languages (日本語, English). Changing the language updates localStorage and triggers i18next's `changeLanguage()`, which re-renders all `t`-bound elements.

**Rationale**: Settings is the natural home for preferences. No need for a persistent language toggle in the header/nav — 2 languages doesn't justify the UI real estate.

## Risks / Trade-offs

- **String extraction completeness**: Hardcoded strings are scattered across ~20 files including dynamic strings in TypeScript. Risk of missing strings.
  → Mitigation: Use `i18next-parser` to scan source files and detect untranslated keys. Run as a CI check.

- **Test breakage**: Existing tests assert against Japanese string output (e.g., `expect(formatted).toMatch(/3月/)`).
  → Mitigation: Update tests to either set a fixed locale or assert on translation keys rather than rendered text.

- **Bundle size increase**: `@aurelia/i18n` + i18next adds ~15-20KB gzipped.
  → Acceptable for the functionality gained. Both locale files are small (~2-5KB each for 24+ keys).

- **Reactivity on language change**: All rendered strings must update when the user switches language mid-session.
  → `@aurelia/i18n`'s `t` binding handles this automatically. `I18N.tr()` calls in imperative code need manual re-trigger (e.g., re-render toast messages).
