## 1. Setup

- [x] 1.1 Install `@aurelia/state` package
- [x] 1.2 Define `AppState` interface and `initialState` in `src/state/app-state.ts`
- [x] 1.3 Define `AppAction` discriminated union type in `src/state/actions.ts`

## 2. Reducer

- [x] 2.1 Implement `appReducer` in `src/state/reducer.ts` handling all onboarding actions
- [x] 2.2 Implement guest artist action handlers in `appReducer` (follow, unfollow, setUserHome, clearAll)
- [x] 2.3 Write unit tests for `appReducer` (all action types + unknown action passthrough)

## 3. Middleware

- [x] 3.1 Implement persistence middleware (After) in `src/state/middleware.ts` — write onboarding step, guest follows, guest home to localStorage
- [x] 3.2 Implement `loadPersistedState()` function to hydrate initial state from localStorage
- [x] 3.3 Implement logging middleware (Before, dev-only) in `src/state/middleware.ts`
- [x] 3.4 Write unit tests for persistence middleware

## 4. Store Registration

- [x] 4.1 Register `StateDefaultConfiguration.init()` in `main.ts` with merged state, reducer, and middleware

## 5. Migrate OnboardingService

- [x] 5.1 Refactor `OnboardingService` as thin Store facade (retaining callbacks)
- [x] 5.2 Update `DiscoverPage` to use Store for guest follow count
- [x] 5.3 Update `Dashboard` to use Store for guest home dispatch
- [x] 5.4 MyArtistsPage unchanged (uses OnboardingService facade)
- [x] 5.5 AppShell unchanged (uses OnboardingService facade)
- [x] 5.6 Rewrite onboarding-related unit tests to use Store

## 6. Migrate LocalArtistClient

- [x] 6.1 Refactor `LocalArtistClient` as thin Store facade
- [x] 6.2 Update `FollowServiceClient` to read guest follows from Store
- [x] 6.3 Update `user-home-selector` component to dispatch `guest/setUserHome` for guest users
- [x] 6.4 Rewrite `LocalArtistClient` unit tests as Store-based tests

## 7. Migrate GuestDataMergeService

- [x] 7.1 Update `GuestDataMergeService` to read guest data from `store.getState().guestArtists`
- [x] 7.2 Update merge completion to dispatch `guest/clearAll` instead of manual localStorage cleanup
- [x] 7.3 Update fresh tutorial start (LP) to dispatch `guest/clearAll` and `onboarding/reset`
- [x] 7.4 Update GuestDataMergeService unit tests

## 8. Cleanup

- [x] 8.1 Remove manual `StorageKeys` entries for onboarding step, guest follows, and guest home (now handled by middleware)
- [x] 8.2 Remove `migrateStorageKeys()` entries for migrated keys (not applicable — legacy migration still relevant)
- [x] 8.3 Run full lint and test suite (`make check`)
