## 1. Fix AUR0016 DI Resolution Error

- [x] 1.1 Investigate why `resolve(IStore)` fails at field init while `resolve(ILogger)` succeeds — check `StateDefaultConfiguration.init()` registration behavior
- [x] 1.2 Fix the `IStore` registration or `resolveStore()` call sites so all 11 affected files resolve without AUR0016
- [x] 1.3 Run `make test` to verify existing unit tests still pass after the fix

## 2. Add Playwright Smoke Job to CI

- [x] 2.1 Add `smoke` job to `frontend/.github/workflows/ci.yaml` running in parallel with `lint`, `test`, `security` (gated by `changes`)
- [x] 2.2 Install only Chromium via `npx playwright install --with-deps chromium`
- [x] 2.3 Run `npx playwright test --project=smoke` in the job
- [x] 2.4 Add `smoke` and `smoke-skip` to the `ci-success` job's `needs` and `allowed-skips`

## 3. Verify

- [x] 3.1 Run `npx playwright test --project=smoke` locally to confirm the DI fix resolves the console errors
- [x] 3.2 Run `make check` to verify lint + unit tests pass
