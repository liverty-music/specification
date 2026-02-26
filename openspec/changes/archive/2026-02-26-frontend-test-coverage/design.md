## Context

The Aurelia 2 frontend has 14 test files covering 11 of 40 testable modules. The existing tests use a DI-container-only approach (`createTestContainer` + `Registration.instance` mocks) which is effective and fast. The `@aurelia/testing` `createFixture` API is configured in `test/setup.ts` but not actively used — all tests exercise class logic directly without DOM rendering.

Key untested areas include the auth route guard (security boundary), gRPC interceptor stack (every backend call), onboarding orchestration (new user flow), and ZK proof utilities (core product feature).

Two analysis reports inform this design:
- `tmp/test-coverage-analysis.md` — module inventory with priority rankings
- `tmp/testing-strategy-guide.md` — testing patterns and best practices

## Goals / Non-Goals

**Goals:**
- Add tests for all Priority-1 modules (7 files: auth-hook, loading-sequence-service, connect-error-router, artist-discovery-service, proof-service pure utils, grpc-transport, loading-sequence route)
- Add tests for all Priority-2 modules (7 files: concert-service, error-boundary-service, dashboard route, discover-page route, artist-discovery-page route, tickets-page route, event-detail-sheet component)
- Expand the shared mock helper library to cover newly tested DI interfaces
- Fix known anti-patterns in existing tests (timer cleanup, `any`-typed mocks)
- Raise coverage thresholds to reflect the new baseline

**Non-Goals:**
- E2E tests (Playwright) — infrastructure is ready but not in scope for this change
- `createFixture` DOM rendering tests — existing DI-only approach is sufficient for all targets
- Canvas/dna-orb component tests — intentionally deferred (complex WebGL/Canvas setup)
- Priority-3/4 modules (settings-page, notification-prompt, push-service, etc.) — deferred to a follow-up

## Decisions

### Decision 1: Continue DI-only testing, do not adopt createFixture

**Choice**: All new tests use `createTestContainer()` + direct method invocation.

**Rationale**: Every target module's testable behavior is accessible through public methods and properties. No template binding verification is needed. The DI-only approach is 5-10x faster than fixture-based tests and already proven in the codebase. `createFixture` adds complexity (platform bootstrapping, teardown) with no additional coverage for these modules.

**Alternative considered**: `createFixture` for component tests (event-detail-sheet). Rejected because the valuable test cases (URL construction, touch threshold logic) are all computable from class properties without DOM rendering.

### Decision 2: Test interceptors via mock `next` function pattern

**Choice**: Test `createAuthRetryInterceptor` and `createRetryInterceptor` by constructing the interceptor with mock dependencies, then invoking it with a mock `next` function that returns or throws ConnectRPC responses/errors.

**Rationale**: Interceptors are higher-order functions that wrap a `next` callback. Testing them in isolation (mock `next` + mock `auth`) gives precise control over error codes, retry behavior, and token refresh flows without needing a real transport or HTTP server.

**Alternative considered**: Integration test with `createTransport` + mock HTTP server. Rejected as over-engineering — the interceptor contract is simple enough for unit testing. A future E2E test will cover the full stack.

### Decision 3: Extract and test proof-service pure utilities separately

**Choice**: Test `bytesToDecimal`, `uuidToFieldElement`, and `bytesToHex` as pure unit tests. Test `verifyCircuitIntegrity` with mocked `crypto.subtle.digest`. Defer full `generateEntryProof` integration testing.

**Rationale**: The pure utility functions contain subtle BigInt arithmetic that is critical to correctness and trivially testable. The full proof generation pipeline requires mocking Worker, fetch, crypto, and circuit files — high effort with diminishing returns for a unit test. The pure functions cover the highest-risk math.

**Alternative considered**: Full `generateEntryProof` mock test. Deferred to Priority-3 or E2E scope.

### Decision 4: Use `vi.mock` + dynamic import for modules with side effects

**Choice**: For modules that import from `@aurelia/router` or proto-generated RPC clients at the module level, use the established pattern: `vi.mock()` at file top → `DI.createInterface()` stub → `await import()` for the SUT.

**Rationale**: Already proven in `my-artists-page.spec.ts`. Consistent with existing codebase conventions. Vitest's module hoisting makes this reliable.

### Decision 5: One mock factory per service interface

**Choice**: Add new mock helper files: `mock-router.ts`, `mock-toast.ts`, `mock-error-boundary.ts`, `mock-ticket-service.ts`, `mock-proof-service.ts`, `mock-loading-sequence.ts`. Each returns `Partial<IInterface>` with `vi.fn()` defaults.

**Rationale**: Follows the established pattern from `mock-auth.ts` and `mock-rpc-clients.ts`. Typed `Partial<IInterface>` catches mock shape drift at compile time. Centralizing avoids inline mock duplication across test files.

### Decision 6: Fix timer anti-pattern globally

**Choice**: Refactor `my-artists-page.spec.ts` to move `vi.useRealTimers()` from inside `it()` blocks to `afterEach()`. Apply this pattern to all new tests.

**Rationale**: If a test throws before reaching `vi.useRealTimers()`, fake timers leak into subsequent tests causing flaky failures. The `afterEach` pattern is unconditionally safe.

## Risks / Trade-offs

**[Risk] Module-level side effects block import** → Some modules (e.g., those importing `auth-service.ts`) trigger `window.location` access at parse time. Mitigation: Use `vi.mock()` + dynamic import pattern (Decision 4). Already proven in codebase.

**[Risk] `connect-error-router` tests depend on ConnectRPC internal types** → The `ConnectError` constructor and error codes may change across versions. Mitigation: Import error types from `@connectrpc/connect` directly; pin version in `package.json`.

**[Risk] Coverage threshold increase breaks CI before all tests land** → If thresholds are raised before tests are merged, CI will fail. Mitigation: Raise thresholds as the final task, after all test files are committed. Use a separate commit for the config change.

**[Trade-off] No DOM rendering tests** → We accept that template binding bugs (e.g., wrong `if.bind` condition) won't be caught by these tests. Mitigation: Storybook visual review + future E2E tests cover this gap.

**[Trade-off] Proof-service full pipeline not tested** → `generateEntryProof` end-to-end is deferred. Mitigation: Pure utility tests cover the highest-risk math. Integration testing is better suited to E2E with real circuit files.
