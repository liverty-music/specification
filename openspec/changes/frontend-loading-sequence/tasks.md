## 1. Loading Sequence Component

- [ ] 1.1 Create `LoadingSequence` Aurelia 2 component with phased text animation (3 phases with crossfade transitions)
- [ ] 1.2 Implement phase timing logic: Phase 1 (0-2s), Phase 2 (2-5s), Phase 3 (5s+)
- [ ] 1.3 Add mobile-first responsive styling (centered content, full-screen layout)

## 2. Data Aggregation Orchestration

- [ ] 2.1 Call `ListFollowedArtists` on component activation to retrieve followed artist list
- [ ] 2.2 Implement parallel `SearchNewConcerts` calls using `Promise.allSettled()` with batching (groups of 5)
- [ ] 2.3 Add `AbortController` with 10-second global timeout
- [ ] 2.4 Implement minimum 3-second display duration using `Promise.all([aggregation, delay(3000)])`

## 3. Navigation & Route Guards

- [ ] 3.1 Register `/onboarding/loading` route with `LoadingSequence` component
- [ ] 3.2 Implement navigation guard: redirect unauthenticated users to `/`, authenticated-with-artists to `/dashboard`, authenticated-without-artists to `/onboarding/discover`
- [ ] 3.3 Navigate to `/dashboard` on aggregation completion or timeout
