# Fix Settings Page Bugs

**Repos:** frontend
**Type:** bugfix

## Problem

Two bugs on the Settings page (`/settings`):

### 1. Home area displays raw i18n key

The "ホームエリア" row shows `userHome.prefectures.福岡` instead of the translated prefecture name (e.g., "福岡").

**Root cause:** `currentHome` stores the Japanese display name via `shortDisplayName()` (e.g., `'福岡'`), but the i18n translation keys use romaji (e.g., `'fukuoka'`). The lookup `i18n.tr('userHome.prefectures.福岡')` fails and i18next returns the key as-is.

### 2. Language selector toggles immediately instead of showing a menu

Tapping the "言語" row instantly cycles `ja → en → ja` instead of presenting a selection UI. The chevron icon (`>`) implies a menu will open, but no menu exists.

## Solution

### Bug 1: Store i18n key instead of display name

Add a `translationKey()` function to `iso3166.ts` that maps an ISO code to its i18n key (the existing `entry.key` field). Replace `shortDisplayName()` usage in `settings-page.ts` with this function.

- `settings-page.ts` line 42: `shortDisplayName(code)` → `translationKey(code)`
- `settings-page.ts` line 55: same change
- `shortDisplayName` import removed (function itself kept if used elsewhere, deleted if unused)

### Bug 2: Replace cycle with language selection UI

Replace `cycleLanguage()` with a proper selection mechanism. Since only 2 languages exist (`ja`, `en`), a lightweight approach is appropriate:

- **Option A:** Bottom sheet (consistent with home area selector pattern)
- **Option B:** Inline radio/list within the settings card

Recommend **Option A** for consistency with existing UX patterns, but keep implementation minimal given only 2 options.

## Scope

- `frontend/src/constants/iso3166.ts` — add `translationKey()` export
- `frontend/src/routes/settings/settings-page.ts` — fix `currentHome` storage, replace `cycleLanguage()`
- `frontend/src/routes/settings/settings-page.html` — update language row to open selector
- New component or inline template for language selection UI
- Update affected tests
