## Why

The frontend application has only 27.5% testable file coverage (11 of 40 testable modules). Critical infrastructure — the auth route guard, gRPC interceptor stack, onboarding orchestration, and ZK proof pipeline — has zero test coverage. A single bug in any of these modules breaks the entire application for all users. Adding targeted tests for the highest-risk modules will prevent regressions in core user flows and establish patterns for ongoing coverage growth.

## What Changes

- Add unit tests for 7 Priority-1 modules: `auth-hook`, `loading-sequence-service`, `connect-error-router`, `artist-discovery-service`, `proof-service` (pure utilities), `grpc-transport`, and `loading-sequence` route
- Add unit tests for 7 Priority-2 modules: `concert-service`, `error-boundary-service`, `dashboard` route, `discover-page` route, `artist-discovery-page` route, `tickets-page` route, `event-detail-sheet` component
- Add shared mock helpers for `IRouter`, `IToastService`, `IErrorBoundaryService`, `ITicketService`, `IProofService`, `ILoadingSequenceService`
- Fix existing anti-patterns: move `vi.useRealTimers()` to `afterEach`, replace `any`-typed mocks with `Partial<IInterface>`
- Raise coverage thresholds from 20/70/30/20 to 55/75/55/55 (statements/branches/functions/lines)

## Capabilities

### New Capabilities

_(none — all testing requirements extend the existing `frontend-testing` capability)_

### Modified Capabilities

- `frontend-testing`: Add requirements for auth hook guard testing, gRPC interceptor testing, service orchestration testing, route lifecycle testing, component logic testing, and raised coverage thresholds

## Impact

- **Code**: New test files under `test/` mirroring `src/` structure; new mock helper files under `test/helpers/`
- **CI**: Coverage thresholds in `vitest.config.ts` will increase — CI will enforce higher minimums
- **Dependencies**: No new runtime dependencies; may add `@vitest/expect` utilities if needed for custom matchers
- **Existing tests**: Minor refactoring to fix anti-patterns (timer cleanup, mock typing) — no behavior changes
