## Why

Every page on dev.liverty-music.app crashes with AUR0016 (`ISyntaxInterpreter` DI resolution failure) after the `207-refine-state-naming` branch introduced `@aurelia/state`. The root cause is `resolveStore()` called at class field initialization time in 11 service/route files, outside an active DI container context. This error was not caught because the E2E smoke test (`no-console-errors.spec.ts`) is not executed in CI — only locally.

## What Changes

- Fix the AUR0016 DI resolution error by correcting the `resolveStore()` call timing in all affected files
- Add a CI job that runs the Playwright `smoke` project in parallel with existing lint/test/security jobs
- Verify the fix via the existing `e2e/smoke/no-console-errors.spec.ts` test

## Capabilities

### New Capabilities

_(none — this is a bugfix and CI improvement)_

### Modified Capabilities

- `component-smoke-tests`: Add requirement that E2E console error smoke tests MUST run in CI, not just locally
- `state-management`: Add requirement that store resolution must occur within an active DI context (constructor or lifecycle hook), never at field initialization time

## Impact

- **Frontend services/routes** (11 files): `resolveStore()` call site changes
- **CI pipeline**: New parallel `smoke` job in `ci.yaml` (adds ~30-60s)
- **State infrastructure**: `store-interface.ts` may need API adjustment to prevent misuse
