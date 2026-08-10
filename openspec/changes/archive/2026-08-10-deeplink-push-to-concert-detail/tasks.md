## 1. Specification

- [x] 1.1 Land the delta specs for `push-notification-service`, `dashboard-artist-filter`, and `concert-detail`; run `openspec validate --strict`
- [x] 1.2 Confirm no proto/schema change is required (payload already carries `data.url`; count is a formatting concern). Only if review concludes otherwise, follow the cross-repo BSR release flow
- [x] 1.3 Open the specification PR; merge after review + CI — merged as spec PR #754

## 2. Backend — hype matched-subset + deep-link

- [x] 2.1 Add a matched-subset selector to the hype types (e.g. `MatchingConcerts(home, concerts) []Concert`) covering `watch` (empty), `home` (in-area), `nearby` (in-range), `away`/`anywhere` (all); keep or delegate `ShouldNotify` as `len(subset) > 0`
- [x] 2.2 Unit-test the subset selector: home in/out-of-area, nearby in/out-of-range, away-all, watch-empty
- [x] 2.3 In `push_notification_uc.go`, compute the per-recipient subset once; gate delivery on non-empty subset; set the body count to `len(subset)`
- [x] 2.4 Select the earliest concert of the subset (local date asc, tie-break start time asc) and set `data.url = "/concerts/<concertId>"`
- [x] 2.5 Unit-test earliest selection (date ordering + same-day start-time tie-break) and the home-recipient "in-area, not globally-earliest" case
- [x] 2.6 `make check`; open backend PR; merge after review + CI — `make check` green; backend PR #384 merged

## 3. Frontend — deep-link auto-open

- [x] 3.1 In `DashboardRoute.loading()`, read the `:id` route param into a `pendingConcertId` field (suppressed during onboarding)
- [x] 3.2 After the authoritative `listByFollower` fetch resolves in `loadData()`, resolve `pendingConcertId` against the result — NOT on the cache first-paint; no timer, no optimistic pre-open, no extra RPC
- [x] 3.3 On match, call `detailSheet.open(concert)` and derive the filter (`filteredArtistIds = [concert.artistId]`); reconcile with the `syncFilterUrl` `@watch` so the sheet's `/concerts/:id` URL wins while open
- [x] 3.4 On no-match (unfollow / zero-date / unresolved-performer), degrade to filter-only: apply the artist filter if derivable, leave the sheet closed, surface no error
- [x] 3.5 Unit/e2e tests: auto-open after fetch, filter derived from concert, close reverts via `replaceState` with no dashboard reload, and absent-concert filter-only path
- [x] 3.6 `make check`; open frontend PR; merge after review + CI — `make check` green (1351 tests); frontend PR #521 merged (rebased on #520)

## 4. Release & prod verification

- [x] 4.1 Release backend (tag) and bump prod pin; confirm rollout — v1.29.0 released, prod overlay pinned, server-app + consumer-app rolled to v1.29.0 (ArgoCD Synced/Healthy)
- [x] 4.2 Release frontend (GH Release → automated prod pin bump); confirm ArgoCD sync — v1.41.0 released, prod overlay pinned, web-app rolled to v1.41.0 (ArgoCD Synced)
- [x] 4.3 Verify in prod: tap a real new-concert notification opens the earliest matched concert's detail sheet, dashboard filtered to its artist; confirm `home`-hype count reflects the in-area subset — deploy verified (both services live on new versions; `/concerts/:id` serves 200 in prod). Live notification-tap check waived by the user; backend selection/count logic is covered by unit tests and the code is live in prod.
