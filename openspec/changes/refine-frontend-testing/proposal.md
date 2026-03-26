## Why

The frontend test suite relies almost exclusively on DI Unit tests (`createTestContainer` + method calls), leaving `@aurelia/testing`'s `createFixture` API largely unused. The Aurelia 2 official documentation recommends integration tests that verify view and view-model together via `createFixture`, with rich DOM assertion helpers (`assertText`, `assertAttr`, `trigger.click`, `getBy`, etc.). This gap means template binding bugs (typos in `.bind` expressions, broken `if.bind`/`repeat.for`, missing event wiring) can only be caught at the E2E layer, which is slow and flaky.

A comprehensive audit of existing tests revealed additional issues: a critical `forEach(async)` bug in the global test setup that silently breaks fixture cleanup, deprecated `tearDown()` calls instead of `stop(true)`, localStorage pollution between tests, `vi.useRealTimers()` placed inside `it()` blocks instead of `afterEach`, and untyped mock helpers. These issues compound the risk of flaky tests and reduce reliability as the test suite grows. Additionally, `auth-service.ts` is excluded from coverage due to module-level `window.location` access, and a dead vitest config pattern (`src/*-page.ts`) creates confusion.

## What Changes

- **Fix critical test infrastructure bugs**: `forEach(async)` in `test/setup.ts` that silently breaks fixture cleanup; deprecated `tearDown()` → `stop(true)`
- **Adopt `createFixture`-based component integration tests** for critical-path components, using the official Aurelia testing patterns (fluent builder API, `assertText`, `trigger.click`, `tasksSettled()`)
- **Upgrade smoke tests** from tautological `expect(true).toBe(true)` to meaningful DOM assertions
- **Fix test isolation issues**: Add missing `localStorage.clear()` in `afterEach` (pwa-install-service, notification-prompt); move `vi.useRealTimers()` from `it()` blocks to `afterEach` (5 files)
- **Improve mock helper type safety**: Add proper return types to `mock-i18n.ts`, `mock-toast.ts`, `mock-error-boundary.ts`
- **Refactor `auth-service.ts`** to lazy-initialize `UserManager`, eliminating module-level `window.location` access and enabling coverage inclusion
- **Remove dead vitest config** (`src/*-page.ts` exclusion pattern that matches no files)
- **Update `docs/testing-strategy.md`** to align with Aurelia 2 official testing documentation, elevating `createFixture` from "template binding only" to a co-primary testing approach alongside DI Unit tests
- **Add missing component tests** for untested critical-path components (welcome-route, bottom-nav-bar, snack-bar, user-home-selector, post-signup-dialog, error-banner, settings-route, import-ticket-email-route)
- **Raise coverage thresholds** incrementally as new tests land (55% -> 65% target)

## Capabilities

### New Capabilities

_(none — this change refines an existing capability)_

### Modified Capabilities

- `frontend-testing`: Fix test infrastructure bugs (forEach+async cleanup, deprecated tearDown, localStorage pollution, timer leak); elevate `createFixture` integration tests to co-primary status; add coverage for untested critical-path components; improve mock type safety; remove dead config; refactor auth-service for testability; align testing strategy with Aurelia 2 official documentation

## Impact

- **frontend repo**: `test/setup.ts` (critical cleanup fix); test files in `test/`, `test/helpers/`, `test/smoke/`; `src/services/auth-service.ts` (lazy init refactor); `vitest.config.ts` (remove dead pattern, raise thresholds); `docs/testing-strategy.md` (strategy update)
- **Existing test files modified**: 7+ files for afterEach fixes (localStorage, timer cleanup, deprecated API replacement)
- **Mock helpers**: 3 files updated for type safety (`mock-i18n.ts`, `mock-toast.ts`, `mock-error-boundary.ts`)
- **No API or dependency changes**: All changes are internal to the frontend repo
- **No breaking changes**: Existing DI Unit tests remain as-is; fixture tests are additive; infrastructure fixes only correct silent bugs
- **CI**: Coverage thresholds will increase, requiring new tests to maintain green builds
