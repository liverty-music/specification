## Why

The dashboard displays a "stale data" warning banner when an API reload fails but previous concert data exists. However, concert information is inherently stable — once published, event details rarely change. The banner unnecessarily alarms users by implying their data may be outdated when it is effectively still accurate. Silently showing cached data is the correct UX for this domain.

## What Changes

- Remove the stale data warning banner from the dashboard UI (template, styles, logic)
- Remove the `isStale` state and `retry()` method from the Dashboard ViewModel
- Remove stale-related i18n keys from locale files
- Simplify the error/catch template branch: when previous data exists and a reload fails, show previous data silently without any warning

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `typography-focused-dashboard`: Remove the stale data warning banner requirement from the "Three-Lane Live Highway Layout" requirement

## Impact

- `frontend/src/routes/dashboard.ts` — remove `isStale`, `retry()`, simplify `loadData()` catch
- `frontend/src/routes/dashboard.html` — remove stale banner markup, simplify catch template
- `frontend/src/routes/dashboard.css` — remove stale banner styles
- `frontend/src/locales/en/translation.json` — remove `dashboard.stale.*` keys
- `frontend/src/locales/ja/translation.json` — remove `dashboard.stale.*` keys
- `frontend/test/routes/dashboard.spec.ts` — remove stale-related test cases
