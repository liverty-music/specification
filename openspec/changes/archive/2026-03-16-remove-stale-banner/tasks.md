## 1. ViewModel cleanup

- [x] 1.1 Remove `isStale` property from `dashboard.ts`
- [x] 1.2 Remove `retry()` method from `dashboard.ts`
- [x] 1.3 Simplify `loadData()` catch block: when `dateGroups.length > 0`, log the error and return (do not set isStale, do not re-throw)

## 2. Template cleanup

- [x] 2.1 Remove the stale banner `<aside>` block from `dashboard.html`
- [x] 2.2 Remove the `if.bind="!isStale"` condition from `<inline-error>` in catch block
- [x] 2.3 Remove the stale `<live-highway>` branch (`if.bind="isStale"`) from catch block

## 3. Styles cleanup

- [x] 3.1 Remove all stale banner CSS (`.dashboard-stale-banner`, `.dashboard-stale-icon`, `.dashboard-stale-retry`, `--_stale-*` custom properties) from `dashboard.css`

## 4. i18n cleanup

- [x] 4.1 Remove `dashboard.stale.*` keys from `en/translation.json`
- [x] 4.2 Remove `dashboard.stale.*` keys from `ja/translation.json`

## 5. Tests

- [x] 5.1 Remove stale-related test cases from `test/routes/dashboard.spec.ts`
- [x] 5.2 Run `make check` to verify no regressions
