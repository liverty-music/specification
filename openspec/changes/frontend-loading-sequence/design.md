## Context

The onboarding flow has 4 steps: Landing Page → Artist Discovery → **Loading Sequence** → Dashboard. After the user follows artists in the Discovery step, the system must aggregate live event data before it can render the Dashboard. The backend already provides `SearchNewConcerts` (per-artist Gemini-powered search) and `ListFollowedArtists` RPCs. The Loading Sequence is a frontend-only concern that orchestrates these calls and provides an engaging waiting experience.

## Goals / Non-Goals

**Goals:**
- Display a phased animated loading screen with progressive messaging during data aggregation.
- Orchestrate parallel `SearchNewConcerts` calls for followed artists.
- Enforce a 10-second global timeout with graceful degradation.
- Ensure a minimum 3-second display time for the loading animation.
- Transition to Dashboard upon completion.

**Non-Goals:**
- Modifying the `SearchNewConcerts` backend implementation.
- Caching or persisting aggregation results on the frontend (backend handles persistence).
- Retry logic for failed searches (proceed with partial results).

## Decisions

### 1. Data Aggregation Strategy
**Decision**: Use `Promise.allSettled()` to fire `SearchNewConcerts` for all followed artists in parallel, wrapped in a global `AbortController` with 10-second timeout. If the initial `ListFollowedArtists` call fails, the system SHALL attempt a single retry before gracefully navigating to the Dashboard.
**Rationale**: `allSettled` ensures partial failures don't block the entire flow. Artists whose searches fail or timeout are simply excluded from the initial Dashboard render — the data can be fetched later. The retry logic for `ListFollowedArtists` prevents the loading screen from becoming stuck if the initial artist list retrieval fails.

```
┌──────────────────────────────────────────────────────┐
│                Loading Sequence                       │
│                                                       │
│  ListFollowedArtists()                               │
│       │                                               │
│       ▼                                               │
│  ┌────────────────────────────────────────┐           │
│  │  Promise.allSettled([                  │           │
│  │    SearchNewConcerts(artist_1),        │           │
│  │    SearchNewConcerts(artist_2),        │           │
│  │    ...                                │           │
│  │    SearchNewConcerts(artist_n),        │           │
│  │  ])                                   │           │
│  └────────────────────────────────────────┘           │
│       │                          │                    │
│       ▼                          ▼                    │
│   All settled              10s timeout fires          │
│       │                          │                    │
│       └──────────┬───────────────┘                    │
│                  ▼                                    │
│         min(3s) elapsed?                             │
│           yes → navigate(/dashboard)                 │
│           no  → wait remaining, then navigate        │
└──────────────────────────────────────────────────────┘
```

### 2. Animation Phases
**Decision**: Three sequential text phases with CSS transitions, independent of actual data loading progress.
**Rationale**: The phases are purely decorative ("benevolent deception"). Tying them to real progress would create unpredictable transitions. Fixed timing provides a polished experience.

| Phase | Timing | Message |
|-------|--------|---------|
| 1 | 0–2s | 「あなたのMusic DNAを構築中...」 |
| 2 | 2–5s | 「全国のライブスケジュールと照合中...」 |
| 3 | 5s+ | 「AIが最新のツアー情報を検索中... 🤖」 |

### 3. Navigation Guard
**Decision**: The loading sequence route SHALL only be accessible from the Artist Discovery step. Direct URL access SHALL redirect to the appropriate step based on auth/onboarding state.
**Rationale**: Prevents users from accidentally triggering redundant data aggregation by bookmarking or refreshing the loading URL.

### 4. Minimum Display Duration
**Decision**: Use `Promise.all([dataAggregation, minimumDelay(3000)])` to ensure both data loading and the minimum delay complete before navigating.
**Rationale**: Simple and race-condition-free. The 3-second minimum ensures users always see the animation, even on fast connections.

## Risks / Trade-offs

- **[Risk] Large number of followed artists causes timeout** → If a user follows 30+ artists, parallel searches may overwhelm the backend.
  - **Mitigation**: Batch searches in groups of 5 with sequential batches. The 10-second global timeout ensures the UI never blocks indefinitely.
- **[Trade-off] No real progress indication** → Users don't see which artists have been processed.
  - **Mitigation**: The phased messaging creates a sense of progress. Real progress bars are complex and may regress if searches fail.
- **[Risk] Route refresh triggers re-aggregation** → Refreshing the loading page could re-trigger all searches.
  - **Mitigation**: Navigation guard redirects direct access away from the loading route. On refresh, redirect to Dashboard (data was already persisted by backend).
