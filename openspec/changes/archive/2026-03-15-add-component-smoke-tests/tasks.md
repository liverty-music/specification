## 1. Bug Fixes

- [x] 1.1 Fix `bottom-nav-bar.html`: already resolved by commit 779e579 (replaced inline SVGs with `<svg-icon>` component)
- [x] 1.2 Fix `error-banner.css`: add `pointer-events: auto` to `.error-dialog` rule
- [x] 1.3 Fix `svg-icon.html`: replace root `<template switch.bind>` (surrogate) with `<span switch.bind>` + `display: contents` — same AUR0703 bug moved here by commit 779e579

## 2. DI Mock Registry

- [x] 2.1 Reuse existing `test/helpers/` mocks (mock-router, mock-i18n, mock-logger, mock-error-boundary) — no separate mock-registry needed

## 3. Component Mount Smoke Tests

- [x] 3.1 Create `test/smoke/component-compile.spec.ts` with `it.each` loop over all globally-registered custom elements from `main.ts`
- [x] 3.2 Verify each component mounts via `createFixture()` without throwing
- [x] 3.3 Document excluded components (dna-orb: JSDOM lacks canvas support) in the test file

## 4. E2E Console Error Smoke Test

- [x] 4.1 Create `e2e/smoke/no-console-errors.spec.ts` that navigates to public routes (`/`, `/welcome`, `/about`, `/discover`)
- [x] 4.2 Assert zero `console.error` messages per route, excluding network errors

## 5. Verification

- [x] 5.1 Run `npx vitest run` — all smoke tests pass (4/4). 3 pre-existing failures in unrelated tests (missing BSR-generated `follow_pb.js`)
- [x] 5.2 Run `npx playwright test --project=smoke` — all 4 E2E smoke tests pass
