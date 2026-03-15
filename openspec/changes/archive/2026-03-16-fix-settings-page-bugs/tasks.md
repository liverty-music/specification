# Tasks

## frontend

- [x] Add `translationKey(code: string): string` to `iso3166.ts` that returns `entry.key` for an ISO code
- [x] In `settings-page.ts`, replace `shortDisplayName(code)` with `translationKey(code)` in both `loading()` and `onHomeSelected()`
- [x] Remove `shortDisplayName` import from `settings-page.ts`; delete the function from `iso3166.ts` if no other consumers exist
- [x] Replace `cycleLanguage()` with a language selector UI (bottom sheet or inline list)
- [x] Update `settings-page.html` language row to open the selector instead of calling `cycleLanguage()`
- [x] Update unit tests for settings page
