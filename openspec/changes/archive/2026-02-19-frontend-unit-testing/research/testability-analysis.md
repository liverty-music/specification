# Testability Analysis by Component

## Test Priority Matrix (Value / Effort)

| Priority | File | Type | Logic | Effort |
|----------|------|------|-------|--------|
| 1 | `color-generator.ts` | Pure function | Hash-to-color mapping | Trivial |
| 2 | `dashboard-service.ts` | Service | Date grouping, concert mapping, parallel fetch | Medium |
| 3 | `loading-sequence-service.ts` | Service | Retry, batching, timeout, abort | Medium |
| 4 | `toast-notification.ts` | Service | Timer-based show/dismiss | Easy |
| 5 | `onboarding-service.ts` | Service | Auth check, redirect branching | Easy |
| 6 | `live-highway.ts` | Component | isEmpty getter, event delegation | Trivial |
| 7 | `event-card.ts` | Component | Color, date format, click event | Easy |
| 8 | `artist-discovery-service.ts` | Service | Follow state, dedup, orbIntensity | Medium |
| 9 | `my-app.ts` | Component | showNav route logic | Easy |
| 10 | `auth-status.ts` | Component | Pure delegation to IAuthService | Trivial |

## Common DI Pattern

All services use Aurelia `resolve()` in field initializers:
```typescript
export class SomeService {
  private readonly logger = resolve(ILogger).scopeTo('SomeService')
  private readonly dep = resolve(ISomeDep)
}
```

Testing approach: Use `DI.createContainer()` + `Registration.instance()` to provide mocks.

## Service-Specific Notes

### dashboard-service.ts
- Rich business logic: `concertToLiveEvent` (date/time formatting), `groupByDate` (sort/group)
- `toLocaleDateString('ja-JP', ...)` - locale-dependent output
- `Promise.allSettled` for parallel fetching
- Dependencies: `IConcertService`, `IArtistServiceClient`, `ILogger`

### loading-sequence-service.ts
- Retry with 1 attempt, batching (BATCH_SIZE=5), timeout (10s), minimum display (3s)
- `Date.now()` and `setTimeout` - needs `vi.useFakeTimers()`
- `AbortController` patterns
- Dependencies: `IArtistDiscoveryService`, `IConcertService`, `ILogger`

### onboarding-service.ts
- Two public methods with clear branching
- `hasCompletedOnboarding` checks followed artists count
- `redirectBasedOnStatus` gates on auth.ready, checks auth, routes
- Dependencies: `IAuthService`, `IArtistServiceClient`, `IRouter`, `ILogger`

### toast-notification.ts
- No DI dependencies (just `DI` for interface registration)
- Uses `requestAnimationFrame` + nested `setTimeout`
- Simple state management: `toasts` array, auto-increment ID

### artist-discovery-service.ts
- Mutable public state: `availableBubbles`, `followedArtists`, `orbIntensity`
- `seenArtistNames` Set for deduplication
- `Math.random()` in `toBubble` (non-deterministic radius)
- Constructor creates RPC client (side effect)
- **Bug**: missing `this.` on `artistClient` in `listFollowedFromBackend`

### event-card.ts
- `resolve(INode)` for DOM element access
- `artistColor` is pure function delegation
- `formattedDate` uses `toLocaleDateString('ja-JP')`
- Dispatches `CustomEvent` on host element

### my-app.ts
- `showNav` computed from `router.activeNavigation?.path`
- `fullscreenRoutes` array matching

## Cross-Cutting Concerns

1. **`import.meta.env`**: Services read env vars at module level. Vitest handles this via Vite config.
2. **Constructor side effects**: Most service constructors create gRPC clients. Module mocking needed.
3. **Locale formatting**: `ja-JP` locale in date formatting. Tests should use snapshot or explicit assertions.
4. **Shadow DOM**: Vite plugin sets `defaultShadowOptions: 'open'`. Component tests may need shadowRoot traversal.
