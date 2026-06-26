# Tasks — Reconcile the analytics catalogue

## 1. Frontend: rename the feed click-through event

- [ ] 1.1 In `frontend/src/services/analytics-events.ts`, rename the event constant `ConcertRecommendationClicked` → `ConcertFeedCardTapped` and its value `'concert.recommendation.clicked'` → `'concert.feed.card.tapped'`.
- [ ] 1.2 Rename the `ConcertRecommendationClickedProps` type → `ConcertFeedCardTappedProps`, keeping the `position` property.
- [ ] 1.3 Update the props-map entry key `'concert.recommendation.clicked'` → `'concert.feed.card.tapped'` to point at the renamed props type.
- [ ] 1.4 Rename the `EventSource` union member `'recommendation'` → `'feed'`.
- [ ] 1.5 Update the doc comments that describe the event as a recommendation click so they describe a concert-feed card tap.
- [ ] 1.6 In `frontend/src/components/live-highway/event-card.ts` (call site ~L57-67), update `Events.ConcertRecommendationClicked` → `Events.ConcertFeedCardTapped`, preserving the `position` property and the `if (this.position !== null)` CTR guard.
- [ ] 1.7 In `frontend/src/routes/dashboard/dashboard-route.ts` (~L369), update the source tag `'recommendation'` → `'feed'`.

## 2. Backend: delete the phantom impression event

- [ ] 2.1 In `backend/internal/usecase/analytics_events.go`, delete the `EventConcertRecommendationServed` constant (and its doc comment).
- [ ] 2.2 Delete the `EventConcertRecommendationServed` entry from the `knownBackendEvents` allowlist.
- [ ] 2.3 Confirm by grep that no publisher references the deleted constant.

## 3. Backend: add the `zero_results` OTel outcome

- [ ] 3.1 In `backend/internal/infrastructure/telemetry/business_metrics.go`, document that `RecordConcertSearch` accepts `success`, `zero_results`, and `error` for the `status` attribute on `concert.search.count`.
- [ ] 3.2 In `backend/internal/usecase/concert_uc.go` `executeSearch`, record `zero_results` instead of `success` when a successful run yields no new concerts, keeping `error` for failures and `success` for non-empty results.

## 4. Catalogue edits

- [ ] 4.1 In `docs/analytics/event-catalog.md`, remove the `concert.recommendation.served` row.
- [ ] 4.2 Replace the `concert.recommendation.clicked` row with a `concert.feed.card.tapped` row (FE; properties `concert_id`, `artist_id`, `position`, `trace_id?`; consumer: feed CTR).
- [ ] 4.3 Remove the `concert.search.completed` row.
- [ ] 4.4 Rename the "Recommendation effectiveness" funnel to a feed-CTR funnel built on `concert.feed.card.tapped` → `concert.detail.viewed`.

## 5. Verification

- [ ] 5.1 Frontend: `make check` passes (lint + typecheck + tests) with the renamed event and source union.
- [ ] 5.2 Backend: `make check` passes with the deleted constant and the new `zero_results` outcome.
- [ ] 5.3 `openspec validate reconcile-analytics-catalogue --strict` is green.
