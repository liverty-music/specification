# Frontend Test Coverage Analysis Report

**Date**: 2026-02-25
**Repository**: `liverty-music/frontend`
**Branch**: `frontend-testing`

---

## 1. Current Test Implementation Status

### Test Infrastructure

| Item | Status |
|------|--------|
| Unit/Integration Framework | Vitest v2.1.8 (jsdom) |
| E2E Framework | Playwright v1.49.1 (configured, 0 tests) |
| Coverage Provider | @vitest/coverage-v8 |
| CI Pipeline | lint → typecheck → vitest --coverage → security audit |
| Codecov Integration | Active (PR comments + upload) |

### Coverage Thresholds (current)

```
statements: 20%  |  branches: 70%  |  functions: 30%  |  lines: 20%
```

### Existing Test Files (14 files)

| Test File | Target | Key Test Cases |
|-----------|--------|----------------|
| `test/my-app.spec.ts` | `MyApp` root component | `showNav` computed property |
| `test/auth-service.spec.ts` | `AuthService` | OIDC signIn/signUp/signOut/handleCallback |
| `test/components/area-selector-sheet.spec.ts` | `AreaSelectorSheet` | open/close, region/prefecture selection, localStorage |
| `test/components/auth-status.spec.ts` | `AuthStatus` | signIn/signUp/signOut delegation |
| `test/components/live-highway/color-generator.spec.ts` | `artistColor()` | HSL output, determinism, unicode |
| `test/components/live-highway/event-card.spec.ts` | `EventCard` | backgroundColor, formattedDate, onClick |
| `test/components/live-highway/live-highway.spec.ts` | `LiveHighway` | isEmpty, onEventSelected |
| `test/routes/auth-callback.spec.ts` | `AuthCallback` | canLoad, sign-up/sign-in flows, error handling |
| `test/routes/my-artists-page.spec.ts` | `MyArtistsPage` | loading, swipe-to-unfollow, long-press, undo |
| `test/services/dashboard-service.spec.ts` | `DashboardService` | event grouping, region-lane assignment, sorting |
| `test/services/toast-notification.spec.ts` | `ToastNotification` | show, auto-dismiss, removal, multiple toasts |
| `test/value-converters/date.spec.ts` | `DateValueConverter` | short/long/relative formats, edge cases |

### Test Helpers

| Helper | Purpose |
|--------|---------|
| `test/helpers/create-container.ts` | Aurelia DI container factory with mock logger |
| `test/helpers/mock-auth.ts` | Mock `IAuthService` with vi.fn() spies |
| `test/helpers/mock-logger.ts` | Mock `ILogger` with vi.fn() spies |
| `test/helpers/mock-rpc-clients.ts` | Mock ConcertService, ArtistServiceClient, ArtistDiscoveryService |

### Coverage Exclusions (vitest.config.ts)

```
src/*-page.ts              # top-level page components (env teardown issues)
src/components/dna-orb/**  # canvas components (deferred - complex setup)
src/services/auth-service.ts  # window.location module-level dependency
```

---

## 2. Source File Inventory vs Test Coverage

### Legend

- ✅ = test exists
- ❌ = no test
- ⬜ = intentionally excluded / not applicable

### Services (16 files)

| File | LOC | Test | Coverage Excluded |
|------|-----|------|-------------------|
| `services/auth-service.ts` | ~150 | ✅ | Yes (window.location) |
| `services/dashboard-service.ts` | ~120 | ✅ | No |
| `services/artist-discovery-service.ts` | 251 | ❌ | No |
| `services/loading-sequence-service.ts` | 174 | ❌ | No |
| `services/error-boundary-service.ts` | 184 | ❌ | No |
| `services/grpc-transport.ts` | 127 | ❌ | No |
| `services/connect-error-router.ts` | 61 | ❌ | No |
| `services/proof-service.ts` | 202 | ❌ | No |
| `services/push-service.ts` | 102 | ❌ | No |
| `services/concert-service.ts` | 72 | ❌ | No |
| `services/notification-manager.ts` | 74 | ❌ | No |
| `services/entry-service.ts` | 43 | ❌ | No |
| `services/global-error-handler.ts` | 31 | ❌ | No |
| `services/ticket-service.ts` | 33 | ❌ | No |
| `services/artist-service-client.ts` | 33 | ❌ | No |
| `services/user-service.ts` | 26 | ❌ | No |

### Routes (9 files)

| File | LOC | Test |
|------|-----|------|
| `routes/auth-callback.ts` | ~80 | ✅ |
| `routes/my-artists/my-artists-page.ts` | ~150 | ✅ |
| `routes/discover/discover-page.ts` | 254 | ❌ |
| `routes/onboarding-loading/loading-sequence.ts` | 183 | ❌ |
| `routes/artist-discovery/artist-discovery-page.ts` | 145 | ❌ |
| `routes/tickets/tickets-page.ts` | 120 | ❌ |
| `routes/dashboard.ts` | 72 | ❌ |
| `routes/settings/settings-page.ts` | 78 | ❌ |
| `routes/not-found/not-found-page.ts` | 1 | ⬜ (empty class) |

### Components (19 files)

| File | LOC | Test |
|------|-----|------|
| `components/area-selector-sheet/area-selector-sheet.ts` | ~120 | ✅ |
| `components/auth-status.ts` | ~40 | ✅ |
| `components/live-highway/color-generator.ts` | ~30 | ✅ |
| `components/live-highway/event-card.ts` | ~60 | ✅ |
| `components/live-highway/live-highway.ts` | ~80 | ✅ |
| `components/toast-notification/toast-notification.ts` | ~50 | ✅ |
| `components/live-highway/event-detail-sheet.ts` | 99 | ❌ |
| `components/region-setup-sheet/region-setup-sheet.ts` | 115 | ❌ |
| `components/error-banner/error-banner.ts` | 51 | ❌ |
| `components/notification-prompt/notification-prompt.ts` | 49 | ❌ |
| `components/bottom-nav-bar/bottom-nav-bar.ts` | 42 | ❌ |
| `components/inline-error/inline-error.ts` | 22 | ❌ |
| `components/dna-orb/dna-orb-canvas.ts` | ~200 | ⬜ (canvas, deferred) |
| `components/dna-orb/absorption-animator.ts` | ~100 | ⬜ (canvas, deferred) |
| `components/dna-orb/bubble-physics.ts` | ~150 | ⬜ (canvas, deferred) |
| `components/dna-orb/orb-renderer.ts` | ~200 | ⬜ (canvas, deferred) |
| `components/icons/*.ts` (x4) | ~10 each | ⬜ (SVG-only) |

### Other

| File | LOC | Test |
|------|-----|------|
| `hooks/auth-hook.ts` | 35 | ❌ |
| `value-converters/date.ts` | ~60 | ✅ |
| `my-app.ts` | ~40 | ✅ |
| `workers/proof.worker.ts` | ~30 | ⬜ (Web Worker) |

---

## 3. Test Recommendations by Priority

### Priority 1: HIGHEST (Critical business logic + High complexity)

These files have the highest risk-to-coverage ratio. A bug in any of them breaks core user flows.

#### 3.1 `hooks/auth-hook.ts` — Security Boundary

| Test Case | Description |
|-----------|-------------|
| Public route bypass | `data.auth === false` → allow navigation without auth check |
| Authenticated user | `isAuthenticated === true` → allow navigation |
| Unauthenticated user | `isAuthenticated === false` → redirect to `/welcome`, show toast |
| Auth ready timing | Verify `canLoad` awaits `authService.ready` before checking auth |

**Why**: This is the **security boundary** for the entire app. All authenticated routes depend on it. A bypass here exposes private content.

---

#### 3.2 `services/loading-sequence-service.ts` — Onboarding Data Pipeline

| Test Case | Description |
|-----------|-------------|
| Happy path | Fetch artists → batch concert search → return `complete` result |
| Partial results | Some concert searches fail → return `partial` with errors |
| Total failure | Artist fetch fails after retry → return `failed` |
| Retry on first failure | First `getFollowedArtists` fails → retry once → succeed |
| Global timeout (10s) | Abort all in-flight requests after 10 seconds |
| Minimum display time (3s) | Even if data loads in 100ms, wait at least 3 seconds |
| Batch size (5) | Artists are processed in parallel batches of 5 |
| AbortSignal propagation | External abort cancels the entire pipeline |
| AbortSignal in `delay` | Signal aborted during delay → reject immediately, cleanup timer |

**Why**: Controls the onboarding→dashboard transition. Without correct batching/timeout/retry, new users see empty dashboards or stuck loading screens.

---

#### 3.3 `services/connect-error-router.ts` — gRPC Interceptor Stack

| Test Case | Description |
|-----------|-------------|
| `createAuthRetryInterceptor`: Unauthenticated → silent refresh | Intercept `Code.Unauthenticated`, call `signinSilent`, retry |
| `createAuthRetryInterceptor`: Refresh fails → redirect | `signinSilent` throws → redirect to `/welcome` |
| `createAuthRetryInterceptor`: Non-auth error → pass through | Other error codes are not intercepted |
| `createRetryInterceptor`: Unavailable → exponential backoff | Retry with increasing delay on `Code.Unavailable` |
| `createRetryInterceptor`: DeadlineExceeded → retry | Retry on `Code.DeadlineExceeded` |
| `createRetryInterceptor`: Max retries exhausted | After N retries, throw the original error |
| `createRetryInterceptor`: Non-retryable error → no retry | E.g., `Code.NotFound` → throw immediately |

**Why**: Every single gRPC call passes through these interceptors. Bugs here cause cascading auth failures or infinite redirect loops.

---

#### 3.4 `services/artist-discovery-service.ts` — Core Discovery Engine

| Test Case | Description |
|-----------|-------------|
| `loadInitialArtists` | Fetch from backend → populate bubbles, track seen artists |
| `reloadWithTag` | Clear bubbles → fetch with genre tag → repopulate |
| `followArtist` / `unfollowArtist` | Optimistic update → backend call → rollback on failure |
| Follow retry (1 attempt) | First follow fails → retry once → succeed |
| Follow rollback | Retry also fails → revert optimistic state |
| Deduplication (3 sets) | Same artist by name/id/mbid → not added to bubbles twice |
| `searchArtists` | Delegates to backend with AbortSignal |
| `getSimilarArtists` | Fetch similar → deduplicate → return new bubbles |
| `evictOldest` | Remove oldest N bubbles from the list |
| `orbIntensity` | Compute intensity based on followed artist count |
| `clearSeenSets` | Reset deduplication state |

**Why**: The gateway to the onboarding flow. If follow/unfollow is broken, users cannot build their artist list.

---

#### 3.5 `services/grpc-transport.ts` — Transport Factory

| Test Case | Description |
|-----------|-------------|
| Auth header injection | `authInterceptor` adds `Authorization: Bearer <token>` |
| No token available | `getUser()` returns null → no auth header added |
| Interceptor ordering | Auth runs before retry (not after) |
| OTEL span creation | `otelInterceptor` creates span with method name |
| OTEL error recording | Failed call → span records error status |
| Logging interceptor | Logs method name, duration, and response status |

**Why**: All backend communication goes through this transport. Auth injection and interceptor ordering bugs break everything.

---

#### 3.6 `services/proof-service.ts` — ZK Proof Generation

| Test Case | Description |
|-----------|-------------|
| Pure utilities: `bytesToDecimal` | Byte array → BigInt decimal string |
| Pure utilities: `uuidToFieldElement` | UUID string → field element string |
| Pure utilities: `bytesToHex` | Byte array → hex string |
| `verifyCircuitIntegrity` | SHA-256 of fetched file matches hardcoded hash |
| `verifyCircuitIntegrity` failure | Hash mismatch → throw with descriptive error |
| `generateEntryProof` happy path | Fetch Merkle path → download circuits → verify → generate proof |
| Worker timeout/abort | AbortSignal propagation into worker |
| Progress callback | Progress is reported at each stage |

**Why**: Core ZK ticketing product feature. The pure utility functions are immediately testable with zero mocking.

---

#### 3.7 `routes/onboarding-loading/loading-sequence.ts` — Onboarding Route

| Test Case | Description |
|-----------|-------------|
| `canLoad`: has followed artists | → allow navigation (return true) |
| `canLoad`: no followed artists, backend has artists | → redirect to `/` |
| `canLoad`: no followed artists, backend empty | → redirect to `/artist-discovery` |
| `canLoad`: backend check fails | → redirect to `/artist-discovery` |
| Aggregation result: `complete` | → navigate to `/dashboard` |
| Aggregation result: `partial` | → navigate to `/dashboard` (with partial data) |
| Aggregation result: `failed` | → capture error, navigate to `/dashboard` |
| Phase animation timing | 3 phases animate in sequence with correct durations |

**Why**: The `canLoad` guard has 5 distinct routing outcomes. Incorrect routing sends users to wrong screens.

---

### Priority 2: HIGH (Critical importance or High complexity)

#### 3.8 `services/concert-service.ts`

| Test Case | Description |
|-----------|-------------|
| `listConcerts` | Fetch concerts for a given artist ID |
| `listByFollower` | Fetch concerts for authenticated user's followed artists |
| `searchNewConcerts` | Trigger backend concert search |
| AbortSignal propagation | All methods forward AbortSignal to gRPC client |
| Error forwarding | Backend errors are properly thrown |

---

#### 3.9 `services/error-boundary-service.ts`

| Test Case | Description |
|-----------|-------------|
| `captureError` | Creates `AppError`, adds to history, sets `currentError` |
| Error history cap | History does not exceed max size |
| `addBreadcrumb` | Breadcrumbs are ring-buffered |
| `generateReport` | Markdown output includes error, breadcrumbs, environment |
| `sanitize` (static) | Redacts Bearer tokens, JWTs, OIDC params |
| `buildGitHubIssueUrl` | Generates valid pre-filled GitHub Issue URL |
| URL length capping | URL is truncated if it exceeds browser limits |
| `dismiss` | Clears `currentError` |

---

#### 3.10 `routes/dashboard.ts`

| Test Case | Description |
|-----------|-------------|
| Happy path load | `loadData` fetches grouped timeline from `DashboardService` |
| Stale data on reload failure | Old data remains visible, `isStale = true` |
| AbortError ignored | Navigation-triggered abort does not set error state |
| `retry` clears error and reloads | Error state cleared, data refetched |
| Region setup shown on first visit | `getStoredRegion()` returns null → show sheet |
| `onRegionSelected` triggers reload | After region selection, data is refetched |

---

#### 3.11 `routes/discover/discover-page.ts`

| Test Case | Description |
|-----------|-------------|
| Genre tag toggle: activate | Select tag → `reloadWithTag(tag)` |
| Genre tag toggle: deactivate | Deselect tag → `loadInitialArtists()` |
| Debounced search (300ms) | Input change → wait 300ms → `performSearch` |
| Stale response guard | Fast typing → only latest response is applied |
| `clearSearch` | Clears query, cancels pending search, restores bubbles |
| Follow from search results | `onFollowFromSearch` → follow artist + reload bubbles |
| Visibility-based canvas pause | Page hidden → pause DnaOrb, page visible → resume |

---

#### 3.12 `routes/artist-discovery/artist-discovery-page.ts`

| Test Case | Description |
|-----------|-------------|
| Initial load | `loadInitialArtists` called with AbortSignal |
| Artist selection → follow | `onArtistSelected` → follow + check live events |
| Guidance overlay auto-dismiss | Guidance dismisses after 5 seconds |
| Guidance fade animation | 400ms fade-out before removal |
| `retryLoad` | Clears error, reloads data |
| `onViewSchedule` navigation | Navigates to `/` |

---

#### 3.13 `routes/tickets/tickets-page.ts`

| Test Case | Description |
|-----------|-------------|
| Ticket list loading | Fetches tickets from `TicketService` |
| `mintDate` (pure) | Timestamp → formatted date string |
| `formatTokenId` (pure) | Token ID → shortened display format |
| `generateEntryCode` happy path | Proof generation → base64 encode → QR code → modal |
| `generateEntryCode` error handling | Proof failure → error state |
| AbortError discrimination | Navigation abort → no error shown |
| QR modal dismiss | `dismissQr` clears QR state |

---

#### 3.14 `components/live-highway/event-detail-sheet.ts`

| Test Case | Description |
|-----------|-------------|
| `googleMapsUrl` (pure) | Correct Google Maps URL construction |
| `calendarUrl` (pure) | Correct Google Calendar URL with start/end times |
| `backgroundColor` (pure) | Correct HSL color from artist name |
| Touch drag-to-dismiss | Touch delta > 100px → close sheet |
| Touch drag below threshold | Touch delta < 100px → sheet stays open |
| Browser history management | `open` → pushState, `close` → replaceState |

---

### Priority 3: MEDIUM

#### 3.15 `services/push-service.ts`

| Test Case | Description |
|-----------|-------------|
| `subscribe` happy path | Permission granted → push subscription created → registered |
| `subscribe` permission denied | Returns without subscribing |
| `subscribe` no VAPID key | Returns early |
| `unsubscribe` | Unsubscribes push + unregisters with backend |
| Service worker readiness timeout | `getRegistration` times out → error |

---

#### 3.16 `routes/settings/settings-page.ts`

| Test Case | Description |
|-----------|-------------|
| Load stored area | localStorage → `selectedArea` |
| Toggle notifications on | Subscribe → update state |
| Toggle notifications off | Unsubscribe → update state |
| Toggle reentrancy guard | Rapid toggles don't cause double subscribe |
| Permission revoked externally | `loading` detects permission !== 'granted' → reset toggle |
| Sign out | Delegates to `authService.signOut` |

---

#### 3.17 `components/error-banner/error-banner.ts`

| Test Case | Description |
|-----------|-------------|
| Copy to clipboard | Calls `navigator.clipboard.writeText` |
| Report to GitHub | Opens GitHub Issue URL via `window.open` |
| Report cooldown (60s) | Second report within 60s → blocked |
| Dismiss | `dismiss()` clears error on `ErrorBoundaryService` |

---

#### 3.18 `components/bottom-nav-bar/bottom-nav-bar.ts`

| Test Case | Description |
|-----------|-------------|
| `isActive` basic match | Current path matches tab path → true |
| `isActive` dashboard sub-routes | `/concerts/123` → dashboard tab active |
| `isActive` no match | → false |
| `currentPath` null safety | Router not initialized → graceful fallback |

---

#### 3.19 `components/notification-prompt/notification-prompt.ts`

| Test Case | Description |
|-----------|-------------|
| Show when not dismissed + not granted | visible = true |
| Hide when dismissed | localStorage flag → visible = false |
| Hide when already granted | permission = 'granted' → visible = false |
| Enable → grant | Subscribe succeeds, permission granted → hide |
| Enable → deny | Subscribe fails with deny → show guidance |
| Dismiss persists to localStorage | `dismiss()` sets localStorage flag |

---

#### 3.20 `components/region-setup-sheet/region-setup-sheet.ts`

| Test Case | Description |
|-----------|-------------|
| Quick city selection | City → mapped prefecture → save |
| Full prefecture selection | Dropdown → save |
| `getStoredRegion` (static) | Reads from localStorage |
| Dialog open/close | `showModal()` / `close()` called |
| Backdrop click → close | Click outside sheet → close |

---

#### 3.21 `services/notification-manager.ts`

| Test Case | Description |
|-----------|-------------|
| Initial permission read | Reads `Notification.permission` |
| `requestPermission` | Calls `Notification.requestPermission()` → updates state |
| Live permission watch | `navigator.permissions.query` → listen for changes |
| `mapPermissionState` | Maps `PermissionState` → `NotificationPermission` |
| No Notification API | Graceful fallback when API unavailable |

---

### Priority 4: LOW

| File | Why Low |
|------|---------|
| `services/entry-service.ts` | Thin wrapper, 1 method, low complexity |
| `services/ticket-service.ts` | Thin wrapper, 1 method, low complexity |
| `services/artist-service-client.ts` | Pure DI plumbing, no logic |
| `services/global-error-handler.ts` | Pure wiring (window.onerror), no branching |
| `components/inline-error/inline-error.ts` | Trivial getter + callback delegation |

### Priority 5: SKIP

| File | Why Skip |
|------|----------|
| `services/user-service.ts` | No active consumers |
| `routes/not-found/not-found-page.ts` | Empty class (1 LOC) |
| `components/dna-orb/*` | Canvas components, intentionally deferred |
| `components/icons/*` | SVG-only, no logic |

---

## 4. E2E Test Gap

Playwright is configured but **zero e2e tests exist**. The CI pipeline has no e2e job.

### Recommended E2E scenarios (when ready)

| Scenario | Flow |
|----------|------|
| Onboarding happy path | Welcome → Auth → Artist Discovery → Loading → Dashboard |
| Dashboard concert browsing | Dashboard → Event detail sheet → Google Maps/Calendar links |
| Settings region change | Settings → Change region → Dashboard reloads with new region |
| Auth redirect | Unauthenticated user visits `/dashboard` → redirected to `/welcome` |

---

## 5. Architecture Diagram: Test Coverage Heatmap

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND APPLICATION                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─── ROUTES ──────────────────────────────────────────────────┐   │
│  │                                                              │   │
│  │  ✅ auth-callback    ✅ my-artists-page                     │   │
│  │  ❌ dashboard        ❌ discover-page                       │   │
│  │  ❌ artist-discovery ❌ loading-sequence                    │   │
│  │  ❌ tickets-page     ❌ settings-page                       │   │
│  │                                                              │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌─── HOOKS ───────┐  ┌─── COMPONENTS ────────────────────────┐   │
│  │                  │  │                                        │   │
│  │  ❌ auth-hook    │  │  ✅ area-selector  ✅ auth-status     │   │
│  │                  │  │  ✅ event-card     ✅ live-highway     │   │
│  └──────────────────┘  │  ✅ color-gen      ✅ toast-notif     │   │
│                         │  ❌ event-detail   ❌ bottom-nav      │   │
│                         │  ❌ error-banner   ❌ inline-error    │   │
│                         │  ❌ notif-prompt   ❌ region-setup    │   │
│                         │  ⬜ dna-orb (deferred)               │   │
│                         └──────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌─── SERVICES ────────────────────────────────────────────────┐   │
│  │                                                              │   │
│  │  ✅ auth-service (coverage excluded)                        │   │
│  │  ✅ dashboard-service                                       │   │
│  │  ❌ artist-discovery-service  ❌ loading-sequence-service   │   │
│  │  ❌ connect-error-router      ❌ grpc-transport             │   │
│  │  ❌ proof-service             ❌ error-boundary-service     │   │
│  │  ❌ concert-service           ❌ push-service               │   │
│  │  ❌ notification-manager      ❌ entry-service              │   │
│  │  ❌ ticket-service            ❌ artist-service-client      │   │
│  │  ❌ global-error-handler      ❌ user-service               │   │
│  │                                                              │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌─── VALUE CONVERTERS ────────────────────────────────────────┐   │
│  │  ✅ date                                                    │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─── E2E (Playwright) ───────────────────────────────────────┐   │
│  │  ❌ Zero tests written                                      │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

Legend: ✅ = tested  ❌ = untested  ⬜ = intentionally excluded
```

---

## 6. Summary Statistics

| Category | Total | Tested | Untested | Coverage % |
|----------|-------|--------|----------|------------|
| Services | 16 | 2 | 14 | 12.5% |
| Routes | 9 | 2 | 6 (+1 skip) | 22.2% |
| Components | 19 | 6 | 7 (+6 deferred/skip) | 31.6% |
| Hooks | 1 | 0 | 1 | 0% |
| Value Converters | 1 | 1 | 0 | 100% |
| E2E Scenarios | ∞ | 0 | — | 0% |
| **Total testable** | **40** | **11** | **28** | **27.5%** |

### Recommended Testing Order (by risk reduction)

1. `auth-hook.ts` — Security boundary, small file, huge impact
2. `loading-sequence-service.ts` — Complex async, critical onboarding path
3. `connect-error-router.ts` — Every gRPC call depends on it
4. `artist-discovery-service.ts` — Core discovery engine
5. `proof-service.ts` (pure utilities first) — ZK proof pure functions
6. `grpc-transport.ts` — All backend communication
7. `loading-sequence.ts` (route) — 5 routing outcomes in canLoad
8. `concert-service.ts` — Dashboard data pipeline
9. `error-boundary-service.ts` — Error reporting correctness
10. `dashboard.ts` (route) — Primary post-onboarding screen
