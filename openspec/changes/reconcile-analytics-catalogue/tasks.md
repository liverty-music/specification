# Tasks — Reconcile the analytics catalogue

## 1. Frontend: delete the redundant click event, ground the surface label

- [x] 1.1 In `frontend/src/services/analytics-events.ts`, delete the event constant `ConcertRecommendationClicked` / `'concert.recommendation.clicked'` from the `Events` map.
- [x] 1.2 Delete the `ConcertRecommendationClickedProps` type.
- [x] 1.3 Delete the props-map entry key `'concert.recommendation.clicked'`.
- [x] 1.4 Rename the `EventSource` union member `'recommendation'` → `'dashboard'` (still used by `concert.detail.viewed`).
- [x] 1.5 Update the doc comments (the `Events` usage example and any stale references) so no comment describes a recommendation click and the example uses `source: 'dashboard'`.
- [x] 1.6 In `frontend/src/components/live-highway/event-card.ts`, remove the analytics capture in `onClick`, the now-unused `IAnalyticsService` injection and `Events` import, and the `position` `@bindable` that fed only it; keep the `readonly` guard and `event-selected` dispatch.
- [x] 1.7 Remove the now-dead `position.bind="$index"` bindings in `frontend/src/components/live-highway/concert-highway.html`, and update the source tag at `frontend/src/routes/dashboard/dashboard-route.ts` `'recommendation'` → `'dashboard'`.
- [x] 1.8 Update the affected unit tests (`event-card.spec.ts`, `event-detail-sheet.spec.ts`): drop the deleted-event assertions and the unused analytics stub; use `source = 'dashboard'`.

## 2. Backend: delete the phantom impression event

- [x] 2.1 In `backend/internal/usecase/analytics_events.go`, delete the `EventConcertRecommendationServed` constant (and its doc comment).
- [x] 2.2 Delete the `EventConcertRecommendationServed` entry from the `knownBackendEvents` allowlist.
- [x] 2.3 Confirm by grep that no publisher references the deleted constant.

## 3. Backend: add the `zero_results` OTel outcome

- [x] 3.1 In `backend/internal/infrastructure/telemetry/business_metrics.go`, document that `RecordConcertSearch` accepts `success`, `zero_results`, and `error` for the `status` attribute on `concert.search.count`.
- [x] 3.2 In `backend/internal/usecase/concert_uc.go` `executeSearch`, record `zero_results` instead of `success` when a successful run yields no new concerts, keeping `error` for failures and `success` for non-empty results.

## 4. Catalogue edits (recommendation + search)

- [x] 4.1 In `docs/analytics/event-catalog.md`, remove the `concert.recommendation.served` row.
- [x] 4.2 Remove the `concert.recommendation.clicked` row (no replacement; the signal is covered by `concert.detail.viewed` with `source = 'dashboard'`).
- [x] 4.3 Remove the `concert.search.completed` row.
- [x] 4.4 Remove the now-empty "Recommendation effectiveness" funnel and renumber the remaining funnels.

## 5. Standardise the underlying-event identifier on `event_id`

- [x] 5.1 In `frontend/src/services/analytics-events.ts`, rename the `concert_id` property to `event_id` on `ConcertDetailViewedProps`, `TicketLotteryEntrySubmittedProps`, `TicketPurchaseInitiatedProps`, and `NotificationOpenedProps` (`concert_id?` → `event_id?`).
- [x] 5.2 Update the only emitting call site `frontend/src/components/live-highway/event-detail-sheet.ts` (`concert.detail.viewed`) to send `event_id`, and update `event-detail-sheet.spec.ts`.
- [x] 5.3 In `docs/analytics/event-catalog.md`, rename every `concert_id` column to `event_id` and drop `concert_id` from the PII-safety "OK" example list (`event_id` already present). Confirm by grep that no backend analytics code emits a `concert_id` property (RPC args, NATS payload fields, and `slog` keys are out of scope).

## 6. Delete the `account.signup.completed` phantom duplicate

- [x] 6.1 In `backend/internal/usecase/analytics_events.go`, delete the `EventAccountSignupCompleted` constant and its `knownBackendEvents` entry; confirm by grep no publisher references it.
- [x] 6.2 In `docs/analytics/event-catalog.md`, remove the `account.signup.completed` row and absorb its consumer (signup funnel, D7/D30 retention cohort) into the `user.created` row.
- [x] 6.3 In `frontend/src/services/analytics-events.ts`, repoint the `account.signup.started` doc-comment pairing from `account.signup.completed` to `user.created`.

## 7. Verification

- [x] 7.1 Frontend: `make check` passes (lint + typecheck + tests).
- [x] 7.2 Backend: `make check` passes.
- [x] 7.3 `openspec validate reconcile-analytics-catalogue --strict` is green.
