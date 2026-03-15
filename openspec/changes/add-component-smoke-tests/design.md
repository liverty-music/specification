## Context

Aurelia 2 compiles templates at runtime (JIT). There is no AOT compilation step or static analysis tool to catch template errors before the app runs. The existing test suite has:

- **Vitest**: Setup with `@aurelia/testing` and JSDOM (`test/setup.ts`), but zero unit/smoke tests exist under `src/`.
- **Playwright E2E**: Layout tests exist (`e2e/layout/`) but only verify bounding boxes, not rendering correctness or console errors.
- **Coverage thresholds**: Configured in `vitest.config.ts` (55% statements) but effectively untested since no test files exist.

The `bottom-nav-bar` component has had an invalid `<template switch.bind>` since commit `d03d188` (2026-02-25) — undetected for 18 days.

## Goals / Non-Goals

**Goals:**

- Catch template compilation errors (AUR0703, etc.) in CI before they reach production.
- Cover all custom elements registered in `main.ts` with mount smoke tests.
- Catch runtime console errors on public routes via E2E smoke tests.
- Fix the two existing bugs (switch surrogate, pointer-events).

**Non-Goals:**

- Full behavioral/interaction testing of each component (future work).
- Testing route-level page components (these are lazy-loaded and have heavy DI requirements).
- Achieving high code coverage — these are compile-pass/fail tests only.

## Decisions

### D1: Vitest mount tests using `createFixture` (not `renderComponent`)

**Decision**: Use `@aurelia/testing`'s `createFixture()` to mount each component in isolation.

**Why**: `createFixture` is the recommended API for Aurelia 2 testing. It handles component registration, template compilation, and lifecycle — exactly what we need to trigger AUR0703-class errors.

**Alternative considered**: `renderComponent()` — lower-level, requires more manual setup. Not needed for compile-only smoke tests.

### D2: One test file, `describe.each` over component list

**Decision**: A single file `test/smoke/component-compile.spec.ts` with a data-driven loop over all components.

**Why**: Adding a new component only requires adding one entry to an array. Minimizes boilerplate. Each component gets its own test case name for clear failure reporting.

**Alternative considered**: One test file per component — too much overhead for smoke tests that only verify compilation.

### D3: DI stubs via inline shared registrations

**Decision**: Define a `sharedRegistrations` array inline in `test/smoke/component-compile.spec.ts`, reusing existing mock factories from `test/helpers/` (`createMockRouter`, `createMockI18n`, `createMockErrorBoundary`).

**Why**: Most components `resolve()` DI tokens. Without stubs, `createFixture` throws missing-registration errors before reaching template compilation. The stubs need to satisfy the type shape but don't need real behavior. A separate `mock-registry.ts` file was unnecessary since the existing `test/helpers/` mocks already provide the required stubs.

**Alternative considered**: Separate `test/smoke/mock-registry.ts` — unnecessary indirection when `test/helpers/` mocks already exist and the registration array is small.

### D4: Exclude `dna-orb` from mount tests

**Decision**: Skip `dna-orb` component (Canvas + Matter.js physics). Already excluded from coverage in `vitest.config.ts`.

**Why**: Requires `HTMLCanvasElement.getContext()` which JSDOM does not support. Would need `jest-canvas-mock` or similar — not worth the complexity for a smoke test.

### D5: E2E console-error test for public routes only

**Decision**: Playwright test navigates to public routes (`/`, `/welcome`, `/about`, `/discover`) and asserts zero `console.error` messages.

**Why**: Public routes don't require auth state setup. Catches runtime errors (including template compilation) in a real browser. Authenticated routes are out of scope — they need auth storage state which is a separate concern.

### D6: `bottom-nav-bar` fix — use `<span>` as switch host

**Decision**: Replace `<template switch.bind="tab.icon">` with `<span switch.bind="tab.icon">`.

**Why**: `<span>` is inline, doesn't break the `<a>` element's content model (unlike `<div>` which is block-level inside `<a>` in flow content). The `<span>` acts as an invisible wrapper — add `display: contents` in CSS so it doesn't affect layout.

**Alternative considered**: `<div>` — valid in Aurelia but semantically wrong inside `<a>` with inline content.

## Risks / Trade-offs

**[Risk] DI mock drift** — Mock registry could become stale as services evolve.
→ Mitigation: Smoke tests fail fast when a new DI token is missing, prompting an update. Keep mocks minimal (empty objects with required properties).

**[Risk] JSDOM limitations** — Some components may use browser APIs not available in JSDOM (beyond canvas).
→ Mitigation: Skip those components with a documented reason. The E2E smoke test provides a second safety net in a real browser.

**[Risk] False sense of security** — Smoke tests only verify compilation, not behavior.
→ Mitigation: Document clearly that these are compile-only tests. Behavioral tests are a separate initiative.
