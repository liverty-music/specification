## 1. Infrastructure & secrets

- [ ] 1.1 Create PostHog Cloud EU project and capture the public project API key, the personal API key (for definitions sync), and the EU API host URL
- [ ] 1.2 Add PostHog project API key and personal API key as GCP Secret Manager secrets in the dev, staging, and prod environments
- [ ] 1.3 Update Pulumi stacks in cloud-provisioning to grant the backend service account read access to the new PostHog secrets
- [ ] 1.4 Add backend ConfigMap entries (`POSTHOG_API_HOST`, `POSTHOG_PROJECT_KEY_SECRET_REF`) under cloud-provisioning/k8s overlays
- [x] 1.5 Document the secret-rotation runbook for PostHog API keys

## 2. Backend dependencies & domain types

- [x] 2.1 Add `github.com/posthog/posthog-go` to backend go.mod and pin the version (v1.13.1)
- [x] 2.2 Add `backend/internal/usecase/analytics_events.go` defining the canonical event-name constants emitted by the backend (placed flat under `usecase/` to match repo convention, not under a new sub-package)
- [x] 2.3 Define the `AnalyticsClient` interface in `backend/internal/usecase/analytics_client.go` covering `Enqueue(distinctID, eventName, properties)` and `Close(ctx)` semantics
- [x] 2.4 Implement `PostHogAnalyticsClient` under `backend/internal/infrastructure/analytics/posthog/` against the `AnalyticsClient` interface using `posthog-go` (placed under `infrastructure/` to match repo convention for outbound dependencies; the design.md `adapter/analytics/` path was inconsistent with the existing `infrastructure/messaging/`, `infrastructure/webpush/` etc. pattern)
- [ ] 2.5 Wire the `AnalyticsClient` binding in the manual DI graph (`internal/di/provider.go` — note: repo uses hand-written DI, not Google Wire) with environment-driven configuration — **deferred to Batch 2b together with the `analytics-consumer` worker so the wiring has an actual consumer at the same time**

## 3. Backend `analytics-consumer` worker

- [x] 3.1 Create the `analytics-consumer` adapter at `backend/internal/adapter/event/analytics_consumer.go` (flat layout matching the existing `*_consumer.go` files in that directory, NOT a new sub-package) with one `Handle*` method per subscribed NATS subject. NATS subjects follow the pre-existing UPPERCASE two-segment convention (e.g. `USER.created`); each `Handle*` method maps its subject to the corresponding lowercase catalogue event name. Initial subscription set: `USER.created` (mapped to `user.created`). Additional subscriptions land in follow-up commits as the corresponding catalogue events become reachable through new publishers.
- [ ] 3.2 Implement per-subject message decoders that transform NATS payloads into PostHog-shaped events with sanitised properties
- [ ] 3.3 Implement exponential-backoff retry for transient PostHog errors and structured logging for permanent failures
- [ ] 3.4 Add OTel `trace_id` propagation from NATS message headers onto outbound PostHog events
- [ ] 3.5 Add `analytics-consumer` to the backend cmd entrypoint and the Kubernetes Deployment manifest with appropriate resource requests/limits
- [ ] 3.6 Add Prometheus metrics for `analytics_consumer_messages_total`, `analytics_consumer_errors_total`, and `analytics_consumer_lag_seconds`

## 4. Frontend dependencies & analytics primitives

- [ ] 4.1 Add `posthog-js` to frontend package.json and pin the version
- [x] 4.2 Create `frontend/src/services/analytics-events.ts` defining the canonical `Events` constant object with typed property shapes per event (placed flat under `services/` to match repo convention, not under a new `lib/analytics/` directory)
- [ ] 4.3 Implement `AnalyticsService` under `frontend/src/lib/analytics/analytics-service.ts` with deferred initialisation via `requestIdleCallback`, in-memory queue, and typed `capture`/`identify`/`reset`/`getFeatureFlag` methods
- [ ] 4.4 Register `AnalyticsService` in the Aurelia 2 DI container via `main.ts`
- [ ] 4.5 Wire page-view emission to the Aurelia router `au:router:navigation-end` event from the app root
- [ ] 4.6 Add Vite environment variables (`VITE_POSTHOG_KEY`, `VITE_POSTHOG_HOST`) and configure injection through the frontend-runtime-config flow

## 5. Frontend identification & instrumentation

- [ ] 5.1 Invoke `AnalyticsService.identify(user.id.value, properties)` after `UserService.GetMe()` returns on app start when the user is authenticated and consent is granted
- [ ] 5.2 Instrument the artist-discovery flow (`artist.discovery.viewed`, `artist.search`, `artist.follow.requested`)
- [ ] 5.3 Instrument the concert-detail flow (`concert.detail.viewed`, `concert.recommendation.clicked`)
- [ ] 5.4 Instrument the ticket-lottery flow (`ticket.lottery.entry.submitted`)
- [ ] 5.5 Instrument the ticket-purchase flow (`ticket.purchase.initiated`)
- [ ] 5.6 Instrument the entry/check-in flow (`entry.checkin.attempted`)
- [ ] 5.7 Instrument push subscription opt-in (`notification.requested`) and notification interaction (`notification.opened`, `notification.dismissed`)
- [ ] 5.8 Tag PII-sensitive DOM elements with `data-pii` and high-risk regions with `.ph-no-capture`

## 6. Opt-out model & consent integration

> Reworked from the original opt-in design to the EU-adequacy opt-out model. The existing `ConsentService` and settings toggles (built opt-in) are refactored, not discarded.

- [ ] 6.1 Refactor `ConsentService` under `frontend/src/lib/consent/` to opt-out semantics: rename field `marketingMeasurement → sessionReplay`, default both purposes **on** for authenticated users, bump persisted-state version and migrate `v1` payloads. (Pre-launch: no opt-in/decline records to preserve.)
- [ ] 6.2 Replace the planned signup consent screen with a one-time, non-blocking **analytics transparency notice** as the final onboarding step: names PostHog + cross-border purpose, links to privacy policy and settings opt-out, never gates progression or default-on state
- [ ] 6.3 Rework the settings "Privacy & Analytics" section to two **opt-out** toggles — **Analytics** and **Session replay** — both defaulting on; Analytics off ⇒ `opt_out_capturing()` + memory-only + `reset()`; Session-replay off ⇒ `set_config` disabling recording only
- [ ] 6.4 Default-on identify: call `posthog.identify(user.id.value, { locale, home_region, signup_month })` after `GetMe` unless Analytics is opted out; do **NOT** call `reset()` on the identify path so anonymous→identified history **merges**; reserve `reset()` for sign-out and opt-out
- [ ] 6.5 Anonymous capture posture: for **anonymous visitors (pre-identification, not opted out)**, capture the **full non-PII catalogue** using `localStorage` persistence + anonymous id (so anonymous funnels survive reload); remove the closed pre-consent allowlist; no account-mapped identifier on anonymous events. An explicit opt-out is a distinct state: `opt_out_capturing()` suppresses all capture, so opted-out users emit nothing (no anonymous telemetry) — therefore the re-enable path (`opt_in_capturing()` + `identify()`) needs no `reset()` because there is no opted-out anonymous profile to merge
- [ ] 6.6 Enforce the structural exclusion of 要配慮個人情報 and minor-identifying data (precise birth date/age) at the property layer — reject/strip in `AnalyticsService` and log; bucketize any age-derived property
- [ ] 6.7 Update privacy policy to discharge the surviving APPI obligation: notification/publication of purpose of use (利用目的の通知・公表) naming PostHog as cross-border recipient, paired with the always-available settings opt-out

## 7. Feature-flag operations

- [x] 7.1 Document the flag申告 template (`OWNER`, `HYPOTHESIS`, `KPI`, `KILL_DATE`, `ISSUE`) in `specification/docs/analytics/feature-flag-policy.md`
- [ ] 7.2 Implement frontend `AnalyticsService.getFeatureFlag(key, defaultValue)` with `localStorage` bootstrap of last-known values and asynchronous refresh
- [ ] 7.3 Implement backend flag evaluation helper under `backend/internal/usecase/featureflag/` that wraps `posthog-go` local evaluation and always requires a default value at the call site
- [ ] 7.4 Add a CI check that fails when any feature-flag evaluation in the frontend or backend codebase omits a default value
- [ ] 7.5 Schedule the monthly stale-flag review as a recurring GitHub issue with a checklist template

## 8. Session replay & PII redaction

- [ ] 8.1 Configure `posthog-js` with `maskAllInputs: true`, `maskTextSelector: '[data-pii]'`, and `blockSelector: '.ph-no-capture'`
- [ ] 8.2 Audit the existing PWA for elements rendering user-controlled text outside form inputs and tag them `data-pii`
- [ ] 8.3 Tag the payment-form region, the ZK-proof entry region, and any 要配慮 / minor-identifying region with `.ph-no-capture`
- [ ] 8.4 Add a monthly recording-audit runbook entry that samples 10 recordings and confirms no PII appears
- [ ] 8.5 Configure a session-recording **sample rate** (initial ~10%) wired to the Session-replay opt-out toggle. Rationale: free-tier 5,000 recordings/month exhausts at ~600–1,000 MAU at 100% capture vs. ~5,000 MAU for events, so replay is the binding constraint and MUST be sampled from day one

## 9. Event catalogue & dashboards

- [x] 9.1 Create `specification/docs/analytics/event-catalog.md` listing every event with its name, domain, action, outcome, source (FE/BE), required properties, and intended consumers
- [ ] 9.2 Add a CI check that fails when an event constant in `frontend/src/services/analytics-events.ts` or `backend/internal/usecase/analytics_events.go` lacks a matching catalogue entry
- [ ] 9.3 Create the discover → follow → lottery → purchase → entry funnel dashboard in PostHog
- [ ] 9.4 Create the D7 / D30 retention cohort by signup month in PostHog
- [ ] 9.5 Create per-domain event-volume monitoring dashboard for the first 90 days

## 10. Testing

- [x] 10.1 Unit-test the `AnalyticsClient` interface contract and the `PostHogAnalyticsClient` implementation including PostHog-unreachable degradation (8 test cases covering happy path, empty distinctID/eventName validation, nil properties, SDK error wrapping, Close propagation, and constructor input validation)
- [ ] 10.2 Unit-test the `analytics-consumer` per-subject decoders including property sanitisation and trace_id propagation
- [ ] 10.3 Unit-test the frontend `AnalyticsService` deferred initialisation, in-memory queue flushing, identify gating on consent, and feature-flag default fallback
- [ ] 10.4 Unit-test the `ConsentService` state persistence and revocation behaviour
- [ ] 10.5 Integration-test the paired-event flow for `artist.follow.requested` (FE) and `artist.follow.completed` (BE) producing both events with matching `user_id` and `artist_id`
- [ ] 10.6 Playwright smoke test for the opt-out model: transparency notice is non-blocking, analytics is on by default, settings Analytics-off stops identified capture, Session-replay-off stops recording only, and anonymous→identified merge connects pre-signup events

## 11. Privacy policy & legal

- [ ] 11.1 Update the privacy policy to enumerate PostHog (Klant Solutions B.V., Netherlands) as a named third party for cross-border data transfer under APPI Article 28
- [ ] 11.2 Update the privacy policy to enumerate every category of data transferred and the purpose of transfer
- [ ] 11.3 Update onboarding transparency-notice copy and the settings toggle descriptions to link the relevant privacy-policy anchors
- [ ] 11.4 Confirm with legal counsel that the opt-out model satisfies APPI: cross-border transfer cleared by EU adequacy, surviving 利用目的の通知・公表 obligation met by privacy policy + opt-out, sensitive-category exclusion enforced, and opt-out (not opt-in-consent) is acceptable for the minor user segment given the adequacy posture

## 12. Rollout & verification

- [ ] 12.1 Deploy backend `analytics-consumer` to dev environment and confirm events flow to PostHog Cloud EU dev project
- [ ] 12.2 Deploy frontend analytics initialisation to dev environment and confirm the discover → follow → lottery → purchase → entry funnel populates with seeded test data
- [ ] 12.3 Promote to staging and run end-to-end smoke covering consent grant, anonymous-to-identified merge, paired-event flows, and PostHog feature-flag bootstrap
- [ ] 12.4 Roll out the production `analytics-enabled` feature flag from 10% to 50% to 100% over three days, observing INP/LCP metrics and PostHog event volume
- [ ] 12.5 Confirm post-launch dashboards populate with real-user data and that the 90-day event-volume forecast remains within the PostHog free-tier ceiling

## 13. Backend event-coverage gap (publishers for catalogued-but-unpublished events)

> Gap analysis: 10 of 17 catalogued BE events are defined in `analytics_events.go` but have **no publisher**, so the funnel tail is empty. Closing this is the largest funnel-completeness lever; the `analytics-consumer` (§3) is inert without these upstream signals.

- [ ] 13.1 Publish `account.signup.completed` and `account.login` — neither is observable today (Zitadel OIDC bypasses the backend). Add a hook (e.g. RPC-context first-seen detection or a Zitadel event) so login/signup become backend-emitted events
- [ ] 13.2 Emit `notification.delivered` from the push sender (`push_notification_uc.go` `NotifyNewConcerts`) using the send result already in hand
- [ ] 13.3 Emit the lottery funnel from `ticket_email_uc.go` parse outcomes: `ticket.lottery.entry.accepted` / `.rejected` and `ticket.lottery.result.assigned`
- [ ] 13.4 Emit the purchase funnel: `ticket.purchase.completed` / `.failed` from the payment-confirmation parse path (and/or mint flow)
- [ ] 13.5 Emit `concert.recommendation.served` from the concert list/recommendation RPC paths so impressions pair with the FE `.clicked`
- [ ] 13.6 Wire each new publisher's NATS subject into the `analytics-consumer` `Handle*` map (§3.1) and add the catalogue/CI coverage entry

## 14. New high-value catalogue events (instrumentation)

> Domain signals that were entirely uninstrumented; added to the event catalogue in this change.

- [ ] 14.1 `ticket.journey.status.changed` from `ticket_journey_uc.go` `SetStatus` (PENDING→TRACKING→ATTENDING interest-tier progression)
- [ ] 14.2 `ticket.email.parsed` from `ticket_email_uc.go` (email-ingestion data quality: type, parse status, field count)
- [ ] 14.3 `notification.unsubscribed` from `push_notification_uc.go` `Delete` (churn vs. cache-clear)
- [ ] 14.4 `sales_reminder.delivered` from `sales_reminder_delivery_uc.go` `DeliverReminder` (sales-phase-timeline KPI)
- [ ] 14.5 `concert.search.completed` from `concert_uc.go` `SearchNewConcerts` (Gemini discovery success rate)
- [ ] 14.6 `ticket.mint.completed` from `ticket_uc.go` `MintTicket` (SBT issuance)

## 15. Internal & E2E traffic exclusion

- [ ] 15.1 Exclude the Pulumi-managed E2E user (`e2e-test-password@dev.liverty-music.app`) from PostHog capture or production dashboards via a stable internal-identity marker (its `UserId` or an `internal_traffic` property), not heuristics
- [ ] 15.2 Tag/suppress developer & staff sessions so production funnel/retention dashboards filter them out by default
- [ ] 15.3 Document the internal-traffic exclusion in the analytics runbook so new internal accounts are added to the filter
