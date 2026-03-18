## Context

The `207-refine-state-naming` branch introduced `@aurelia/state` with a Redux-style store (`IStore<AppState, AppAction>`). A convenience wrapper `resolveStore()` calls `resolve(IStore)` and is used at class field initialization time in 11 files. This triggers AUR0016 because the DI container is not active during field initializer evaluation for `IStore` (unlike `ILogger` which is registered earlier in the Aurelia bootstrap pipeline).

The existing E2E smoke test (`e2e/smoke/no-console-errors.spec.ts`) would catch this error, but it only runs locally — the CI pipeline (`ci.yaml`) only executes vitest unit tests, not Playwright E2E tests.

## Goals / Non-Goals

**Goals:**
- Fix the AUR0016 runtime crash so all pages render correctly
- Add the Playwright `smoke` project to CI as a parallel job so DI resolution failures are caught before merge

**Non-Goals:**
- Expanding E2E smoke test coverage to authenticated routes (requires OIDC session state in CI)
- Changing the `@aurelia/state` store architecture or middleware
- Adding Playwright to the `make check` pre-commit target (too slow for local dev)

## Decisions

### D1: Keep `resolve()` at field init, fix `IStore` registration timing

**Choice**: Ensure `StateDefaultConfiguration.init()` registers `IStore` in a way compatible with Aurelia's `resolve()` at field initialization time.

**Alternative considered**: Move all `resolveStore()` calls to constructor bodies or lifecycle hooks. Rejected because `resolve(ILogger)`, `resolve(IAuthService)`, etc. already work at field init — this is an established pattern in the codebase. The fix should target why `IStore` specifically fails, not change the DI pattern used everywhere.

**Investigation needed during implementation**: Verify whether `StateDefaultConfiguration.init()` is correctly creating a singleton `IStore` registration. If the issue is in `@aurelia/state` itself, the workaround is to manually register `IStore` before calling `StateDefaultConfiguration.init()`.

### D2: CI smoke job runs in parallel with existing jobs

**Choice**: Add a `smoke` job to `ci.yaml` that runs in parallel with `lint`, `test`, and `security` (all gated by `changes` job).

```
ci.yaml job graph:

  changes ──┬── lint
            ├── test
            ├── security
            ├── smoke       ← NEW (parallel)
            └── ci-success  (waits for all)
```

**Rationale**: The smoke test launches a Vite dev server (`npm start`) and navigates 3 public routes — ~30-60s total. Running it in parallel avoids adding to the critical path.

### D3: Use Playwright's built-in `webServer` config for CI

**Choice**: Rely on `playwright.config.mjs`'s existing `webServer` block (`command: 'npm start'`, `port: 9000`, `reuseExistingServer: !process.env.CI`).

**Rationale**: No custom server startup script needed. In CI, `process.env.CI` is truthy so Playwright will start the dev server fresh and wait for port 9000. The `smoke` project already configures `baseURL: 'http://localhost:9000'`.

### D4: Install only Chromium for smoke job

**Choice**: Use `npx playwright install --with-deps chromium` instead of installing all browsers.

**Rationale**: The `smoke` project uses `devices['Desktop Chrome']` only. Installing all browsers adds ~300MB and 30s of unnecessary download time.

## Risks / Trade-offs

**[Risk] Vite dev server startup time in CI** → The dev server may take 10-20s to start. Playwright's `webServer` config handles this by waiting for the port. Set `timeout-minutes: 5` on the job as a safety net.

**[Risk] Flaky smoke tests due to timing** → The test uses `waitForTimeout(2000)` for async init. In CI this should be sufficient since no network calls are made (backend is not running, and network errors are excluded). If flaky, increase to 3000ms.

**[Risk] `@aurelia/state` IStore registration may be an upstream bug** → If the fix requires a workaround for an `@aurelia/state` RC issue, document it clearly with a link to the upstream issue tracker.

## Open Questions

- Is the `IStore` resolution failure caused by registration ordering in `main.ts`, or by `StateDefaultConfiguration.init()` not creating a standard DI registration? → Investigate during implementation.
