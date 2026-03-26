## 1. Regression Tests (test-first)

- [x] 1.1 Add unit test: `PageHelp.attached()` auto-opens for discovery/my-artists
- [x] 1.2 Add unit test: `PageHelp.attached()` does NOT auto-open for dashboard
- [x] 1.3 Add unit test: `DashboardRoute.loading()` does NOT set `showCelebration=true` prematurely
- [x] 1.4 Add unit test: `DashboardRoute.attached()` calls `startLaneIntro()` when step is DASHBOARD (not blocked by celebration)
- [x] 1.5 Add unit test: `completeLaneIntro()` sets `showCelebration=true` after AWAY phase
- [x] 1.6 Run tests to confirm they fail against current code

## 2. Fix PageHelp auto-open

- [x] 2.1 Add auto-open allowlist (`['discovery', 'my-artists']`) to `PageHelp.attached()` — dashboard excluded
- [x] 2.2 Update tests to reflect allowlist approach (no `suppress` bindable)

## 3. Fix Dashboard orchestration order

- [x] 3.1 Remove `showCelebration = true` from `loading()` — celebration is set only by `completeLaneIntro()`
- [x] 3.2 Update `attached()` to always call `startLaneIntro()` when step is DASHBOARD (remove `!showCelebration` guard)
- [x] 3.3 Move `celebrationShown = true` from `loading()` to `completeLaneIntro()`
- [x] 3.4 Verify `onCelebrationDismissed()` does not need changes

## 4. Unify page-help placement inside `<page-header>`

- [x] 4.1 Add `<page-header>` + `<page-help>` to dashboard-route.html (inside header, before stage-header)
- [x] 4.2 Add `<page-header>` + `<page-help>` to discovery-route.html (above search bar)
- [x] 4.3 Verify my-artists already correct — no changes needed

## 5. Verify all fixes

- [x] 5.1 Run `make check` to confirm all regression tests pass (829 tests, 0 failures)
- [x] 5.2 Run `make lint` to confirm no linting issues (pre-existing `lint-no-div-role-status` in celebration-overlay only)
