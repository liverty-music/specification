## 1. Mock Helper Expansion

- [x] 1.1 Create `test/helpers/mock-router.ts` — `createMockRouter()` returning `Partial<IRouter>` with `load` as `vi.fn()`
- [x] 1.2 Create `test/helpers/mock-toast.ts` — `createMockToastService()` returning `Partial<IToastService>` with `show` as `vi.fn()`
- [x] 1.3 Create `test/helpers/mock-error-boundary.ts` — `createMockErrorBoundary()` returning `Partial<IErrorBoundaryService>` with `captureError`, `dismiss`, `addBreadcrumb` as `vi.fn()`
- [x] 1.4 Create `test/helpers/mock-ticket-service.ts` — `createMockTicketService()` returning `Partial<ITicketService>` with `listTickets` as `vi.fn()`
- [x] 1.5 Create `test/helpers/mock-proof-service.ts` — `createMockProofService()` returning `Partial<IProofService>` with `generateEntryProof` as `vi.fn()`
- [x] 1.6 Create `test/helpers/mock-loading-sequence.ts` — `createMockLoadingSequenceService()` returning `Partial<ILoadingSequenceService>` with `aggregateData` as `vi.fn()`

## 2. Fix Existing Anti-Patterns

- [x] 2.1 Refactor `test/routes/my-artists-page.spec.ts` — move `vi.useRealTimers()` from inside `it()` blocks to `afterEach()`
- [x] 2.2 Refactor `test/auth-service.spec.ts` — replace `any`-typed `userManagerMock` with a typed `Partial<UserManager>` or factory
- [x] 2.3 Refactor `test/auth-service.spec.ts` — replace inline logger mock with `createTestContainer()`

## 3. Priority-1 Service Tests

- [x] 3.1 Create `test/hooks/auth-hook.spec.ts` — test `canLoad` for public route bypass, authenticated user pass-through, unauthenticated redirect, and `authService.ready` awaiting
- [x] 3.2 Create `test/services/loading-sequence-service.spec.ts` — test `aggregateData` for happy path, artist fetch retry, batch-of-5 concurrency, 10s global timeout, 3s minimum display, AbortSignal propagation, and `delay` cleanup
- [x] 3.3 Create `test/services/connect-error-router.spec.ts` — test `createAuthRetryInterceptor` (Unauthenticated retry, refresh failure redirect, non-auth passthrough) and `createRetryInterceptor` (Unavailable backoff, DeadlineExceeded retry, max retries exhausted, non-retryable passthrough)
- [x] 3.4 Create `test/services/artist-discovery-service.spec.ts` — test `loadInitialArtists`, `followArtist` optimistic update + rollback, deduplication (name/id/mbid), `reloadWithTag`, `evictOldest`, `getSimilarArtists`, `orbIntensity`
- [x] 3.5 Create `test/services/proof-service.spec.ts` — test pure utilities (`bytesToDecimal`, `uuidToFieldElement`, `bytesToHex`) and `verifyCircuitIntegrity` with mocked `crypto.subtle.digest`
- [x] 3.6 Create `test/services/grpc-transport.spec.ts` — test `authInterceptor` Bearer header injection (with token, without token) and interceptor ordering
- [x] 3.7 Create `test/routes/loading-sequence.spec.ts` — test `canLoad` (5 routing outcomes: local artists → allow, backend artists → redirect `/`, empty → redirect `/artist-discovery`, error → redirect `/artist-discovery`) and aggregation result handling (complete/partial/failed → navigate to dashboard)

## 4. Priority-2 Service Tests

- [x] 4.1 Create `test/services/concert-service.spec.ts` — test `listConcerts`, `listByFollower`, `searchNewConcerts`, AbortSignal forwarding, and error propagation
- [x] 4.2 Create `test/services/error-boundary-service.spec.ts` — test `captureError` + history cap, `addBreadcrumb` ring buffer, `generateReport` markdown output, `sanitize` token redaction, `buildGitHubIssueUrl`, and `dismiss`

## 5. Priority-2 Route Tests

- [x] 5.1 Create `test/routes/dashboard.spec.ts` — test `loadData` happy path, stale data preservation on failure, AbortError ignore, `retry`, region setup trigger, `onRegionSelected` reload
- [x] 5.2 Create `test/routes/discover-page.spec.ts` — test 300ms debounced search, stale response discard, genre tag toggle (activate/deactivate), `clearSearch`, follow from search, using `vi.useFakeTimers()` and `vi.mock` for dynamic imports
- [x] 5.3 Create `test/routes/artist-discovery-page.spec.ts` — test initial load, guidance auto-dismiss (5s + 400ms fade via fake timers), artist selection → follow + live event check, `retryLoad`, `onViewSchedule` navigation
- [x] 5.4 Create `test/routes/tickets-page.spec.ts` — test `mintDate` and `formatTokenId` (pure), `generateEntryCode` happy path (mock ProofService + QRCode), error handling, AbortError discrimination, `dismissQr`

## 6. Priority-2 Component Tests

- [x] 6.1 Create `test/components/live-highway/event-detail-sheet.spec.ts` — test `googleMapsUrl` URL construction, `calendarUrl` URL construction, `backgroundColor`, touch drag > 100px → close, touch drag < 100px → stays open, history pushState/replaceState

## 7. Coverage Threshold Update

- [x] 7.1 Update `vitest.config.ts` — raise coverage thresholds to statements: 55, branches: 75, functions: 55, lines: 55
- [x] 7.2 Run full test suite (`vitest run --coverage`) and verify all tests pass and thresholds are met
