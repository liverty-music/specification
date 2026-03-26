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

- [ ] 5.1 Update `docs/testing-strategy.md` Section 1 (Testing Architecture): Elevate `createFixture` to co-primary status alongside DI Unit, update the decision flow diagram per design.md Decision 1
- [ ] 5.2 Update `docs/testing-strategy.md` Section 2 (Test Patterns): Add Pattern H for `createFixture` fluent builder with official assertion helpers (`assertText`, `assertAttr`, `trigger.click`, `type`, `tasksSettled`)
- [ ] 5.3 Update `docs/testing-strategy.md` Section 6 (Anti-Patterns): Add entries for forEach+async cleanup, missing `tasksSettled()` after state mutation, using deprecated `tearDown()` instead of `stop(true)`, `vi.useRealTimers()` inside `it()` instead of `afterEach`
- [ ] 5.4 Update `docs/testing-strategy.md` Section 8 (Key Decisions): Change `createFixture` row from "Template binding verification only" to "Co-primary for components with templates"
- [ ] 5.5 Add new section to `docs/testing-strategy.md` referencing all Aurelia 2 official testing documentation pages (Overview, Testing Components, Testing Attributes, Testing Value Converters, Fluent API, Stubs Mocks & Spies, Advanced Testing Techniques, Outcome Recipes, Quick Reference, Decision Trees)

## 6. Upgrade smoke tests

- [ ] 6.1 Upgrade `test/smoke/component-compile.spec.ts`: Replace `expect(true).toBe(true)` with `fixture.getBy()` / `fixture.assertAttr()` assertions for SvgIcon, StatePlaceholder, BottomNavBar
- [ ] 6.2 Migrate smoke tests to fluent builder API (`createFixture.component(X).html(Y).deps(Z).build()`)
- [ ] 6.3 Add additional components to the smoke test suite (expand the `components` array with more globally-registered components)

## 7. Custom attribute and value converter integration tests

- [ ] 7.1 Add `createFixture` integration test for `tile-color` custom attribute using `fixture.assertStyles()`
- [ ] 7.2 Add `createFixture` integration test for `dot-color` custom attribute using `fixture.assertStyles()`
- [ ] 7.3 Add `createFixture` integration test for `DateValueConverter` using `fixture.assertText()` with `${date | dateFormat}` pipeline

## 8. Critical-path component integration tests (Phase 1)

- [ ] 8.1 Create `test/components/bottom-nav-bar.fixture.spec.ts`: Test nav item rendering and active state via `createFixture` with mocked `IRouter`
- [ ] 8.2 Create `test/components/snack-bar.fixture.spec.ts`: Test toast display, auto-dismiss (fake timers + `tasksSettled`), and action callback via `fixture.trigger.click()`
- [ ] 8.3 Create `test/components/error-banner.fixture.spec.ts`: Test error display, dismiss interaction via `fixture.trigger.click()`, and GitHub issue URL rendering
- [ ] 8.4 Create `test/components/concert-highway.spec.ts`: Test ConcertHighway CE — dateGroups rendering, beam index map construction from matched events, readonly mode, detaching cleanup (scroll listener removal, rAF cancellation)

## 9. Critical-path component integration tests (Phase 2)

- [ ] 9.1 Create `test/routes/welcome-route.fixture.spec.ts`: Test rendered DOM for unauthenticated user (sign-in/sign-up CTAs), canLoad redirect, preview concert data loading via ConcertService, language switching via @observable currentLocale
- [ ] 9.2 Create `test/components/user-home-selector.fixture.spec.ts`: Test region option rendering, selection interaction via `fixture.trigger.click()`, and service call verification
- [ ] 9.3 Create `test/components/post-signup-dialog.fixture.spec.ts`: Test multi-step flow rendering (notification prompt -> PWA install), step advancement via `fixture.trigger.click()`

## 10. Additional high-complexity component integration tests (Phase 3)

- [ ] 10.1 Create `test/routes/settings-route.fixture.spec.ts`: Test language option rendering (repeat.for), email verification conditional, PWA install section visibility
- [ ] 10.2 Create `test/routes/import-ticket-email-route.fixture.spec.ts`: Test multi-step wizard rendering, step advancement, input form presence

## 11. Coverage threshold increase

- [ ] 11.1 Run `vitest --coverage` and verify new tests increase coverage above current thresholds
- [ ] 11.2 Raise coverage thresholds in `vitest.config.ts` (statements: 55->65%, functions: 54->65%, lines: 55->65%, branches: 75% maintained)
- [ ] 11.3 Run `make check` to verify all linting and tests pass with new thresholds
