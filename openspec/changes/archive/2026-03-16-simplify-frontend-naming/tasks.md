## Tasks

- [x] **Task 1: Move and rename route files** — Move all route components to consistent `routes/<name>/<name>-route.*` structure and rename classes (`WelcomePage` → `WelcomeRoute`, etc.)
- [x] **Task 2: Update app-shell.ts route imports** — Update all `component: import(...)` paths and the `fallback` path to point to new file locations.
- [x] **Task 3: Unify `discover` → `discovery` in code references** — onboarding-service, bottom-nav-bar, svg-icon, dashboard-route, my-artists-route, welcome-route, bubble-pool
- [x] **Task 4: Merge i18n namespaces** — Merge `"discover"` keys into `"discovery"` in both locales, delete old namespace, update `nav.discover` → `nav.discovery`
- [x] **Task 5: Update i18n key references in code** — Replace `discover.*` i18n keys with `discovery.*` in route templates and TypeScript files
- [x] **Task 6: Update test files** — Update imports and class references in unit and E2E test files
- [x] **Task 7: Verify build and lint** — `make check` passes (lint, typecheck, 574 unit tests)
