# product-analytics — delta for reconcile-analytics-catalogue

## MODIFIED Requirements

### Requirement: Event catalogue is the single source of truth
The system SHALL maintain `docs/analytics/event-catalog.md` in the specification repository as the canonical inventory of every emitted event. Frontend and backend event constants SHALL be reviewed against the catalogue during pull-request review. The catalogue SHALL list `concert.feed.card.tapped` (the frontend feed click-through event), and SHALL NOT list a recommendation impression event (`concert.recommendation.served`), a recommendation click event (`concert.recommendation.clicked`), or `concert.search.completed`, because no recommendation engine exists and search-pipeline health is recorded in OpenTelemetry rather than PostHog.

#### Scenario: Pull request adds an event without catalogue update
- **WHEN** a pull request introduces a new event constant in `frontend/src/services/analytics-events.ts` or `backend/internal/usecase/analytics_events.go`
- **THEN** the pull request SHALL also update `docs/analytics/event-catalog.md` with the event's domain, action, outcome (if any), source (FE/BE), required properties, and at least one consuming dashboard or KPI
- **AND** the pull request SHALL NOT be approved without that update

#### Scenario: Catalogue lists the feed click-through event under honest vocabulary
- **WHEN** the catalogue is reviewed for the concert feed click-through signal
- **THEN** it SHALL contain a `concert.feed.card.tapped` row sourced FE with properties `concert_id`, `artist_id`, `position`, and `trace_id?`
- **AND** it SHALL NOT contain a `concert.recommendation.served` row or a `concert.recommendation.clicked` row
- **AND** it SHALL NOT contain a `concert.search.completed` row
- **AND** the frontend constant `Events.ConcertFeedCardTapped` SHALL map to the catalogue's `concert.feed.card.tapped` name

---

### Requirement: Product analytics and OpenTelemetry remain separated; only `trace_id` bridges
PostHog SHALL receive product-domain events only. OpenTelemetry SHALL receive request traces, metrics, and logs only. No system-observability data SHALL be emitted to PostHog; no product-analytics event SHALL be emitted as an OTel span, log, or metric. User-less pipeline-health signals — such as the success, failure, or empty-result outcome of the concert-discovery search pipeline — SHALL be recorded as OpenTelemetry metrics and SHALL NOT be catalogued as PostHog events. The single permitted bridge SHALL be including the active OTel `trace_id` as a property on conversion-critical analytics events.

#### Scenario: HTTP request latency is recorded in OTel, not PostHog
- **WHEN** the frontend makes a Connect-RPC call
- **THEN** the fetch instrumentation SHALL record an OTel span describing the request
- **AND** PostHog SHALL NOT receive an event describing the request unless the request also represents a product action (e.g. `ticket.purchase.initiated`)

#### Scenario: Conversion event carries `trace_id`
- **WHEN** the backend `analytics-consumer` forwards a `ticket.purchase.completed` event
- **THEN** if a current OTel span context is available, the consumer SHALL include `trace_id` in the event properties
- **AND** the value SHALL match the same trace ID recorded in the corresponding Cloud Trace span

#### Scenario: Search-pipeline health is an OTel metric, not a catalogue event
- **WHEN** the concert-discovery search pipeline completes a run (successfully, with no results, or with an error)
- **THEN** the backend SHALL record the outcome on the `concert.search.count` OpenTelemetry counter using the `success`, `zero_results`, or `error` label
- **AND** the system SHALL NOT emit a PostHog event such as `concert.search.completed` for that run
- **AND** the event catalogue SHALL NOT list any search-pipeline-health event
