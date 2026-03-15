## Why

A critical AUR0703 template compilation error (`switch` on surrogate `<template>`) shipped to production undetected because no test verifies that Aurelia 2 component templates compile successfully. Aurelia 2 uses JIT compilation — template errors only surface at runtime. Without mount-level tests, any template syntax mistake becomes a production incident.

## What Changes

- Add a Vitest smoke test suite that mounts every Aurelia 2 custom element via `@aurelia/testing`, verifying template compilation succeeds without error.
- Add a Playwright E2E smoke test that navigates to each public route and asserts zero console errors.
- Fix the two bugs discovered during investigation:
  - `bottom-nav-bar.html`: Replace `<template switch.bind>` (invalid surrogate + template controller) with a valid host element.
  - `error-banner.css`: Add `pointer-events: auto` to `.error-dialog` to override the inherited `pointer-events: none` from `my-app.css`.

## Capabilities

### New Capabilities

- `component-smoke-tests`: Vitest mount tests that verify all custom element templates compile without AUR0703-class errors. Playwright console-error smoke tests for public routes.

### Modified Capabilities

- `frontend-error-handling`: Fix error dialog pointer-events so buttons respond to taps.

## Impact

- **frontend/test/**: New smoke test files using `@aurelia/testing` and `createFixture`.
- **frontend/e2e/**: New console-error smoke spec.
- **frontend/src/components/bottom-nav-bar/**: Template fix (`<template>` → valid element for `switch.bind`).
- **frontend/src/components/error-banner/**: CSS fix for dialog pointer-events.
- **CI**: Smoke tests run as part of existing `make test` / `make test:e2e` pipelines — no new CI jobs needed.
