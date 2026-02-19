# Current Test State Analysis

## Summary

| Dimension | Status |
|-----------|--------|
| Test framework | Vitest (unit) + Playwright (E2E) configured |
| Total test files | 2 |
| Total test cases | 8 (7 active, 1 skipped) |
| E2E tests | None (config exists, no files) |
| Storybook | 1 story (welcome-page) |
| Test utilities | Basic Aurelia setup file only |
| Coverage reporting | Not configured |

## Test Framework Configuration

### Vitest (`vitest.config.ts`)
- Environment: `jsdom`
- Watch mode disabled by default
- Excludes `e2e/*` directory
- Setup file: `./test/setup.ts`
- Merges with main Vite config (inherits Aurelia plugin)

### Playwright (`playwright.config.mjs`)
- Test directory: `./e2e` (does not exist)
- Only Chromium active
- Web server: `npm start` on port 9000

### Test Dependencies
- `@aurelia/testing` (latest) - `createFixture` utility
- `jsdom` (^25.0.1) - DOM environment
- `@playwright/test` (^1.49.1) - E2E framework

## Existing Test Files

### `test/auth-service.spec.ts` (6 tests)
- Mocks `oidc-client-ts` module entirely via `vi.mock`
- Creates DI container with mocked `ILogger`
- Tests: UserManager init, isAuthenticated state, signIn, register, signOut, handleCallback
- Uses `@ts-expect-error` for private member access

### `test/my-app.spec.ts` (2 tests, 1 skipped)
- 1 skipped test (complex dependency mocking needed)
- 1 active test verifying `<nav>` and `<au-viewport>` presence via `createFixture`

### `test/setup.ts`
- JSDOM instance with global DOM objects
- Aurelia `BrowserPlatform` bootstrap via `setPlatform()`
- Auto-cleanup: tracks fixtures via `onFixtureCreated`, stops in `afterEach`

## Untested Code

### Services (7 untested)
- `grpc-transport.ts` - Transport factory with auth interceptor
- `artist-service-client.ts` - Artist RPC client wrapper
- `artist-discovery-service.ts` - Artist discovery state management
- `concert-service.ts` - Concert RPC client
- `dashboard-service.ts` - Dashboard data orchestration
- `loading-sequence-service.ts` - Loading flow with retry/batching
- `onboarding-service.ts` - Onboarding status & routing
- `user-service.ts` - User RPC client wrapper

### Components (~12 untested)
- `auth-status` - Sign in/out UI
- `dna-orb/` - Canvas animation (3 files)
- `icons/` - SVG icon components (4 files)
- `live-highway/` - Live events feature (5 files)
- `region-setup-sheet/` - Region config
- `toast-notification/` - Toast notification

### Route Components (5 untested)
- `auth-callback` - OIDC callback
- `dashboard` - User dashboard
- `artist-discovery-page` - Onboarding discovery
- `loading-sequence` - Onboarding loading animation
- `welcome-page` / `about-page` - Static pages

## Known Bug

`artist-discovery-service.ts` line ~112: `artistClient` missing `this.` prefix.
```ts
// Bug:
const resp = await artistClient.listFollowed({}, { signal })
// Should be:
const resp = await this.artistClient.listFollowed({}, { signal })
```
