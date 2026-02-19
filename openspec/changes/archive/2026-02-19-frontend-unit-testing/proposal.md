## Why

The Aurelia 2 frontend application has only 2 test files covering 8 test cases (7 active, 1 skipped), leaving 7 services, ~12 components, and 5 route components entirely untested. Business-critical logic such as dashboard data orchestration, onboarding flow routing, loading sequence retry/batching, and artist discovery state management has zero automated verification. Adding comprehensive unit and integration tests will catch regressions early and enable confident refactoring.

## What Changes

- Add shared test utilities (mock factories for ILogger, IAuthService, RPC clients, DI container helper)
- Add unit tests for all pure functions (color-generator, showNav logic)
- Add service-level tests for all services with business logic (dashboard-service, loading-sequence-service, onboarding-service, toast-notification, artist-discovery-service)
- Add component integration tests using `@aurelia/testing` createFixture API (auth-status, event-card, live-highway)
- Configure Vitest coverage reporting
- Fix known bug: missing `this.` in artist-discovery-service.ts `listFollowedFromBackend`

## Capabilities

### New Capabilities
- `frontend-testing`: Comprehensive unit and integration test suite for the Aurelia 2 frontend application, covering services, components, and pure utility functions.

### Modified Capabilities
- `artist-discovery`: Bug fix for `listFollowedFromBackend` missing `this.artistClient` reference.

## Impact

- **Code**: New test files under `test/` directory (services/, components/, helpers/ subdirectories)
- **Config**: Vitest coverage configuration added to `vitest.config.ts`
- **Dependencies**: No new dependencies (all test tooling already installed)
- **Bug fix**: `src/services/artist-discovery-service.ts` - `this.` prefix fix
- **CI**: Tests run via existing `npm test` script (pretest lint + vitest)
