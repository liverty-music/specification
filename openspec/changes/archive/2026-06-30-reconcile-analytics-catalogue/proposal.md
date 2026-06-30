# Reconcile the analytics catalogue: honest vocabulary, drop phantoms, separate pipeline health

## Why

A devil's-advocate review of two in-flight catalogue cleanups found they touch the same files (`docs/analytics/event-catalog.md`, the `product-analytics` spec, `analytics-events.ts`, `analytics_events.go`) and would collide if shipped separately. They are merged here into one reconciliation.

A devil's-advocate review then inspected the actual code, and corrected an earlier "rename it" instinct on the click event into a **deletion** by following the firing path:

- `concert.recommendation.clicked` should be **deleted**, not renamed. Naming it `recommendation` is misleading (there is no recommendation engine), but renaming it to a "feed"/"card-tap" event would only swap one ungrounded surface noun for another. More importantly the event is **redundant**: a single dashboard card tap fires both this event (`frontend/src/components/live-highway/event-card.ts`) **and** `concert.detail.viewed` (`frontend/src/components/live-highway/event-detail-sheet.ts`), because the tap dispatches `event-selected` → `dashboard-route.ts` opens the detail sheet → `concert.detail.viewed` fires. The only datum unique to the tap event was `position`, and its CTR denominator (the impression event below) is itself a phantom being deleted — so no real click-through rate could ever be computed. The signal "a concert from the dashboard list was opened" already lives in `concert.detail.viewed` with its `source` property.
- `concert.recommendation.served` (BE) is a genuine phantom: the constant `EventConcertRecommendationServed` and its `knownBackendEvents` entry exist in `backend/internal/usecase/analytics_events.go`, but no publisher ever emits it and no recommendation engine exists to produce impressions. It should be deleted.
- `concert.search.completed` is user-less search-pipeline telemetry. Per Decisions 10 and 13 of the archived `introduce-analytics-tool`, system/pipeline-health signals belong in OpenTelemetry, not PostHog. It has no PostHog publisher, and the OTel counter `concert.search.count` already records the same signal in `backend/internal/infrastructure/telemetry/business_metrics.go` (labelled `success`/`error`, recorded in `concert_uc.go` `executeSearch`). It should be removed from the catalogue, and its OTel counter strengthened with a `zero_results` outcome so the pipeline-health view is complete.

The dashboard surface keeps an honest name where it genuinely matters: the `EventSource` member `'recommendation'` (still carried by `concert.detail.viewed`) is renamed to `'dashboard'`, matching the actual route (`frontend/src/routes/dashboard/`) rather than an imaginary recommendation engine.

A wider catalogue audit (requested while reviewing the above) surfaced two more inconsistencies of the same kind, folded into this reconciliation:

- **The same identifier is named two ways.** `Concert` is a user-facing DTO whose `id` *is* an `EventId` (`proto/.../entity/v1/concert.proto`: "The unique identifier of the underlying event. `EventId id = 1`"). Yet the catalogue refers to that one identifier as `concert_id` on ten events (`concert.detail.viewed`, the `ticket.*` funnel, `notification.{delivered,opened}`) and as `event_id` on five (`entry.*`, `ticket.journey.status.changed`, `ticket.mint.completed`). An analyst building the view→purchase→mint→check-in funnel cannot join on one property because the name changes mid-funnel. The canonical entity is `Event`/`EventId`, so the catalogue standardises on **`event_id`** everywhere.
- **`account.signup.completed` is a phantom and a duplicate.** The constant is defined and allow-listed in `analytics_events.go` but no publisher emits it, while `user.created` *is* emitted (`internal/adapter/event/analytics_consumer.go`) with identical properties (`signup_month`, `locale`, `home_region?`). It should be deleted; the signup-funnel terminus and retention cohort are served by `user.created`.

The net effect is an honest catalogue: the redundant click event is gone (its signal is preserved by `concert.detail.viewed`), the phantom impression and phantom signup events are gone, the dashboard surface label is grounded in the real route, and one identifier (`event_id`) names the underlying event across every event so funnels join cleanly. Pipeline health is owned solely by OTel.

## What Changes

- **Delete** the frontend click event `concert.recommendation.clicked` (constant, props type, props-map entry, call site, and its now-dead `position` plumbing); its signal is fully covered by `concert.detail.viewed`.
- **Rename** the `EventSource` union member `'recommendation'` → `'dashboard'` (still used by `concert.detail.viewed`) so the surface label matches the real dashboard route.
- **Delete** the backend phantom event `concert.recommendation.served` (constant + allowlist entry); it has no publisher and no engine.
- **Remove** `concert.search.completed` from the catalogue; it is user-less pipeline health that already lives in OTel.
- **Add** a `zero_results` outcome label to the existing `concert.search.count` OTel counter (today only `success`/`error`), so a successful-but-empty search is distinguishable from a fruitful one.
- **Standardise** the underlying-event identifier on `event_id` across the catalogue (rename the `concert_id` property to `event_id` on every event that carries it) and in the implemented frontend code (`concert.detail.viewed`).
- **Delete** the phantom, duplicate backend event `account.signup.completed` (constant + allowlist entry); `user.created` already covers it.
- **Update** `docs/analytics/event-catalog.md`: drop the two recommendation rows, the search row, and the `account.signup.completed` row; remove the now-empty "Recommendation effectiveness" funnel; rename every `concert_id` column to `event_id`; and absorb the signup-funnel/retention consumer into `user.created`.

## Capabilities

### Modified Capabilities

- `product-analytics`

## Impact

- **Frontend** (`frontend/src/services/analytics-events.ts`): delete the `ConcertRecommendationClicked` event constant, the `ConcertRecommendationClickedProps` type, and the props-map entry; rename the `'recommendation'` member of the `EventSource` union to `'dashboard'`; update the doc comments. The call site in `frontend/src/components/live-highway/event-card.ts` is removed (taking the now-unused `IAnalyticsService` injection and `position` `@bindable` with it), the dead `position.bind="$index"` bindings in `concert-highway.html` are removed, and the source tag at `frontend/src/routes/dashboard/dashboard-route.ts` becomes `'dashboard'`. `concert.detail.viewed` behaviour is unchanged.
- **Backend** (`backend/internal/usecase/analytics_events.go`): delete the `EventConcertRecommendationServed` constant and its `knownBackendEvents` entry. No publisher referenced it, so no call site changes.
- **Backend** (`backend/internal/infrastructure/telemetry/business_metrics.go` + `internal/usecase/concert_uc.go`): add `zero_results` to the set of values `RecordConcertSearch` accepts, and record it in `executeSearch` when a successful search yields no concerts.
- **Frontend** (`frontend/src/services/analytics-events.ts` + `event-detail-sheet.ts`): rename the `concert_id` property to `event_id` on `ConcertDetailViewedProps`, `TicketLotteryEntrySubmittedProps`, `TicketPurchaseInitiatedProps`, and `NotificationOpenedProps`; update the only emitting call site (`concert.detail.viewed` in `event-detail-sheet.ts`) and its test. The three ticket/notification props are type-only today (no call sites yet), so those are declaration edits. Also repoint the `account.signup.started` doc comment's pairing from `account.signup.completed` to `user.created`.
- **Backend** (`backend/internal/usecase/analytics_events.go`): delete the `EventAccountSignupCompleted` constant and its `knownBackendEvents` entry. No publisher referenced it. No backend analytics code carries a `concert_id` property today (the `concert_id` occurrences in backend are RPC arguments, NATS payload fields, and `slog` log keys — out of scope), so the `event_id` standardisation is catalogue-only on the backend.
- **Catalogue** (`docs/analytics/event-catalog.md`): four rows removed (`concert.recommendation.served`, `concert.recommendation.clicked`, `concert.search.completed`, `account.signup.completed`), the "Recommendation effectiveness" funnel removed, every `concert_id` column renamed to `event_id` (and dropped from the PII-safety example list), and the `user.created` consumer note expanded.
- **No proto changes**, no BSR regeneration, no migration. PostHog simply stops receiving `concert.recommendation.clicked`; its historical series is retained but no longer extended — an accepted discontinuity, since the same conversion is observable through `concert.detail.viewed`.
