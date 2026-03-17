## 1. Extract Controllers from DiscoveryRoute

- [x] 1.1 Create `SearchController` class (`src/routes/discovery/search-controller.ts`) — owns `searchQuery`, `isSearchMode`, `searchResults`, `isSearching`, debounce timer, `performSearch()`, `clearSearch()`, `exitSearchMode()`
- [x] 1.2 Create `GenreFilterController` class (`src/routes/discovery/genre-filter-controller.ts`) — owns `activeTag`, `isLoadingTag`, `onGenreSelected()`, `reloadWithTag()`
- [x] 1.3 Create `FollowOrchestrator` class (`src/routes/discovery/follow-orchestrator.ts`) — owns `followedArtists`, optimistic follow/rollback, follow RPC call, `checkLiveEvents()`
- [x] 1.4 Create `ConcertSearchTracker` class (`src/routes/discovery/concert-search-tracker.ts`) — owns `concertSearchStatus`, `completedSearchCount`, `concertGroupCount`, `searchConcertsWithTimeout()`, `verifyConcertData()`

## 2. Create BubbleManager

- [x] 2.1 Create `BubbleManager` class (`src/routes/discovery/bubble-manager.ts`) — wraps `BubblePool`, coordinates with `DnaOrbCanvas` for add/remove/evict/spawn operations
- [x] 2.2 Implement coordinated eviction: `addBubbles()` evicts oldest physics bodies via `fadeOutBubbles()` before adding new ones, ensuring pool and physics stay in sync
- [x] 2.3 Implement `spawnAndAbsorbAfterSearch()` with `requestAnimationFrame` guard to defer canvas reads until element is visible (fixes the display:none bug)
- [x] 2.4 Change `BubblePool.evictOldest()` from in-place `splice()` to immutable return (new array reference for Aurelia change detection)

## 3. Refactor DiscoveryRoute

- [x] 3.1 Wire controllers into `DiscoveryRoute` — instantiate `SearchController`, `GenreFilterController`, `FollowOrchestrator`, `ConcertSearchTracker`, `BubbleManager` in constructor/loading
- [x] 3.2 Delegate all handler methods to controllers — `onSearchQueryChanged` → `SearchController`, `onGenreSelected` → `GenreFilterController`, `onArtistSelected`/`onFollowFromSearch` → `FollowOrchestrator` + `BubbleManager`, `onNeedMoreBubbles` → `BubbleManager`
- [x] 3.3 Remove all state properties that moved to controllers (search*, genre*, followed*, concert*)
- [x] 3.4 Update `discovery-route.html` template bindings to reference controller properties (e.g., `search.query`, `search.results`, `genre.activeTag`)

## 4. Unit Tests

- [x] 4.1 Write unit tests for `SearchController` — debounce behavior, search execution, clear/exit, stale response handling
- [x] 4.2 Write unit tests for `GenreFilterController` — tag selection, tag deselection, loading state, error handling
- [x] 4.3 Write unit tests for `FollowOrchestrator` — optimistic update, rollback on failure, duplicate follow prevention
- [x] 4.4 Write unit tests for `ConcertSearchTracker` — search status tracking, timeout handling, completion detection, `verifyConcertData`
- [x] 4.5 Write unit tests for `BubbleManager` — pool↔physics sync on add/remove/evict, capacity enforcement, canvas-ready guard for search-follow absorption
- [x] 4.6 Update existing `BubblePool` tests for immutable `evictOldest()` behavior

## 5. Integration Verification

- [x] 5.1 Update existing discovery route tests to work with new controller-based architecture
- [x] 5.2 Run `make check` (lint + format + typecheck + unit tests) and fix any issues
- [x] 5.3 Manual E2E verification: bubble tap follow, search follow absorption, genre filter, onboarding flow
