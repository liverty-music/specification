# Reconcile the analytics catalogue: honest vocabulary, drop phantoms, separate pipeline health

## Why

A devil's-advocate review of two in-flight catalogue cleanups found they touch the same files (`docs/analytics/event-catalog.md`, the `product-analytics` spec, `analytics-events.ts`, `analytics_events.go`) and would collide if shipped separately. They are merged here into one reconciliation.

The review also corrected an earlier "delete it" instinct on the recommendation events by inspecting the actual code:

- `concert.recommendation.clicked` is **not** dead. The dashboard concert list *is* the recommendation feed: `frontend/src/routes/dashboard/dashboard-route.ts:369` tags the detail sheet with `source: 'recommendation'`, and `frontend/src/components/live-highway/event-card.ts:57-67` fires the event position-keyed with a null-position CTR guard. It is a real, position-keyed click-through signal — only its **name** is misleading, because there is no recommendation engine producing it. It should be **renamed**, not deleted.
- `concert.recommendation.served` (BE) is a genuine phantom: the constant `EventConcertRecommendationServed` and its `knownBackendEvents` entry exist in `backend/internal/usecase/analytics_events.go`, but no publisher ever emits it and no recommendation engine exists to produce impressions. It should be deleted.
- `concert.search.completed` is user-less search-pipeline telemetry. Per Decisions 10 and 13 of the archived `introduce-analytics-tool`, system/pipeline-health signals belong in OpenTelemetry, not PostHog. It has no PostHog publisher, and the OTel counter `concert.search.count` already records the same signal in `backend/internal/infrastructure/telemetry/business_metrics.go` (labelled `success`/`error`, recorded in `concert_uc.go` `executeSearch`). It should be removed from the catalogue, and its OTel counter strengthened with a `zero_results` outcome so the pipeline-health view is complete.

The net effect is an honest catalogue: the live feed-CTR signal carries honest vocabulary, the phantom impression event is gone, and pipeline health is owned solely by OTel.

## What Changes

- **Rename** the frontend feed click-through event `concert.recommendation.clicked` → `concert.feed.card.tapped`, preserving its `position` property and the null-position CTR guard.
- **Delete** the backend phantom event `concert.recommendation.served` (constant + allowlist entry); it has no publisher and no engine.
- **Remove** `concert.search.completed` from the catalogue; it is user-less pipeline health that already lives in OTel.
- **Add** a `zero_results` outcome label to the existing `concert.search.count` OTel counter (today only `success`/`error`), so a successful-but-empty search is distinguishable from a fruitful one.
- **Update** `docs/analytics/event-catalog.md`: drop the two recommendation rows and the search row, add the `concert.feed.card.tapped` row, and rename the "Recommendation effectiveness" funnel to a feed-CTR funnel.

## Capabilities

### Modified Capabilities

- `product-analytics`

## Impact

- **Frontend** (`frontend/src/services/analytics-events.ts`): rename the `ConcertRecommendationClicked` event constant, the `ConcertRecommendationClickedProps` type, the props-map entry, the `'recommendation'` member of the `EventSource` union (→ `'feed'`), and the doc comments. Call site `frontend/src/components/live-highway/event-card.ts:57-67` and the source tag at `frontend/src/routes/dashboard/dashboard-route.ts:369` follow the rename. Behaviour (position-keyed capture, null-position guard) is unchanged.
- **Backend** (`backend/internal/usecase/analytics_events.go`): delete the `EventConcertRecommendationServed` constant and its `knownBackendEvents` entry. No publisher referenced it, so no call site changes.
- **Backend** (`backend/internal/infrastructure/telemetry/business_metrics.go` + `internal/usecase/concert_uc.go`): add `zero_results` to the set of values `RecordConcertSearch` accepts, and record it in `executeSearch` when a successful search yields no concerts.
- **Catalogue** (`docs/analytics/event-catalog.md`): three row edits (remove two, add one) and one funnel rename.
- **No proto changes**, no BSR regeneration, no migration. PostHog will see the renamed event as a new name — a known, accepted discontinuity from the old `concert.recommendation.clicked` series.
