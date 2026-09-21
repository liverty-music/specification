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
