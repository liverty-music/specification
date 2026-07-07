## MODIFIED Requirements

### Requirement: Event sourcing is partitioned between frontend and backend
The system SHALL emit each event from the side that is the source of truth for that signal: UI exploration and user intent from the frontend, trust-critical state changes (financial transactions, identity verification, push delivery confirmation) from the backend. A small set of paired events SHALL be emitted from both sides to measure the gap between user intent and server-confirmed outcome.

#### Scenario: Trust-critical event is emitted from backend only
- **WHEN** a push notification reaches the delivered state and `notification.delivered` needs to be recorded
- **THEN** the backend SHALL emit the event via `analytics-consumer`
- **AND** the frontend SHALL NOT emit a duplicate `notification.delivered` event
- **AND** the frontend MAY emit a `notification.requested` intent event when the user opts in

#### Scenario: UI exploration event is emitted from frontend only
- **WHEN** the user opens a concert's detail sheet
- **THEN** the frontend SHALL emit `concert.detail.viewed` with `event_id`, `artist_id`, and `source` properties
- **AND** the backend SHALL NOT emit a duplicate event for the same detail view

#### Scenario: Paired event captures intent-to-completion gap
- **WHEN** the user taps the enable-notifications control
- **THEN** the frontend SHALL emit `notification.requested` immediately on tap, before the asynchronous permission flow
- **AND** the backend SHALL emit `notification.subscribed` after the Web Push subscription is persisted
- **AND** both events SHALL be attributable to the same `distinct_id` (the platform `UserId` UUID) so the opt-in drop-off from OS/browser permission denial is measurable

### Requirement: Frontend disables autocapture and automatic page-view capture
The frontend SHALL initialise PostHog with `autocapture: false`, `capture_pageview: false`, and `capture_pageleave: false`. Every catalogue event SHALL be emitted manually through the typed `AnalyticsService`. The application SHALL NOT emit a per-navigation page-view event: route navigation is not a catalogued analytics signal, because the analytically meaningful surfaces are already instrumented by explicit events (`concert.detail.viewed`, `artist.search`, notification events) and a per-navigation firehose is the largest event-volume source with the lowest per-event insight.

#### Scenario: Click on an arbitrary element does not produce an autocapture event
- **WHEN** the user clicks any element that is not explicitly instrumented
- **THEN** no `$autocapture` event SHALL appear in PostHog
- **AND** the only events recorded SHALL be those emitted via `AnalyticsService.capture`

#### Scenario: Router navigation does not emit a page-view event
- **WHEN** the Aurelia router completes a navigation and fires `au:router:navigation-end`
- **THEN** the application SHALL NOT emit any `page.viewed` event
- **AND** active-user and session metrics SHALL be derived from the explicit catalogue events that PostHog already receives, not from per-navigation page views

## ADDED Requirements

### Requirement: Every active catalogue event has a verified emission call site
An event catalogued with collection status `active` SHALL have at least one verified emission call site in the frontend or backend codebase. The catalogue SHALL NOT list an `active` event whose only presence is a name constant or type declaration with no code path that emits it. An event with no emission call site SHALL be removed from the live catalogue and recorded in the Removed events section; it SHALL NOT be catalogued as `dormant`, because `dormant` is reserved for events that have a real emitter and are inactive only because a feature is deferred or externally blocked.

#### Scenario: A name constant with no emitter is not an active event
- **WHEN** an event name is declared in `frontend/src/services/analytics-events.ts` or `backend/internal/usecase/analytics_events.go` but no `capture(...)` or `PublishEvent(...)` call site emits it
- **THEN** the event SHALL NOT be catalogued with status `active`
- **AND** the event SHALL be removed from the live catalogue and recorded under Removed events, NOT catalogued as `dormant`, because `dormant` requires a real emitter

#### Scenario: Pull-request review checks the call site, not only the catalogue row
- **WHEN** a pull request adds or changes a catalogued `active` event
- **THEN** review SHALL confirm a concrete emission call site exists for that event
- **AND** an event whose emitter was removed SHALL be dropped from the catalogue in the same change

### Requirement: The event catalogue records a per-event collection status
The event catalogue SHALL record, for every listed event, a collection status of `active` (currently emitted and consumed) or `dormant` (has a real emitter but is not currently emitting, pending a deferred feature or an external fix). A removed event SHALL NOT remain in the live catalogue table; it SHALL instead be recorded in a dedicated Removed events section together with the reason for removal, so the deletion is documented without reopening the phantom pattern. Dashboards and funnels SHALL be built only on `active` events. The primary conversion funnel SHALL terminate at the last observable step given the current active set — `concert.detail.viewed` — rather than at a `dormant` ticketing or entry event.

#### Scenario: Dashboard is built only on active events
- **WHEN** a dashboard or funnel is defined in PostHog
- **THEN** every step SHALL reference an event catalogued as `active`
- **AND** a step SHALL NOT reference a `dormant` event such as `entry.zk_proof.verified` or `ticket.email.parsed`

#### Scenario: Deferred ticketing events are dormant, not deleted
- **WHEN** the catalogue lists an implemented-but-inactive event such as `entry.zk_proof.verified`, `ticket.mint.completed`, or `ticket.email.parsed`
- **THEN** the event SHALL be catalogued with status `dormant` and an activation note
- **AND** the event SHALL NOT be counted toward active event volume or listed on any live dashboard

#### Scenario: A removed event is recorded, not silently dropped
- **WHEN** an event is removed from active collection (phantom, redundant, double-counting, firehose, or wrong-altitude)
- **THEN** its row SHALL be removed from the live catalogue table
- **AND** the event SHALL be listed in the Removed events section with the reason for its removal
