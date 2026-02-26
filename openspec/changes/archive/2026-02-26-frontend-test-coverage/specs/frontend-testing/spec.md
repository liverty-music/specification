## ADDED Requirements

### Requirement: Auth hook guards all authenticated routes
The `AuthHook.canLoad` method SHALL enforce authentication on all routes except those with `data.auth === false`.

#### Scenario: Public route bypasses auth check
- **WHEN** `canLoad` is called with a route where `data.auth === false`
- **THEN** it SHALL return `true` without awaiting `authService.ready`

#### Scenario: Authenticated user on protected route
- **WHEN** `canLoad` is called for a protected route and `authService.isAuthenticated` is `true`
- **THEN** it SHALL return `true`

#### Scenario: Unauthenticated user redirected to welcome
- **WHEN** `canLoad` is called for a protected route and `authService.isAuthenticated` is `false`
- **THEN** it SHALL return the redirect path `/welcome`
- **AND** it SHALL show a toast notification

#### Scenario: Auth readiness is awaited before checking
- **WHEN** `canLoad` is called and `authService.ready` has not yet resolved
- **THEN** the method SHALL await `authService.ready` before checking `isAuthenticated`

### Requirement: Auth retry interceptor refreshes tokens on Unauthenticated errors
The `createAuthRetryInterceptor` SHALL intercept `Code.Unauthenticated` errors, attempt a silent OIDC token refresh, and retry the request.

#### Scenario: Silent refresh succeeds and request is retried
- **WHEN** a gRPC call returns `Code.Unauthenticated`
- **THEN** the interceptor SHALL call `signinSilent()` and retry the original request

#### Scenario: Silent refresh fails and user is redirected
- **WHEN** a gRPC call returns `Code.Unauthenticated` and `signinSilent()` throws
- **THEN** the interceptor SHALL redirect to `/welcome`

#### Scenario: Non-auth errors pass through
- **WHEN** a gRPC call returns an error code other than `Unauthenticated`
- **THEN** the interceptor SHALL re-throw the error without interception

### Requirement: Retry interceptor applies exponential backoff on transient errors
The `createRetryInterceptor` SHALL retry requests that fail with `Code.Unavailable` or `Code.DeadlineExceeded` using exponential backoff.

#### Scenario: Unavailable error triggers retry with backoff
- **WHEN** a gRPC call returns `Code.Unavailable`
- **THEN** the interceptor SHALL retry with exponential backoff delay

#### Scenario: DeadlineExceeded error triggers retry
- **WHEN** a gRPC call returns `Code.DeadlineExceeded`
- **THEN** the interceptor SHALL retry with exponential backoff delay

#### Scenario: Max retries exhausted
- **WHEN** retries are exhausted and the error persists
- **THEN** the interceptor SHALL throw the original error

#### Scenario: Non-retryable error is not retried
- **WHEN** a gRPC call returns `Code.NotFound` or `Code.InvalidArgument`
- **THEN** the interceptor SHALL throw immediately without retrying

### Requirement: Artist discovery service manages bubble state with optimistic follow
The `ArtistDiscoveryService` SHALL manage artist bubbles, track seen artists across three deduplication sets, and perform optimistic follow/unfollow with retry and rollback.

#### Scenario: Load initial artists
- **WHEN** `loadInitialArtists` is called
- **THEN** it SHALL fetch artists from the backend, convert them to bubbles, and populate `availableBubbles`

#### Scenario: Follow artist with optimistic update
- **WHEN** `followArtist` is called with an artist
- **THEN** it SHALL immediately add the artist to `followedArtists` before the backend call completes

#### Scenario: Follow fails after retry — rollback
- **WHEN** `followArtist` backend call fails and the retry also fails
- **THEN** it SHALL remove the artist from `followedArtists` (rollback)

#### Scenario: Deduplication across name, id, and mbid
- **WHEN** an artist has already been seen (by name, id, or mbid)
- **THEN** it SHALL NOT be added to `availableBubbles` again

#### Scenario: Reload with genre tag
- **WHEN** `reloadWithTag` is called with a genre tag
- **THEN** it SHALL clear existing bubbles and fetch new artists filtered by the tag

#### Scenario: Evict oldest bubbles
- **WHEN** `evictOldest` is called with count N
- **THEN** it SHALL remove the N oldest bubbles from `availableBubbles`

### Requirement: Proof service utility functions perform correct byte-to-field conversions
The proof-service pure utility functions SHALL correctly convert between byte arrays, hex strings, decimal strings, and field elements.

#### Scenario: bytesToDecimal converts big-endian bytes to decimal string
- **WHEN** `bytesToDecimal` is called with `Uint8Array([1, 0])`
- **THEN** it SHALL return `"256"`

#### Scenario: bytesToDecimal handles single zero byte
- **WHEN** `bytesToDecimal` is called with `Uint8Array([0])`
- **THEN** it SHALL return `"0"`

#### Scenario: uuidToFieldElement converts UUID to field element
- **WHEN** `uuidToFieldElement` is called with a valid UUID string
- **THEN** it SHALL return a decimal string representing the UUID's bytes as a big-endian integer

#### Scenario: bytesToHex converts bytes to hex string
- **WHEN** `bytesToHex` is called with `Uint8Array([255, 0, 171])`
- **THEN** it SHALL return `"ff00ab"`

### Requirement: Proof service verifies circuit file integrity
The `verifyCircuitIntegrity` method SHALL verify SHA-256 hashes of downloaded circuit files against hardcoded expected hashes.

#### Scenario: Hash matches expected value
- **WHEN** the SHA-256 digest of a downloaded file matches the hardcoded hash
- **THEN** verification SHALL succeed without error

#### Scenario: Hash mismatch
- **WHEN** the SHA-256 digest does not match
- **THEN** verification SHALL throw an error indicating integrity failure

### Requirement: gRPC transport injects auth headers
The `authInterceptor` within `createTransport` SHALL inject a Bearer token into every outgoing gRPC request.

#### Scenario: Authenticated user has valid token
- **WHEN** `getUserManager().getUser()` returns a user with an `access_token`
- **THEN** the interceptor SHALL add `Authorization: Bearer <token>` to the request headers

#### Scenario: No authenticated user
- **WHEN** `getUserManager().getUser()` returns `null`
- **THEN** the interceptor SHALL NOT add an Authorization header

### Requirement: Loading sequence route guards based on onboarding status
The `LoadingSequence.canLoad` method SHALL check onboarding completion and redirect accordingly.

#### Scenario: User has locally followed artists
- **WHEN** `canLoad` is called and the local `followedArtists` array is non-empty
- **THEN** it SHALL return `true` (allow navigation)

#### Scenario: No local artists but backend has followed artists
- **WHEN** local `followedArtists` is empty but `listFollowedFromBackend` returns artists
- **THEN** it SHALL redirect to `/` (dashboard)

#### Scenario: No followed artists anywhere
- **WHEN** both local and backend artist lists are empty
- **THEN** it SHALL redirect to `/artist-discovery`

#### Scenario: Backend check fails
- **WHEN** `listFollowedFromBackend` throws an error
- **THEN** it SHALL redirect to `/artist-discovery` as a safe fallback

### Requirement: Loading sequence animates phases during data aggregation
The `LoadingSequence` route SHALL display a multi-phase progress animation while `LoadingSequenceService.aggregateData` runs.

#### Scenario: Complete aggregation navigates to dashboard
- **WHEN** `aggregateData` returns status `complete`
- **THEN** the route SHALL navigate to `/dashboard`

#### Scenario: Partial aggregation navigates to dashboard
- **WHEN** `aggregateData` returns status `partial`
- **THEN** the route SHALL navigate to `/dashboard`

#### Scenario: Failed aggregation captures error and navigates
- **WHEN** `aggregateData` returns status `failed`
- **THEN** the route SHALL capture the error via `ErrorBoundaryService` and navigate to `/dashboard`

### Requirement: Concert service forwards RPC calls with AbortSignal
The `ConcertService` SHALL forward concert listing and search requests to the backend gRPC service with AbortSignal support.

#### Scenario: List concerts by artist
- **WHEN** `listConcerts` is called with an artist ID
- **THEN** it SHALL call the backend `listConcerts` RPC and return the response

#### Scenario: List concerts by follower
- **WHEN** `listByFollower` is called
- **THEN** it SHALL call the backend `listByFollower` RPC for the authenticated user

#### Scenario: AbortSignal cancels in-flight request
- **WHEN** the provided AbortSignal is aborted during a request
- **THEN** the RPC call SHALL be cancelled

### Requirement: Error boundary service captures and sanitizes errors
The `ErrorBoundaryService` SHALL capture application errors, maintain a capped history, track breadcrumbs, and generate sanitized error reports.

#### Scenario: Capture error adds to history
- **WHEN** `captureError` is called with an error
- **THEN** the error SHALL be added to the history and set as `currentError`

#### Scenario: History is capped
- **WHEN** the error history exceeds the maximum size
- **THEN** the oldest entry SHALL be removed

#### Scenario: Sanitize redacts sensitive tokens
- **WHEN** `generateReport` is called for an error containing Bearer tokens or JWT strings
- **THEN** the report SHALL redact those tokens

#### Scenario: GitHub issue URL is constructed correctly
- **WHEN** `buildGitHubIssueUrl` is called
- **THEN** it SHALL return a valid GitHub URL with pre-filled title and body

#### Scenario: Dismiss clears current error
- **WHEN** `dismiss` is called
- **THEN** `currentError` SHALL be set to `null`

### Requirement: Dashboard route manages stale data on reload failure
The `Dashboard` route SHALL preserve existing data and mark it as stale when a data reload fails.

#### Scenario: Successful data load
- **WHEN** `loadData` succeeds
- **THEN** `groupedEvents` SHALL contain the returned date groups and `isStale` SHALL be `false`

#### Scenario: Reload failure preserves old data
- **WHEN** `loadData` fails after a previous successful load
- **THEN** `groupedEvents` SHALL retain the previous data and `isStale` SHALL be `true`

#### Scenario: AbortError is ignored
- **WHEN** `loadData` throws an AbortError (navigation-triggered)
- **THEN** the error SHALL NOT be set on the component

#### Scenario: Retry clears error and reloads
- **WHEN** `retry` is called
- **THEN** the error state SHALL be cleared and `loadData` SHALL be invoked again

### Requirement: Discover page debounces search with stale response guard
The `DiscoverPage` route SHALL debounce artist search input by 300ms and discard stale responses.

#### Scenario: Search is debounced
- **WHEN** the search query changes
- **THEN** `performSearch` SHALL NOT be called until 300ms after the last change

#### Scenario: Stale search response is discarded
- **WHEN** the search query changes again before a previous search responds
- **THEN** the previous response SHALL be discarded

#### Scenario: Genre tag toggle activates and deactivates
- **WHEN** a genre tag is selected and then selected again
- **THEN** the first selection SHALL call `reloadWithTag` and the second SHALL call `loadInitialArtists`

#### Scenario: Clear search restores bubble view
- **WHEN** `clearSearch` is called
- **THEN** the search query SHALL be emptied and the bubble canvas SHALL resume

### Requirement: Artist discovery page dismisses guidance overlay
The `ArtistDiscoveryPage` route SHALL auto-dismiss the guidance overlay after 5 seconds with a 400ms fade animation.

#### Scenario: Guidance auto-dismiss after 5 seconds
- **WHEN** the component is attached
- **THEN** the guidance overlay SHALL become hidden after 5000ms

#### Scenario: Fade animation before removal
- **WHEN** the guidance overlay begins dismissing
- **THEN** a 400ms fade-out animation SHALL complete before the element is removed

#### Scenario: Artist selection triggers follow and live event check
- **WHEN** an artist is selected
- **THEN** `followArtist` SHALL be called followed by `checkLiveEvents`

### Requirement: Tickets page generates ZK proof entry QR codes
The `TicketsPage` route SHALL generate ZK proof entry codes and display them as QR code images.

#### Scenario: Successful proof generation
- **WHEN** `generateEntryCode` is called for a ticket
- **THEN** it SHALL call `ProofService.generateEntryProof`, encode the result as base64 JSON, generate a QR code, and open the QR modal

#### Scenario: Proof generation error
- **WHEN** `generateEntryProof` throws an error
- **THEN** the error SHALL be captured and displayed

#### Scenario: AbortError is silently ignored
- **WHEN** proof generation is aborted due to navigation
- **THEN** no error SHALL be shown

#### Scenario: mintDate and formatTokenId are pure formatters
- **WHEN** `mintDate` is called with a timestamp
- **THEN** it SHALL return a formatted date string
- **WHEN** `formatTokenId` is called with a token ID
- **THEN** it SHALL return a shortened display format

### Requirement: Event detail sheet computes URLs and handles touch dismiss
The `EventDetailSheet` component SHALL compute Google Maps and Calendar URLs and support touch drag-to-dismiss with a 100px threshold.

#### Scenario: Google Maps URL construction
- **WHEN** the sheet is opened with an event that has a venue name
- **THEN** `googleMapsUrl` SHALL return a valid Google Maps search URL for the venue

#### Scenario: Google Calendar URL construction
- **WHEN** the sheet is opened with an event
- **THEN** `calendarUrl` SHALL return a Google Calendar URL with correct start and end times

#### Scenario: Touch drag exceeding threshold closes sheet
- **WHEN** a touch drag moves more than 100px downward
- **THEN** the sheet SHALL close

#### Scenario: Touch drag below threshold keeps sheet open
- **WHEN** a touch drag moves less than 100px
- **THEN** the sheet SHALL remain open

### Requirement: Test mock helpers cover all tested DI interfaces
The test helper library SHALL provide typed mock factories for all DI interfaces used across the test suite.

#### Scenario: Mock router factory
- **WHEN** `createMockRouter` is called
- **THEN** it SHALL return a `Partial<IRouter>` with `load` as a Vitest spy

#### Scenario: Mock toast service factory
- **WHEN** `createMockToastService` is called
- **THEN** it SHALL return a `Partial<IToastService>` with `show` as a Vitest spy

#### Scenario: Mock error boundary factory
- **WHEN** `createMockErrorBoundary` is called
- **THEN** it SHALL return a `Partial<IErrorBoundaryService>` with `captureError` and `dismiss` as Vitest spies

### Requirement: Timer cleanup uses afterEach unconditionally
All tests that use `vi.useFakeTimers()` SHALL restore real timers in `afterEach`, never inside individual `it()` blocks.

#### Scenario: Fake timers restored after each test
- **WHEN** a test suite uses `vi.useFakeTimers()` in `beforeEach`
- **THEN** `vi.useRealTimers()` SHALL be called in `afterEach`

#### Scenario: Mocks restored after each test
- **WHEN** a test suite uses mock spies
- **THEN** `vi.restoreAllMocks()` SHALL be called in `afterEach`

## MODIFIED Requirements

### Requirement: Coverage reporting is configured
Vitest SHALL be configured with V8 coverage reporting with raised thresholds reflecting the expanded test suite.

#### Scenario: Running tests with coverage
- **WHEN** `vitest --coverage` is executed
- **THEN** a coverage report SHALL be generated showing statement, branch, and function coverage

#### Scenario: Coverage thresholds enforce minimum levels
- **WHEN** coverage falls below thresholds (statements: 55%, branches: 75%, functions: 55%, lines: 55%)
- **THEN** the coverage check SHALL fail
