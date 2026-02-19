## 1. Test Infrastructure Setup

- [x] 1.1 Create `test/helpers/mock-logger.ts` with `createMockLogger()` factory returning ILogger mock with all methods as vi.fn()
- [x] 1.2 Create `test/helpers/mock-auth.ts` with `createMockAuth()` factory returning IAuthService mock with configurable state
- [x] 1.3 Create `test/helpers/mock-rpc-clients.ts` with mock factories for IConcertService, IArtistServiceClient, IArtistDiscoveryService
- [x] 1.4 Create `test/helpers/create-container.ts` with `createTestContainer()` helper that sets up DI container with pre-registered ILogger
- [x] 1.5 Configure Vitest coverage reporting in `vitest.config.ts` (add @vitest/coverage-v8)

## 2. Pure Unit Tests

- [x] 2.1 Create `test/components/live-highway/color-generator.spec.ts` - test determinism, different inputs, empty string
- [x] 2.2 Create `test/my-app.spec.ts` - add showNav tests for fullscreen vs non-fullscreen routes (enhance existing file)

## 3. Service Tests

- [x] 3.1 Create `test/services/dashboard-service.spec.ts` - test loadDashboardEvents with multiple artists, no artists, partial RPC failure
- [ ] 3.2 Create `test/services/loading-sequence-service.spec.ts` - test aggregateData with fake timers: success, retry, batching, timeout → [Issue #24](https://github.com/liverty-music/frontend/issues/24)
- [x] 3.3 Create `test/services/onboarding-service.spec.ts` - test hasCompletedOnboarding and redirectBasedOnStatus branching
- [x] 3.4 Create `test/services/toast-notification.spec.ts` - test show/dismiss lifecycle with fake timers
- [ ] 3.5 Create `test/services/artist-discovery-service.spec.ts` - test follow state, dedup, orbIntensity calculation → [Issue #24](https://github.com/liverty-music/frontend/issues/24)

## 4. Bug Fix

- [x] 4.1 Fix `src/services/artist-discovery-service.ts` - add missing `this.` prefix to `artistClient` in `listFollowedFromBackend`

## 5. Component Integration Tests

- [x] 5.1 Create `test/components/auth-status.spec.ts` - test signIn/signUp/signOut delegation via createFixture
- [x] 5.2 Create `test/components/live-highway/event-card.spec.ts` - test backgroundColor, formattedDate, click event dispatch
- [x] 5.3 Create `test/components/live-highway/live-highway.spec.ts` - test isEmpty getter and onEventSelected delegation

## 6. Verification

- [x] 6.1 Run full test suite (`npm test`) and verify all tests pass
- [x] 6.2 Run coverage report and document baseline coverage numbers
