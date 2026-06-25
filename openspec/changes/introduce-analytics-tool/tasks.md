## 1. Infrastructure & secrets

- [~] 1.1 Create PostHog Cloud EU project and capture the public project API key, the personal API key (for definitions sync), and the EU API host URL — PARTIAL: dev + prod projects exist and public `phc_` project keys are captured (live in the consumer/frontend ConfigMaps); the **personal** API key (flag-definition sync) is not captured/provisioned — pending until backend feature flags are actually used (see 7.3, DI deferred).
- [~] 1.2 Add PostHog project API key and personal API key as GCP Secret Manager secrets in the dev, staging, and prod environments — PARTIAL: public project key provisioned (`posthog-public-project-key` GSM secret + plaintext ConfigMap, acceptable for a public key); the **personal** key is not in GSM and no ExternalSecret sync exists — deferred with 1.1.
- [x] 1.3 Update Pulumi stacks in cloud-provisioning to grant the backend service account read access to the new PostHog secrets — `src/gcp/components/kubernetes.ts` binds the backend-app SA to the PostHog secret via `SecretManager.SecretAccessor` (per-secret, minimal scope).
- [x] 1.4 Add backend ConfigMap entries (`POSTHOG_API_HOST`, `POSTHOG_PROJECT_KEY_SECRET_REF`) under cloud-provisioning/k8s overlays — `POSTHOG_API_HOST` + `POSTHOG_PROJECT_API_KEY` present in dev and prod `consumer/configmap.env`. (Delivered as the plaintext public `phc_` value rather than a `*_SECRET_REF`, which is correct for a public key.)
- [x] 1.5 Document the secret-rotation runbook for PostHog API keys

## 2. Backend dependencies & domain types

- [x] 2.1 Add `github.com/posthog/posthog-go` to backend go.mod and pin the version (v1.13.1)
- [x] 2.2 Add `backend/internal/usecase/analytics_events.go` defining the canonical event-name constants emitted by the backend (placed flat under `usecase/` to match repo convention, not under a new sub-package)
- [x] 2.3 Define the `AnalyticsClient` interface in `backend/internal/usecase/analytics_client.go` covering `Enqueue(distinctID, eventName, properties)` and `Close(ctx)` semantics
- [x] 2.4 Implement `PostHogAnalyticsClient` under `backend/internal/infrastructure/analytics/posthog/` against the `AnalyticsClient` interface using `posthog-go` (placed under `infrastructure/` to match repo convention for outbound dependencies; the design.md `adapter/analytics/` path was inconsistent with the existing `infrastructure/messaging/`, `infrastructure/webpush/` etc. pattern)
- [x] 2.5 Wire the `AnalyticsClient` binding in the manual DI graph (`internal/di/provider.go` — note: repo uses hand-written DI, not Google Wire) with environment-driven configuration — `internal/di/consumer.go` constructs `posthog.New(APIHost, ProjectAPIKey, logger)` when the project key is non-empty and registers `Close` with the shutdown manager.

## 3. Backend `analytics-consumer` worker

- [x] 3.1 Create the `analytics-consumer` adapter at `backend/internal/adapter/event/analytics_consumer.go` (flat layout matching the existing `*_consumer.go` files in that directory, NOT a new sub-package) with one `Handle*` method per subscribed NATS subject. NATS subjects follow the pre-existing UPPERCASE two-segment convention (e.g. `USER.created`); each `Handle*` method maps its subject to the corresponding lowercase catalogue event name. Initial subscription set: `USER.created` (mapped to `user.created`). Additional subscriptions land in follow-up commits as the corresponding catalogue events become reachable through new publishers.
- [x] 3.2 Implement per-subject message decoders that transform NATS payloads into PostHog-shaped events with sanitised properties — `analytics_consumer.go` `Handle*` methods decode each CloudEvent payload and enqueue sanitised properties.
- [x] 3.3 Implement exponential-backoff retry for transient PostHog errors and structured logging for permanent failures — permanent failures are logged and recorded as error-status metrics; transient retry is delegated to the posthog-go async worker per the non-blocking `AnalyticsClient` contract (Decision 6), so the consumer never blocks. No consumer-level blocking retry by design.
- [x] 3.4 Add OTel `trace_id` propagation from NATS message headers onto outbound PostHog events — `posthog_client.go buildSDKProperties` injects the active span's `trace_id`.
- [x] 3.5 Add `analytics-consumer` to the backend cmd entrypoint and the Kubernetes Deployment manifest with appropriate resource requests/limits — wired in `cmd/consumer` via `internal/di/consumer.go` (7 analytics handlers) and `k8s/namespaces/backend/base/consumer/deployment.yaml`; confirmed Running in prod.
- [x] 3.6 Add Prometheus metrics for `analytics_consumer_messages_total`, `analytics_consumer_errors_total`, and `analytics_consumer_lag_seconds` — `internal/infrastructure/telemetry/analytics_consumer_metrics.go` emits `messages_total` (status-labelled; error statuses are the `errors_total` equivalent) and `lag_seconds`, wired in `di/consumer.go`.

## 4. Frontend dependencies & analytics primitives

- [x] 4.1 Add `posthog-js` to frontend package.json and pin the version — pinned in `package.json`.
- [x] 4.2 Create `frontend/src/services/analytics-events.ts` defining the canonical `Events` constant object with typed property shapes per event (placed flat under `services/` to match repo convention, not under a new `lib/analytics/` directory)
- [x] 4.3 Implement `AnalyticsService` under `frontend/src/lib/analytics/analytics-service.ts` with deferred initialisation via `requestIdleCallback`, in-memory queue, and typed `capture`/`identify`/`reset`/`getFeatureFlag` methods — implemented as described.
- [x] 4.4 Register `AnalyticsService` in the Aurelia 2 DI container via `main.ts` — registered via `IAnalyticsService` in `main.ts`.
- [x] 4.5 Wire page-view emission to the Aurelia router `au:router:navigation-end` event from the app root — `app-shell.ts` emits `Events.PageViewed` on router navigation.
- [x] 4.6 Add Vite environment variables (`VITE_POSTHOG_KEY`, `VITE_POSTHOG_HOST`) and configure injection through the frontend-runtime-config flow — DONE via divergence: config is delivered through the runtime `/config.json` flow (`posthogApiHost`/`posthogProjectKey` read by `shared/config/app-config.ts`), not `VITE_*` build-time env. This matches how the frontend-runtime-config flow injects other runtime config and avoids baking keys into the build.

## 5. Frontend identification & instrumentation

- [x] 5.1 Invoke `AnalyticsService.identify(user.id.value, properties)` after `UserService.GetMe()` returns on app start when the user is authenticated and consent is granted — `user-hydration-task.ts` calls `identify` after hydration; consent gating is enforced inside `AnalyticsService`.
- [x] 5.2 Instrument the artist-discovery flow (`artist.discovery.viewed`, `artist.search`, `artist.follow.requested`) — emitted from `discovery-route.ts`.
- [x] 5.3 Instrument the concert-detail flow (`concert.detail.viewed`, `concert.recommendation.clicked`) — `event-detail-sheet.ts` + `event-card.ts`.
- [~] 5.4 Instrument the ticket-lottery flow (`ticket.lottery.entry.submitted`) — OUT OF SCOPE per Decision 12: no lottery feature is offered (no FE route, no BE handler on `main`). Re-enters scope with the feature.
- [~] 5.5 Instrument the ticket-purchase flow (`ticket.purchase.initiated`) — OUT OF SCOPE per Decision 12: no purchase feature is offered. Re-enters scope with the feature.
- [~] 5.6 Instrument the entry/check-in flow (`entry.checkin.attempted`) — PARTIAL: the `entry.checkin.attempted` event type/constant is defined in `analytics-events.ts` but no FE call site emits it. The BE side of entry (`ENTRY.zk_proof_verified/rejected`) is forwarded by the consumer; the FE intent event needs the check-in screen to emit it. Instrument when the entry/check-in UI is confirmed present.
- [~] 5.7 Instrument push subscription opt-in (`notification.requested`) and notification interaction (`notification.opened`, `notification.dismissed`) — PARTIAL: `notification.requested` IS emitted (`notification-prompt.ts`). `notification.opened`/`notification.dismissed` are NOT instrumented — they require a service-worker `notificationclick`/`close` handler. This is the main remaining in-scope FE gap.
- [~] 5.8 Tag PII-sensitive DOM elements with `data-pii` and high-risk regions with `.ph-no-capture` — DEFERRED per Decision 12: only meaningful under session replay/autocapture, both disabled in prod. Re-enters scope when replay is enabled.

## 6. Opt-out model & consent integration

> Reworked from the original opt-in design to the EU-adequacy opt-out model. The existing `ConsentService` and settings toggles (built opt-in) are refactored, not discarded.

> **§6 verified & implemented** via `/opsx:verify` → opt-out refactor (frontend PR #465, merged). The earlier opt-in/`marketingMeasurement` model was confirmed superseded and replaced with the opt-out model below. Legal review (§11.4) was waived for this change per product direction.

- [x] 6.1 Refactor `ConsentService` under `frontend/src/lib/consent/` to opt-out semantics: rename field `marketingMeasurement → sessionReplay`, default both purposes **on** for authenticated users, bump persisted-state version and migrate `v1` payloads. (Pre-launch: no opt-in/decline records to preserve.) — done in PR #465: `DEFAULT_STATE { analytics: true, sessionReplay: true }`, `consent-storage.ts` v1→v2 `migrateFromV1()`.
- [x] 6.2 Replace the planned signup consent screen with a one-time, non-blocking **analytics transparency notice** as the final onboarding step: names PostHog + cross-border purpose, links to privacy policy and settings opt-out, never gates progression or default-on state — `consent-route.*` rebuilt as a notice with no `IConsentService` dependency, so it structurally cannot gate or mutate state.
- [x] 6.3 Rework the settings "Privacy & Analytics" section to two **opt-out** toggles — **Analytics** and **Session replay** — both defaulting on; Analytics off ⇒ `opt_out_capturing()` + memory-only + `reset()`; Session-replay off ⇒ `set_config` disabling recording only — done. NB session recording itself stays hard-disabled per Decision 12; the Session-replay toggle is wired as the future enable point (`applySessionReplayToSdk`).
- [x] 6.4 Default-on identify: call `posthog.identify(user.id.value, …)` after `GetMe` unless Analytics is opted out; do **NOT** call `reset()` on the identify path so anonymous→identified history **merges**; reserve `reset()` for sign-out and opt-out — done in `analytics-service.ts` (identify has no preceding `reset()`).
- [x] 6.5 Anonymous capture posture: full non-PII catalogue with `localStorage` + anonymous id (anonymous funnels survive reload); closed pre-consent allowlist removed; opt-out (`opt_out_capturing()`) suppresses all — done; default-on init uses `persistence: 'localStorage+cookie'` when not opted out, memory-only when opted out.
- [x] 6.6 Enforce the structural exclusion of 要配慮個人情報 and minor-identifying data (precise birth date/age) at the property layer — reject/strip in `AnalyticsService` and log; bucketize any age-derived property — done via new `sensitive-property-filter.ts`, applied on capture and identify.
- [~] 6.7 Update privacy policy to discharge the surviving APPI obligation: notification/publication of purpose of use (利用目的の通知・公表) naming PostHog as cross-border recipient, paired with the always-available settings opt-out — EXTERNAL: the policy lives on liverty.me/privacy (outside this repo); the in-app notice + settings toggles already link to it. The policy-page edit is tracked under §11.

## 7. Feature-flag operations

- [x] 7.1 Document the flag申告 template (`OWNER`, `HYPOTHESIS`, `KPI`, `KILL_DATE`, `ISSUE`) in `specification/docs/analytics/feature-flag-policy.md`
- [x] 7.2 Implement frontend `AnalyticsService.getFeatureFlag(key, defaultValue)` with `localStorage` bootstrap of last-known values and asynchronous refresh — implemented on `AnalyticsService`.
- [x] 7.3 Implement the backend flag evaluation helper that wraps `posthog-go` local evaluation and always requires a default value at the call site. Implemented as the `usecase.FeatureFlagEvaluator` interface plus a `posthog` adapter; placed in `internal/usecase/` + `internal/infrastructure/analytics/posthog/` to match repo convention rather than a new `featureflag/` sub-package. `IsEnabled`/`Variant` require a default and never return an error (a PostHog outage degrades to the default). Merged via backend PR #344; DI wiring deferred until a first flag consumer exists.
- [~] 7.4 Add a CI check that fails when any feature-flag evaluation in the frontend or backend codebase omits a default value — DESCOPED per Decision 11: defaults are enforced at the **type level** instead (backend `FeatureFlagEvaluator.IsEnabled/Variant` take a required default param; frontend `getFeatureFlag(key, defaultValue)` likewise), which is strictly stronger than a CI lint. Residual gap (bypassing the helper to call the SDK directly) is a within-repo import-restriction lint, deferred until a flag is actually in use.
- [x] 7.5 Schedule the monthly stale-flag review as a recurring GitHub issue with a checklist template. Implemented as the scheduled workflow `.github/workflows/stale-flag-review.yml` (monthly `cron` + `workflow_dispatch`): it opens a `feature-flag-review`-labelled issue assigned to the OWNER, carrying the four review-checklist items from `docs/analytics/feature-flag-policy.md`.

## 8. Session replay & PII redaction

> **Section deferred per Decision 12.** The shipped `AnalyticsService` runs with `disable_session_recording: true` and `autocapture: false` — session replay is not enabled in production. This whole section re-enters scope as one unit if/when replay is deliberately enabled.

- [~] 8.1 Configure `posthog-js` with `maskAllInputs: true`, `maskTextSelector: '[data-pii]'`, and `blockSelector: '.ph-no-capture'` — DEFERRED (replay not enabled)
- [~] 8.2 Audit the existing PWA for elements rendering user-controlled text outside form inputs and tag them `data-pii` — DEFERRED (replay not enabled)
- [~] 8.3 Tag the payment-form region, the ZK-proof entry region, and any 要配慮 / minor-identifying region with `.ph-no-capture` — DEFERRED (replay not enabled)
- [~] 8.4 Add a monthly recording-audit runbook entry that samples 10 recordings and confirms no PII appears — DEFERRED (no replay to audit)
- [~] 8.5 Configure a session-recording **sample rate** (initial ~10%) wired to the Session-replay opt-out toggle — NOT NEEDED in current scope per Decision 12: sampling only bounds replay's free-tier cost, and replay is disabled. Re-enters scope with replay.

## 9. Event catalogue & dashboards

- [x] 9.1 Create `specification/docs/analytics/event-catalog.md` listing every event with its name, domain, action, outcome, source (FE/BE), required properties, and intended consumers
- [~] 9.2 Add a CI check that fails when an event constant in `frontend/src/services/analytics-events.ts` or `backend/internal/usecase/analytics_events.go` lacks a matching catalogue entry — DESCOPED per Decision 11: building a cross-repo drift guard would pay a permanent cost to police a deliberately drift-prone 3-copy structure (locus trilemma: sync vs timing vs coupling). Instead rely on PR review now (Decision 5 mitigation); adopt schema-generation (Paradigm B: one proto source → generated Go/TS constants + catalogue doc, drift impossible by construction) when the taxonomy grows multi-author or a drift bug reaches `main`.
- [ ] 9.3 Create the discover → follow → lottery → purchase → entry funnel dashboard in PostHog
- [ ] 9.4 Create the D7 / D30 retention cohort by signup month in PostHog
- [ ] 9.5 Create per-domain event-volume monitoring dashboard for the first 90 days

## 10. Testing

- [x] 10.1 Unit-test the `AnalyticsClient` interface contract and the `PostHogAnalyticsClient` implementation including PostHog-unreachable degradation (8 test cases covering happy path, empty distinctID/eventName validation, nil properties, SDK error wrapping, Close propagation, and constructor input validation)
- [ ] 10.2 Unit-test the `analytics-consumer` per-subject decoders including property sanitisation and trace_id propagation
- [ ] 10.3 Unit-test the frontend `AnalyticsService` deferred initialisation, in-memory queue flushing, default-on identify (opt-out semantics), and feature-flag default fallback
- [ ] 10.4 Unit-test the `ConsentService` opt-out/re-enable state persistence, `localStorage` version migration, and session-replay-only toggle
- [ ] 10.5 Integration-test the paired-event flow for `artist.follow.requested` (FE) and `artist.follow.completed` (BE) producing both events with matching `user_id` and `artist_id`
- [ ] 10.6 Playwright smoke test for the opt-out model: transparency notice is non-blocking, analytics is on by default, settings Analytics-off stops identified capture, Session-replay-off stops recording only, and anonymous→identified merge connects pre-signup events

## 11. Privacy policy & legal

- [ ] 11.1 Update the privacy policy to enumerate PostHog (Klant Solutions B.V., Netherlands) as a named third party for cross-border data transfer under APPI Article 28
- [ ] 11.2 Update the privacy policy to enumerate every category of data transferred and the purpose of transfer
- [~] 11.3 Update onboarding transparency-notice copy and the settings toggle descriptions to link the relevant privacy-policy anchors — PARTIAL: the in-app side shipped in frontend PR #465 (the transparency notice and the settings "Privacy & Analytics" section both link to the privacy policy + the settings opt-out). The deep anchors to specific privacy-policy sections depend on the external policy page (§11.1/11.2 on liverty.me) and remain pending with it.
- [~] 11.4 Confirm with legal counsel that the opt-out model satisfies APPI: cross-border transfer cleared by EU adequacy, surviving 利用目的の通知・公表 obligation met by privacy policy + opt-out, sensitive-category exclusion enforced, and opt-out (not opt-in-consent) is acceptable for the minor user segment given the adequacy posture — WAIVED for this change per product direction: legal review was explicitly deemed not required before shipping the opt-out refactor (§6). Risk accepted by the product owner; the minor-user determination noted in design Decision-7 / analytics-consent spec remains a documented open legal question, not a blocker for this change.

## 12. Rollout & verification

- [ ] 12.1 Deploy backend `analytics-consumer` to dev environment and confirm events flow to PostHog Cloud EU dev project
- [ ] 12.2 Deploy frontend analytics initialisation to dev environment and confirm the discover → follow → lottery → purchase → entry funnel populates with seeded test data
- [ ] 12.3 Promote to staging and run end-to-end smoke covering consent grant, anonymous-to-identified merge, paired-event flows, and PostHog feature-flag bootstrap
- [ ] 12.4 Roll out the production `analytics-enabled` feature flag from 10% to 50% to 100% over three days, observing INP/LCP metrics and PostHog event volume
- [ ] 12.5 Confirm post-launch dashboards populate with real-user data and that the 90-day event-volume forecast remains within the PostHog free-tier ceiling

## 13. Backend event-coverage gap (publishers for catalogued-but-unpublished events)

> Gap analysis: 10 of 17 catalogued BE events are defined in `analytics_events.go` but have **no publisher**, so the funnel tail is empty. Of those, **4 are actionable now** — §13.1 (`account.signup.completed`, `account.login`), §13.2 (`notification.delivered`), and §13.5 (`concert.recommendation.served`). §13.3–13.4 (5 events: the 3 lottery + 2 purchase events) are **out of scope per Decision 12** (no lottery/purchase feature offered) and re-enter scope with those features. The remaining `user.deleted` has no deletion feature yet and is deferred to the `manage-analytics-data-rights` change. Closing the actionable gap is the largest funnel-completeness lever; the `analytics-consumer` (§3) is inert without these upstream signals.

- [ ] 13.1 Publish `account.signup.completed` and `account.login` — neither is observable today (Zitadel OIDC bypasses the backend). Add a hook (e.g. RPC-context first-seen detection or a Zitadel event) so login/signup become backend-emitted events
- [ ] 13.2 Emit `notification.delivered` from the push sender (`push_notification_uc.go` `NotifyNewConcerts`) using the send result already in hand
- [~] 13.3 Emit the lottery funnel from `ticket_email_uc.go` parse outcomes: `ticket.lottery.entry.accepted` / `.rejected` and `ticket.lottery.result.assigned` — OUT OF SCOPE per Decision 12 (no lottery feature offered). Re-enters scope with the feature.
- [~] 13.4 Emit the purchase funnel: `ticket.purchase.completed` / `.failed` from the payment-confirmation parse path (and/or mint flow) — OUT OF SCOPE per Decision 12 (no purchase feature offered). Re-enters scope with the feature.
- [ ] 13.5 Emit `concert.recommendation.served` from the concert list/recommendation RPC paths so impressions pair with the FE `.clicked`
- [ ] 13.6 Wire each new publisher's NATS subject into the `analytics-consumer` `Handle*` map (§3.1) and add the catalogue/CI coverage entry

## 14. New high-value catalogue events (instrumentation)

> Domain signals that were entirely uninstrumented; added to the event catalogue in this change.

- [x] 14.1 `ticket.journey.status.changed` from `ticket_journey_uc.go` `SetStatus` (interest-tier progression) — done in backend PR #347: `SetStatus` reads the prior status and, only on change, publishes `TICKET_JOURNEY.status_changed` (non-fatal); the analytics-consumer forwards it to PostHog with `{event_id, from_status, to_status}` per user. New `TicketJourneyRepository.Get` supplies `from_status` (new journey = `UNSPECIFIED`). Establishes the publisher+forwarder template for 14.2–14.6.
- [x] 14.2 `ticket.email.parsed` from `ticket_email_uc.go` (email-ingestion data quality: type, parse status, field count) — done in backend PR #348: `Create` publishes `TICKET_EMAIL.parsed` on both parse success and failure (non-fatal), forwarded with `{email_type, parse_status, field_count}`.
- [x] 14.3 `notification.unsubscribed` from `push_notification_uc.go` `Delete` (churn vs. cache-clear) — done in backend PR #349: the user-initiated `Delete` publishes `NOTIFICATION.unsubscribed` (non-fatal, `{device_type}`); the 410-Gone send-loop expiry path is deliberately NOT instrumented (a regression test enforces it), so the signal is churn-only.
- [ ] 14.4 `sales_reminder.delivered` from `sales_reminder_delivery_uc.go` `DeliverReminder` (sales-phase-timeline KPI)
- [ ] 14.5 `concert.search.completed` from `concert_uc.go` `SearchNewConcerts` (Gemini discovery success rate)
- [x] 14.6 `ticket.mint.completed` from `ticket_uc.go` `MintTicket` (SBT issuance) — done in backend PR #348: `MintTicket` publishes `TICKET.mint_completed` after persist (fresh-mint + concurrent-reconcile paths, non-fatal), forwarded with `{event_id}`.

## 15. Internal & E2E traffic exclusion

- [ ] 15.1 Exclude the Pulumi-managed E2E user (`e2e-test-password@dev.liverty-music.app`) from PostHog capture or production dashboards via a stable internal-identity marker (its `UserId` or an `internal_traffic` property), not heuristics
- [ ] 15.2 Tag/suppress developer & staff sessions so production funnel/retention dashboards filter them out by default
- [ ] 15.3 Document the internal-traffic exclusion in the analytics runbook so new internal accounts are added to the filter
