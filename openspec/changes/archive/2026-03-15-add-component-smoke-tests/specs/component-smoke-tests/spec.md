# Component Smoke Tests

## Purpose

Defines the smoke testing requirements that verify all Aurelia 2 custom element templates compile without errors. These tests serve as a safety net against template compilation errors (AUR0703 and similar) that are only detectable at runtime due to Aurelia 2's JIT compilation model.

## ADDED Requirements

### Requirement: Component mount smoke tests
The test suite SHALL mount every globally-registered Aurelia 2 custom element via `@aurelia/testing` `createFixture()` and verify that template compilation completes without throwing.

#### Scenario: Valid component template compiles successfully
- **WHEN** a custom element with a valid template is mounted via `createFixture()`
- **THEN** the fixture SHALL be created without errors
- **AND** the test SHALL pass

#### Scenario: Invalid template controller usage is detected
- **WHEN** a custom element template uses a template controller (e.g., `switch`, `if`, `repeat`) on a surrogate `<template>` element
- **THEN** the `createFixture()` call SHALL throw an AUR0703 error
- **AND** the test SHALL fail with a clear error message identifying the component

#### Scenario: All registered components are covered
- **WHEN** the smoke test suite runs
- **THEN** it SHALL test every custom element registered in `main.ts` via `.register()`
- **AND** components explicitly excluded (e.g., `dna-orb` due to Canvas dependency) SHALL be documented with a reason in the test file

---

### Requirement: DI mock registry for smoke tests
The test suite SHALL provide a shared mock registry that supplies minimal DI stubs for common service tokens, enabling components to be mounted in isolation.

#### Scenario: Component with DI dependencies mounts successfully
- **WHEN** a component resolves DI tokens (e.g., `IRouter`, `I18N`, `IAuthService`)
- **THEN** the mock registry SHALL provide stub implementations that satisfy the dependency resolution
- **AND** the stubs SHALL implement the minimal interface required (empty methods, default property values)

#### Scenario: Missing DI stub causes clear failure
- **WHEN** a component resolves a DI token not present in the mock registry
- **THEN** the test SHALL fail with a DI resolution error identifying the missing token
- **AND** the developer SHALL add the missing stub to the mock registry

---

### Requirement: E2E console error smoke test
The test suite SHALL navigate to each public route in a real browser and verify that no console errors are emitted during page load.

#### Scenario: Public route loads without console errors
- **WHEN** Playwright navigates to a public route (e.g., `/`, `/welcome`, `/about`, `/discover`)
- **THEN** the page SHALL load successfully
- **AND** no `console.error` messages SHALL be emitted
- **AND** the test SHALL fail if any console error is detected

#### Scenario: Network errors are excluded from assertion
- **WHEN** a console error is caused by a failed network request (e.g., backend unavailable)
- **THEN** the test SHALL exclude network-related errors from the assertion
- **AND** only application-level errors (template compilation, JS exceptions) SHALL cause test failure
