## Context

The Aurelia 2 frontend application (`liverty-music/frontend`) has minimal test coverage: 2 test files with 8 test cases. The existing `test/setup.ts` bootstraps the Aurelia `BrowserPlatform` for jsdom, and `@aurelia/testing` is already installed. Vitest is configured with jsdom environment. No shared test utilities or mock factories exist, causing each test file to duplicate mock setup.

All services follow the same DI pattern: `resolve(IInterface)` in field initializers, with `DI.createInterface` providing mockable tokens. Components use `@bindable` properties and `createFixture` for integration testing.

## Goals / Non-Goals

**Goals:**
- Establish reusable test infrastructure (mock factories, DI helpers)
- Achieve comprehensive test coverage for all services with business logic
- Add component integration tests for interactive components
- Configure coverage reporting for visibility
- Fix the known bug in `artist-discovery-service.ts`

**Non-Goals:**
- E2E tests (Playwright) - deferred to a separate change
- Testing thin RPC client wrappers with no business logic (`user-service.ts`, `artist-service-client.ts`)
- Visual/snapshot testing for canvas components (`dna-orb/`)
- Testing generated protobuf code

## Decisions

### 1. Test file organization: `test/` directory with subdirectories

**Decision**: Keep tests in `test/` root (matching existing convention and Aurelia monorepo pattern) with `services/`, `components/`, and `helpers/` subdirectories.

**Rationale**: The project already has `test/setup.ts` and two test files in `test/`. Aurelia's own monorepo uses a centralized `__tests__` package. Subdirectories add organization without restructuring.

**Alternative considered**: Co-located tests (`src/services/__tests__/`). Rejected because it contradicts the existing pattern and Aurelia convention.

### 2. Shared mock factories over inline mocks

**Decision**: Create reusable mock factories in `test/helpers/` for commonly mocked dependencies: `ILogger`, `IAuthService`, `IRouter`, and RPC service clients.

**Rationale**: Every service resolves `ILogger` and most resolve `IAuthService`. The existing `auth-service.spec.ts` already duplicates mock setup that could be shared. Factories reduce boilerplate and ensure consistent mock behavior.

**Structure**:
```
test/helpers/
  mock-logger.ts        # createMockLogger() -> ILogger mock
  mock-auth.ts          # createMockAuth() -> IAuthService mock
  mock-rpc-clients.ts   # createMockConcertService(), etc.
  create-container.ts   # createTestContainer(...registrations)
```

### 3. Service tests via DI container (not module mocking)

**Decision**: Test services by creating a real `DI.createContainer()` with mocked dependencies registered via `Registration.instance()`, rather than using `vi.mock()` for module-level mocking.

**Rationale**: DI container approach is idiomatic Aurelia, matches how services are actually resolved at runtime, and avoids the fragility of module mocking. The existing `auth-service.spec.ts` already demonstrates this pattern successfully.

**Exception**: `auth-service.spec.ts` will continue using `vi.mock('oidc-client-ts')` because `UserManager` is instantiated directly (not via DI).

### 4. Fake timers for time-dependent tests

**Decision**: Use `vi.useFakeTimers()` for tests involving `setTimeout`, `requestAnimationFrame`, and `Date.now()`.

**Applicable to**: `toast-notification.ts` (show/dismiss timing), `loading-sequence-service.ts` (timeout, minimum display, retry delays).

**Rationale**: Real timers make tests slow and flaky. Vitest's fake timer API provides deterministic control.

### 5. Component tests via DI container (simplified unit testing)

**Decision**: Use DI container instantiation (`container.get(Component)`) for component unit tests, reserving `createFixture` for complex integration tests.

**Rationale**: During implementation, we found that `createFixture` adds unnecessary overhead for simple component unit tests. The DI container approach is:
- **Simpler**: Direct instantiation without fixture boilerplate
- **Faster**: No template compilation or DOM rendering for unit tests
- **More focused**: Tests view-model logic and delegation directly
- **Idiomatic**: Matches the service testing pattern (DI container with mocks)

**When to use each approach**:
- **DI container** (`container.get(Component)`): Unit tests for delegation, computed properties, simple logic
- **createFixture**: Integration tests requiring full template binding, lifecycle hooks, or DOM interaction

**Implementation pattern**:
```typescript
beforeEach(() => {
  const container = createTestContainer(
    Registration.instance(IDependency, mockDependency),
  )
  container.register(MyComponent)
  component = container.get(MyComponent)
})
```

**Deviation from original design**: Originally planned to use `createFixture` for all component tests. Implementation revealed that DI container approach is more appropriate for unit testing, with `createFixture` reserved for true integration tests.

### 6. Coverage configuration

**Decision**: Add `@vitest/coverage-v8` with statement/branch/function thresholds reported but not enforced.

**Rationale**: V8 coverage is fast and works with jsdom. Starting without enforcement avoids blocking CI while building coverage incrementally.

**Implementation results**:
- Initial coverage: 22.15% (50 tests, 9 test files)
- Service coverage: 90%+ on tested services (DashboardService 97.39%, OnboardingService 92.1%)
- Component coverage: 100% on tested components

**Future improvements**: Once remaining complex service tests are implemented ([Issue #24](https://github.com/liverty-music/frontend/issues/24)), consider adding coverage thresholds:
- Target: 40%+ overall coverage
- Enforcement: Optional, could be added to CI workflow to prevent regressions

## Risks / Trade-offs

**[Locale-dependent formatting]** `dashboard-service.ts` and `event-card.ts` use `toLocaleDateString('ja-JP', ...)`. Test output depends on the system locale and ICU data availability.
-> Mitigation: Assert on structural patterns (e.g., contains year, month, day) rather than exact strings, or use regex matching.

**[Shadow DOM in component tests]** The Vite plugin sets `defaultShadowOptions: 'open'`. Component tests may need to traverse `shadowRoot` to query elements.
-> Mitigation: Use `appHost.querySelector('component-name')?.shadowRoot?.querySelector(...)` pattern, as demonstrated in existing `my-app.spec.ts`.

**[Non-deterministic `Math.random()`]** `artist-discovery-service.ts` uses `Math.random()` in `toBubble()` for radius.
-> Mitigation: Mock `Math.random` with `vi.spyOn(Math, 'random').mockReturnValue(0.5)` in relevant tests.

**[Constructor side effects in RPC services]** Services create gRPC clients in constructors. Direct instantiation triggers real transport creation.
-> Mitigation: For services with business logic (dashboard, loading-sequence, onboarding), mock the entire DI interface rather than testing the class directly. For `artist-discovery-service`, mock the protobuf client module.
