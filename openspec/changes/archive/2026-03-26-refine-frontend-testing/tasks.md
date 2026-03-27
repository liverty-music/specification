## 1. Critical infrastructure fixes

- [x] 1.1 Fix `test/setup.ts` afterEach: Replace `fixtures.forEach(async (f) => ...)` with `await Promise.all(fixtures.map(f => f.stop(true).catch(() => {})))` — the forEach+async pattern silently drops Promises
- [x] 1.2 Fix `test/smoke/component-compile.spec.ts`: Replace deprecated `tearDown()` with `stop(true)`
- [x] 1.3 Remove dead `"src/*-page.ts"` exclusion pattern from `vitest.config.ts` (matches no files)

## 2. Test isolation fixes (afterEach hygiene)

- [x] 2.1 Add `localStorage.clear()` to afterEach in `test/services/pwa-install-service.spec.ts`
- [x] 2.2 Add `localStorage.clear()` to afterEach in `test/components/notification-prompt.spec.ts`
- [x] 2.3 Move `vi.useRealTimers()` from `it()` blocks to `afterEach` in `test/routes/discovery-route.spec.ts` (already correct — skipped)
- [x] 2.4 Move `vi.useRealTimers()` from `it()` blocks to `afterEach` in `test/routes/my-artists-route.spec.ts` (already correct — skipped)
- [x] 2.5 Move `vi.useRealTimers()` from `it()` blocks to `afterEach` in `test/services/connect-error-router.spec.ts` (already correct — skipped)
- [x] 2.6 Move `vi.useRealTimers()` from `it()` blocks to `afterEach` in `test/components/dna-orb-canvas.spec.ts` (already correct — skipped)
- [x] 2.7 Move `vi.useRealTimers()` from `it()` blocks to `afterEach` in `test/value-converters/date.spec.ts` (already correct — skipped)

## 3. Mock helper type safety improvements

- [x] 3.1 Add explicit `Partial<I18N>` return type to `test/helpers/mock-i18n.ts` (already typed — skipped)
- [x] 3.2 Add explicit typed return to `test/helpers/mock-toast.ts` (already typed — skipped)
- [x] 3.3 Fix `test/helpers/mock-error-boundary.ts`: Properly type `currentError` and `errorHistory` properties (already typed — skipped)

## 4. Auth service refactor for testability

- [x] 4.1 Refactor `src/services/auth-service.ts` to lazy-initialize `UserManager` (move `UserManagerSettings` construction from module scope to a lazy getter)
- [x] 4.2 Remove `src/services/auth-service.ts` from vitest coverage exclusion list
- [x] 4.3 Add unit test for `AuthService` itself (test lazy init, `ready` promise, `signIn`/`signOut` delegation)
- [x] 4.4 Refactor `test/auth-service.spec.ts` to test public API instead of private members via `@ts-expect-error`

## 5. Update testing strategy documentation

- [x] 5.1 Update `docs/testing-strategy.md` Section 1 (Testing Architecture): Elevate `createFixture` to co-primary status alongside DI Unit, update the decision flow diagram per design.md Decision 1
- [x] 5.2 Update `docs/testing-strategy.md` Section 2 (Test Patterns): Add Pattern H for `createFixture` fluent builder with official assertion helpers (`assertText`, `assertAttr`, `trigger.click`, `type`, `tasksSettled`)
- [x] 5.3 Update `docs/testing-strategy.md` Section 6 (Anti-Patterns): Add entries for forEach+async cleanup, missing `tasksSettled()` after state mutation, using deprecated `tearDown()` instead of `stop(true)`, `vi.useRealTimers()` inside `it()` instead of `afterEach`
- [x] 5.4 Update `docs/testing-strategy.md` Section 8 (Key Decisions): Change `createFixture` row from "Template binding verification only" to "Co-primary for components with templates"
- [x] 5.5 Add new section to `docs/testing-strategy.md` referencing all Aurelia 2 official testing documentation pages (Overview, Testing Components, Testing Attributes, Testing Value Converters, Fluent API, Stubs Mocks & Spies, Advanced Testing Techniques, Outcome Recipes, Quick Reference, Decision Trees)

## 6. Upgrade smoke tests

- [x] 6.1 Upgrade `test/smoke/component-compile.spec.ts`: Replace `expect(true).toBe(true)` with `fixture.getBy()` / `fixture.assertAttr()` assertions for SvgIcon, StatePlaceholder, BottomNavBar
- [x] 6.2 Migrate smoke tests to fluent builder API (`createFixture.component(X).html(Y).deps(Z).build()`)
- [x] 6.3 Add additional components to the smoke test suite (expand the `components` array with more globally-registered components)

## 7. Custom attribute and value converter integration tests

- [x] 7.1 Add `createFixture` integration test for `tile-color` custom attribute using `fixture.getBy()` + `style.getPropertyValue()`
- [x] 7.2 Add `createFixture` integration test for `dot-color` custom attribute using `fixture.getBy()` + `style.getPropertyValue()`
- [x] 7.3 Add `createFixture` integration test for `DateValueConverter` using `fixture.assertText()` with `${date | date}` pipeline

## 8. Critical-path component integration tests (Phase 1)

- [x] 8.1 Create `test/components/bottom-nav-bar.fixture.spec.ts`: Test nav item rendering and active state via `createFixture` with mocked `IRouter`
- [x] 8.2 Create `test/components/snack-bar.fixture.spec.ts`: Skipped — popover API not available in JSDOM; service logic already tested in `test/services/snack-bar.spec.ts`
- [x] 8.3 Create `test/components/error-banner.spec.ts`: Test dismiss delegation, clipboard copy, GitHub issue URL, cooldown logic
- [x] 8.4 Create `test/components/concert-highway.spec.ts`: Test beam index map construction, getBeamIndex, detaching cleanup, dateGroupsChanged

## 9. Critical-path component integration tests (Phase 2)

- [x] 9.1 Create `test/routes/welcome-route.spec.ts`: Test canLoad redirect, handleGetStarted, handleLogin, detaching abort
- [x] 9.2 Create `test/components/user-home-selector.spec.ts`: Test open/close, region selection, guest vs auth persistence, quick city, getStoredHome
- [x] 9.3 Create `test/components/post-signup-dialog.spec.ts`: Test activeChanged, notification subscribe, PWA install, canInstallPwa, onDefer

## 10. Additional high-complexity component integration tests (Phase 3)

- [x] 10.1 Create `test/routes/settings-route.spec.ts`: Test loading, language selection, home selection, notification toggle, email verification resend, sign out
- [x] 10.2 Create `test/routes/import-ticket-email-route.spec.ts`: Test validation, artist matching, wizard flow, submitForParsing, sanitizeUrl, formatJourneyStatus, detaching

## 11. Coverage threshold increase

- [x] 11.1 Run `vitest --coverage` and verify new tests increase coverage above current thresholds (Stmt 68.76%, Branch 87.91%, Func 71.72%, Lines 68.76%)
- [x] 11.2 Raise coverage thresholds in `vitest.config.ts` (statements: 55->65%, functions: 54->65%, lines: 55->65%, branches: 75% maintained)
- [x] 11.3 Run `make check` to verify all linting and tests pass with new thresholds (lint-no-div-role-status is a pre-existing issue in celebration-overlay.html, unrelated to this change)
