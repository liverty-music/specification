## ADDED Requirements

### Requirement: PostHog Cloud EU is the sole product-analytics platform
The system SHALL use PostHog Cloud (EU region) as the single platform for product analytics, including event tracking, funnels, cohorts, retention, session replay, and feature flags. The system SHALL NOT introduce alternative analytics SDKs (Google Analytics 4, Mixpanel, Amplitude, etc.) without a separate proposal.

#### Scenario: Backend forwards a domain event to PostHog Cloud EU
- **WHEN** the `analytics-consumer` worker processes a NATS message it is configured to forward
- **THEN** the worker SHALL call `posthog-go` with `Endpoint = "https://eu.i.posthog.com"`
- **AND** the worker SHALL use a project API key sourced from GCP Secret Manager
- **AND** no other analytics destination SHALL receive the event

#### Scenario: Frontend bundle does not include a second analytics SDK
- **WHEN** the production Vite build is produced
- **THEN** `posthog-js` SHALL be the only third-party analytics SDK in the bundle
- **AND** no Google Analytics, Mixpanel, Amplitude, Segment, or RudderStack SDK SHALL be present

---

### Requirement: Analytics `distinct_id` is the platform-internal `UserId`
The system SHALL use the Liverty Music `UserId` (UUID) as the `distinct_id` for every PostHog event tied to an identified user. The system SHALL NOT use the Zitadel `sub` claim or any other identity-provider-issued identifier as the analytics `distinct_id`.

#### Scenario: Frontend identifies an authenticated user
- **WHEN** the Aurelia 2 PWA completes the OIDC callback and the `UserService.GetMe` call returns
- **THEN** the frontend SHALL invoke `posthog.identify(user.id.value, properties)` where `user.id.value` is the platform `UserId` UUID
- **AND** the frontend SHALL NOT pass the Zitadel `sub` value as the `distinct_id`
- **AND** the frontend SHALL pass non-PII properties only (`locale`, `home_region`, `signup_month`)

#### Scenario: Backend forwards an event with `distinct_id`
- **WHEN** the `analytics-consumer` forwards a domain event such as `ticket.purchase.completed`
- **THEN** the request to PostHog SHALL set `distinct_id` to the `UserId` UUID associated with the event
- **AND** if the domain event does not carry a `UserId`, the consumer SHALL NOT forward the event

---

### Requirement: Event names follow `domain.action[.qualifier][.outcome]` in dot.case
Every PostHog event name SHALL be a dot-separated lowercase identifier of two to four segments in the form `<domain>.<action>`, `<domain>.<action>.<outcome>`, or `<domain>.<action>.<qualifier>.<outcome>`, where `<domain>` matches a domain prefix listed in the event catalogue. The four-segment form supports paired-funnel events such as `ticket.lottery.entry.submitted` and `ticket.lottery.result.assigned`. Property keys SHALL use `snake_case`.

#### Scenario: A new event is added to the catalogue
- **WHEN** an engineer adds a new event constant to `frontend/src/services/analytics-events.ts` or `backend/internal/usecase/analytics_events.go`
- **THEN** the event name SHALL match the regex `^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*){1,3}$`
- **AND** the event SHALL be documented in `docs/analytics/event-catalog.md` with its domain, action, outcome (if any), source (FE/BE), required properties, and consuming dashboards

#### Scenario: Property keys use snake_case
- **WHEN** an event is emitted with custom properties
- **THEN** every property key SHALL match the regex `^[a-z][a-z0-9_]*$`
- **AND** property keys SHALL NOT use camelCase, PascalCase, or kebab-case

---

### Requirement: Event sourcing is partitioned between frontend and backend
The system SHALL emit each event from the side that is the source of truth for that signal: UI exploration and user intent from the frontend, trust-critical state changes (financial transactions, identity verification, push delivery confirmation) from the backend. A small set of paired events SHALL be emitted from both sides to measure the gap between user intent and server-confirmed outcome.

#### Scenario: Trust-critical event is emitted from backend only
- **WHEN** a `ticket.purchase.completed` event needs to be recorded
- **THEN** the backend SHALL emit the event via `analytics-consumer`
- **AND** the frontend SHALL NOT emit a `ticket.purchase.completed` event
- **AND** the frontend MAY emit a `ticket.purchase.initiated` event when the purchase flow is started

#### Scenario: UI exploration event is emitted from frontend only
- **WHEN** the user opens an artist's detail page
- **THEN** the frontend SHALL emit `artist.discovery.viewed` with `artist_id` and `source` properties
- **AND** the backend SHALL NOT emit a duplicate event for the same page view

#### Scenario: Paired event captures intent-to-completion gap
- **WHEN** the user submits a ticket lottery entry form
- **THEN** the frontend SHALL emit `ticket.lottery.entry.submitted` immediately on submit
- **AND** the backend SHALL emit `ticket.lottery.entry.accepted` on successful persistence or `ticket.lottery.entry.rejected` on failure
- **AND** both events SHALL share the same `distinct_id` (the platform `UserId` UUID) and the same `concert_id` property

---

### Requirement: Backend analytics flow uses NATS and an `analytics-consumer`
Backend-originated analytics events SHALL be delivered to PostHog asynchronously via the existing NATS event bus and a dedicated `analytics-consumer` worker. Connect-RPC handlers SHALL NOT call the PostHog SDK directly.

#### Scenario: Connect-RPC handler completes without calling PostHog
- **WHEN** a Connect-RPC handler completes its primary business logic and publishes a domain event to NATS
- **THEN** the handler SHALL return the response without awaiting any PostHog call
- **AND** the handler SHALL NOT import the `posthog-go` package

#### Scenario: `analytics-consumer` forwards a subscribed NATS message
- **WHEN** the `analytics-consumer` worker receives a NATS message on a subject it is configured to forward (e.g. `ticket.purchase.completed`)
- **THEN** the worker SHALL transform the message payload into a PostHog event with the corresponding event name, `distinct_id`, and sanitised properties
- **AND** the worker SHALL retry transient PostHog errors with exponential backoff
- **AND** the worker SHALL log permanent failures without blocking subsequent messages

#### Scenario: PostHog outage does not block business handlers
- **WHEN** PostHog Cloud is unreachable for an extended period
- **THEN** the Connect-RPC handlers SHALL continue to serve requests with no added latency
- **AND** the `analytics-consumer` SHALL accumulate failures with backoff
- **AND** the system SHALL NOT lose the source NATS messages while PostHog is unreachable, up to the configured NATS retention

---

### Requirement: PostHog SDK initialisation is deferred until after first paint
The frontend SHALL defer PostHog SDK initialisation until after the application's first paint, using `requestIdleCallback` with a 2-second fallback timeout. Events emitted before initialisation completes SHALL be held in an in-memory queue and flushed when the SDK reports ready.

#### Scenario: SDK initialises after first paint on a cold start
- **WHEN** the Aurelia 2 app starts and renders its first frame
- **THEN** PostHog SDK initialisation SHALL NOT have begun
- **AND** `requestIdleCallback` (or `setTimeout` fallback) SHALL schedule initialisation
- **AND** initialisation SHALL complete only after the first paint has occurred

#### Scenario: Early event is queued and flushed on SDK ready
- **WHEN** application code calls `AnalyticsService.capture(...)` before the SDK has finished initialising
- **THEN** the service SHALL enqueue the event in memory
- **AND** when PostHog signals ready, the service SHALL flush every queued event in submission order
- **AND** queued events SHALL retain their original timestamp on flush

---

### Requirement: Frontend disables autocapture and automatic page-view capture
The frontend SHALL initialise PostHog with `autocapture: false`, `capture_pageview: false`, and `capture_pageleave: false`. Every event including page views SHALL be emitted manually through the typed `AnalyticsService`.

#### Scenario: Click on an arbitrary element does not produce an autocapture event
- **WHEN** the user clicks any element that is not explicitly instrumented
- **THEN** no `$autocapture` event SHALL appear in PostHog
- **AND** the only events recorded SHALL be those emitted via `AnalyticsService.capture`

#### Scenario: Page view is emitted on router navigation
- **WHEN** the Aurelia router completes a navigation and fires `au:router:navigation-end`
- **THEN** the application SHALL emit a `page.viewed` event with `path` and `title` properties
- **AND** the event SHALL be the result of an explicit `AnalyticsService.capture` call, not PostHog's automatic page-view capture

---

### Requirement: Session replay masks PII by default
Session replay SHALL be enabled with `maskAllInputs: true` so that the contents of every `<input>` and `<textarea>` are masked. Elements containing PII outside form inputs SHALL be marked with `data-pii` to extend masking. Sensitive sections (payment forms, ZK proof entry screens) and any 要配慮個人情報 / minor-identifying region SHALL be marked with `.ph-no-capture` to suppress recording entirely.

Session replay SHALL be sampled rather than recorded for every session. The PostHog free tier permits ~5,000 recordings/month, which at 100% capture is exhausted at roughly 600–1,000 monthly active users — far below the ~5,000 MAU the 1M-event tier supports — so the binding free-tier constraint is replay, not event volume. The application SHALL configure a session-recording sample rate (initial target ~10%) so replay coverage scales to a comparable MAU ceiling as event capture.

#### Scenario: Only a sampled fraction of sessions is recorded
- **WHEN** the configured replay sample rate is below 100% and many sessions occur
- **THEN** PostHog SHALL record session replays for approximately the configured fraction of sessions
- **AND** the un-sampled sessions SHALL still emit catalogue events normally
- **AND** the monthly recording count SHALL be projected to stay within the PostHog tier ceiling

#### Scenario: User types into an email input
- **WHEN** the user types an email address into any `<input>` element during a recorded session
- **THEN** the recorded replay SHALL show the input as a masked placeholder
- **AND** the recorded replay SHALL NOT contain the typed email text

#### Scenario: Payment form area is excluded from recording
- **WHEN** the user navigates to the ticket payment step containing a `.ph-no-capture` wrapper
- **THEN** the session replay SHALL stop capturing DOM updates within that wrapper
- **AND** mouse-movement and keystroke data within that wrapper SHALL NOT be recorded

#### Scenario: Email displayed in the UI is masked
- **WHEN** the user's profile page renders the email address inside an element marked `data-pii`
- **THEN** the recorded replay SHALL mask the email text
- **AND** the recorded replay SHALL NOT reveal the email address

---

### Requirement: Product analytics and OpenTelemetry remain separated; only `trace_id` bridges
PostHog SHALL receive product-domain events only. OpenTelemetry SHALL receive request traces, metrics, and logs only. No system-observability data SHALL be emitted to PostHog; no product-analytics event SHALL be emitted as an OTel span, log, or metric. The single permitted bridge SHALL be including the active OTel `trace_id` as a property on conversion-critical analytics events.

#### Scenario: HTTP request latency is recorded in OTel, not PostHog
- **WHEN** the frontend makes a Connect-RPC call
- **THEN** the fetch instrumentation SHALL record an OTel span describing the request
- **AND** PostHog SHALL NOT receive an event describing the request unless the request also represents a product action (e.g. `ticket.purchase.initiated`)

#### Scenario: Conversion event carries `trace_id`
- **WHEN** the backend `analytics-consumer` forwards a `ticket.purchase.completed` event
- **THEN** if a current OTel span context is available, the consumer SHALL include `trace_id` in the event properties
- **AND** the value SHALL match the same trace ID recorded in the corresponding Cloud Trace span

---

### Requirement: Event catalogue is the single source of truth
The system SHALL maintain `docs/analytics/event-catalog.md` in the specification repository as the canonical inventory of every emitted event. Frontend and backend event constants SHALL be reviewed against the catalogue during pull-request review.

#### Scenario: Pull request adds an event without catalogue update
- **WHEN** a pull request introduces a new event constant in `frontend/src/services/analytics-events.ts` or `backend/internal/usecase/analytics_events.go`
- **THEN** the pull request SHALL also update `docs/analytics/event-catalog.md` with the event's domain, action, outcome (if any), source (FE/BE), required properties, and at least one consuming dashboard or KPI
- **AND** the pull request SHALL NOT be approved without that update

---

### Requirement: Internal and E2E traffic is excluded from product analytics
The system SHALL exclude internal traffic — the Pulumi-managed E2E test user and developer/staff sessions — from product-analytics measurement so that funnels, conversion rates, and retention cohorts reflect real users only. Exclusion MAY be implemented at the SDK level (suppress capture for known-internal identities), at the PostHog project level (internal-user filters), or both; production dashboards SHALL apply the filter regardless.

#### Scenario: E2E test user does not pollute funnels
- **WHEN** the Pulumi-managed E2E user (`e2e-test-password@dev.liverty-music.app`) drives an automated session
- **THEN** the events from that session SHALL be excluded from production funnel and retention dashboards
- **AND** the exclusion SHALL be based on a stable internal-identity marker (e.g. the E2E user's `UserId` or an internal-traffic property), not on heuristic guessing

#### Scenario: Developer session is distinguishable from real users
- **WHEN** a developer or staff member uses the production app while signed in to a known-internal account
- **THEN** the analytics layer SHALL tag or suppress that session so dashboards can filter it out
- **AND** the default production dashboards SHALL have the internal filter applied
