## Context

Liverty Music is approaching production launch with the technical platform fully provisioned (GKE, ArgoCD, Cloudflare, Zitadel, Cloud SQL) but with no instrumentation for measuring user behaviour. The platform already operates an OpenTelemetry pipeline (`backend-otel-instrumentation`, `frontend-observability`) and a NATS event bus (used by `push-notification-service` and others) for cross-service domain events, but these are scoped to system observability and inter-service coordination respectively. Neither answers product questions such as "what fraction of users who follow an artist enter that artist's next ticket lottery?"

The frontend is an Aurelia 2 PWA with strict Core Web Vitals budgets, an existing OIDC integration with Zitadel, a Workbox-based offline strategy, and an OpenTelemetry web SDK already initialized at startup. The backend is a Go Connect-RPC service with a Clean Architecture layout and a layered domain model in which `UserId` (a UUID owned by the platform) is the canonical primary key for every user-owned entity; the Zitadel `sub` claim is stored only on the `User` record as `UserExternalId` for IdP linkage. Infrastructure runs on GCP under Pulumi-managed Kubernetes manifests delivered via ArgoCD.

Two regulatory considerations shape this design. First, Japan's Act on the Protection of Personal Information (APPI), specifically Article 28 on cross-border data transfer, requires explicit user consent when personal data is provided to a third party outside Japan. PostHog Cloud EU stores data in the Netherlands; this is a cross-border transfer regardless of which EU sub-region is chosen. Second, the 2026 APPI amendments permit processing for statistical purposes without fresh consent when data is rendered non-identifying through documented technical and organisational measures, which informs the PII-redaction approach.

A prior exploration considered five stacks (lightweight privacy-first, all-in-one PostHog, raw-event ownership via Snowplow, SaaS-first with Mixpanel, and a hybrid with GA4) before converging on the PostHog-only design captured here.

## Goals / Non-Goals

**Goals:**

- Provide product, growth, and engineering with a single source of truth for user-behaviour data covering the live-music funnel (discover → follow → lottery → purchase → entry).
- Maintain a privacy posture that satisfies APPI cross-border transfer requirements without degrading the signup conversion funnel.
- Preserve the analytics history across future identity-provider changes by decoupling analytics identity from Zitadel-issued identifiers.
- Keep the Core Web Vitals impact of the analytics SDK negligible (target: zero impact on LCP, ≤10 ms INP impact).
- Establish naming and instrumentation conventions strong enough that a second engineer can add a correctly-shaped event without consulting the author.
- Make feature-flag rollout and A/B experimentation possible without introducing flag debt or bucket-flip user experience defects.
- Keep operational ownership of analytics infrastructure low — no self-hosted ClickHouse, Kafka, or Postgres for analytics purposes.

**Non-Goals:**

- A customer data platform (CDP) such as Segment or RudderStack. Out of scope; revisited only if multiple destinations are needed.
- A raw-event data lake in BigQuery for general use. ML and recommendation workloads, when they arrive, will use a dedicated backend → Pub/Sub → BigQuery pipeline, not the analytics SDK.
- Search Console / Google Ads integration. No paid acquisition is planned for the launch window.
- Marketing email analytics, transactional email open tracking, or push-notification click attribution beyond what the existing `push-notification-service` and `analytics-consumer` already capture.
- Anonymous-user behavioural cohorts: the launch focuses on identified-user analytics; anonymous telemetry is restricted to non-PII page views needed for acquisition attribution.
- Replacement of OpenTelemetry. System observability remains entirely with OTel; PostHog does not receive request traces, error metrics, or log lines.
- Self-hosted PostHog. PostHog's Kubernetes deployment path has been officially unsupported since May 2023 and the operational ROI of running ClickHouse + Kafka + Postgres ourselves is not justified at current scale.

## Decisions

### Decision 1: PostHog Cloud EU as the single analytics platform

We will use PostHog Cloud (EU region, Frankfurt) as the sole product-analytics platform. PostHog bundles event analytics, funnels, cohorts, retention, session replay, feature flags, and A/B testing in one product with a single SDK on the client.

**Alternatives considered:**

- *Mixpanel Cloud*: more polished funnel UI but data residency is US-only or EU-only with no self-host path; pricing scales by Monthly Tracked Users which is unfavourable for a music-fan service with seasonal usage.
- *Amplitude*: strong enterprise feature set but the MTU-based pricing breaks above the 10K free tier and the product surface area is heavier than needed.
- *PostHog self-hosted on GKE*: rejected. Kubernetes is officially unsupported since May 2023; the recommended self-host path is Docker Compose ("hobby" tier), which is not production-suitable. Running ClickHouse + Kafka + Postgres for analytics adds an SRE workload disproportionate to the value delivered.
- *Plausible / Umami self-hosted*: rejected for the primary tool. They lack funnel, cohort, replay, and feature-flag capabilities required for the live-music conversion analysis.

**Rationale:** PostHog Cloud EU minimises operational burden, provides every analytics capability the launch requires, and the EU residency satisfies APPI cross-border requirements with a single consent (rather than separate consents for multiple SaaS vendors). The free tier (1M events/month, 5K session replays/month) covers the launch and early-growth period.

### Decision 2: Decline GA4 / GA4 + BigQuery for the initial scope

GA4 is not adopted. With no paid acquisition or SEO-driven growth planned for the launch window, GA4's unique value reduces to its free BigQuery export, which is a poor fit for the actual use case (ML and recommendation training data should not depend on consent or ad-blocker tolerance).

**Alternatives considered:**

- *GA4 alone*: the high-cardinality "(other)" collapse at 500 unique daily values per dimension would hide the long tail of artist/concert IDs that is central to a music service. The 500-event-name limit and 14-month data retention also constrain the multi-month live-event funnel.
- *GA4 + PostHog hybrid*: rejected for the launch. Doubles the consent surface (two third parties), risks event-schema drift across tools, and adds ~50 KB of script weight for marginal incremental value.
- *GA4-autocollect-only as a marketing safety net*: rejected. Unused instrumentation creates technical debt and undermines the simplicity of the single-tool model.

**Rationale:** Simplicity, smaller consent burden, and absence of meaningful incremental capability for the planned launch. GA4 remains a 30-minute integration if the business introduces paid advertising or SEO-driven acquisition.

### Decision 3: `distinct_id` is the Liverty `UserId`, not the Zitadel `sub`

PostHog `distinct_id` and equivalent identifiers MUST be the platform-internal `UserId` (UUID). The Zitadel `sub` claim is stored only on the `User` record as `UserExternalId` for IdP linkage and is not used as an analytics identifier.

**Alternatives considered:**

- *Zitadel `sub`*: trivially available from the OIDC ID token without a backend call. Rejected because it ties analytics history to the current identity provider; any future IdP migration breaks every historical cohort and funnel. It also forecloses future account-merging where multiple identity providers could resolve to one `UserId`.
- *Salted SHA-256 of `sub`*: rejected. `sub` is already an opaque UUID; hashing adds complexity without meaningful security benefit and prevents direct joins with `users` table in BigQuery.
- *Separate analytics-only ID issued by the backend*: rejected as premature; introduces an additional mapping layer with no offsetting privacy benefit beyond what `UserId` already provides.

**Rationale:** `UserId` is the canonical foreign key in `Ticket`, `Follow`, `PushSubscription`, `TicketJourney`, and `TicketEmail`. Using it as the analytics identifier means BigQuery joins between PostHog exports and backend tables are 1:1 with no translation layer, and the analytics history survives any future identity-provider change.

The trade-off — that the frontend must complete one `UserService.GetMe()` round-trip before `posthog.identify()` can run — is acceptable because PostHog automatically merges anonymous events captured before `identify()` into the identified profile.

### Decision 4: Event naming uses `domain.action[.outcome]` in dot.case

Events are named as dot-separated hierarchies of domain, action, and (where applicable) outcome. Examples: `artist.follow.requested`, `ticket.purchase.completed`, `entry.zk_proof.verified`. Properties use `snake_case` for keys.

**Alternatives considered:**

- *`snake_case` action names (`artist_follow_completed`)*: GA4-native style. Rejected because the dot hierarchy makes domain grouping visible in alphabetical sorts in the PostHog UI and matches the existing proto package convention (`liverty_music.entity.v1`).
- *Verb-first natural language ("Followed Artist")*: Mixpanel's official recommendation. Rejected because it is hard to grep, hard to localise, and resists state-suffix conventions like `.completed` / `.failed` / `.abandoned`.

**Rationale:** Domain prefix groups events for navigation, the outcome suffix makes state transitions first-class, and the convention mirrors the existing proto layout. The cost is a one-line documented convention rather than self-evident natural language.

### Decision 5: Frontend / backend event-sourcing split

Event emission is partitioned by trust requirement:

- **Frontend-only**: UI exploration, user intent, perceived quality (`page_view`, `artist.search`, `ticket.lottery.entry.submitted`, `recommendation.clicked`). The backend cannot observe these without explicit reporting.
- **Backend-only (trust-critical)**: events whose accuracy must survive client tampering or absence (`ticket.purchase.completed`, `entry.zk_proof.verified`, `push.notification.delivered`, `user.created`). Emitting these from the client would create both fraud risk and ad-blocker fragility.
- **Paired events for major conversion steps**: a small set of high-value actions emit both an FE `*.requested` / `*.submitted` event and a BE `*.completed` event so that the gap between user intent and successful server-side outcome is measurable. Scope is limited to artist follow, lottery entry, and ticket purchase; expanding the pattern further introduces noise without product value.

**Alternatives considered:**

- *Frontend-only emission for everything*: simplest but undermines the integrity of revenue and entry-verification metrics. Rejected.
- *Backend-only emission for everything (server-side analytics)*: removes ad-blocker fragility but requires every UI interaction to round-trip the server, which is incompatible with the PWA's offline capability and adds RPC volume. Rejected.

**Rationale:** Aligns trust boundaries with the natural origin of each signal: the backend is the source of truth for things it controls; the frontend is the source of truth for things only the user's session knows.

### Decision 6: Backend events flow through the existing NATS event bus to an `analytics-consumer`

Backend-originated analytics events are published as domain events on existing NATS subjects. A new `analytics-consumer` worker under `backend/internal/adapter/event/` subscribes to seven multi-level subject wildcards (`>`, which matches one or more tokens) that cover every backend-emitted event in the catalogue — `account.>`, `user.>`, `artist.>`, `concert.>`, `ticket.>`, `entry.>`, and `push.>` — and forwards each matching message to PostHog via the `posthog-go` SDK after sanitising properties per the PII policy.

**Alternatives considered:**

- *Synchronous `posthog-go` call inside Connect-RPC handlers*: simplest but couples handler latency to PostHog availability and mixes analytics concerns into business handlers. Rejected.
- *Dedicated GCP Pub/Sub topic for analytics*: introduces a second event bus alongside NATS for minimal benefit; rejected to avoid bus proliferation.
- *Database outbox + worker*: provides exactly-once delivery but is over-engineered for at-least-once analytics use cases. Rejected.

**Rationale:** Reuses the existing NATS infrastructure, isolates analytics failures from RPC latency, allows multiple consumers (push notifications, analytics, future ML pipelines) to consume the same domain events, and enforces a clean separation between business logic and observability concerns.

### Decision 7: APPI consent collected at signup with explicit cross-border disclosure

A consent screen at the final step of signup obtains explicit agreement for cross-border data transfer to PostHog (Netherlands). Pre-consent telemetry runs in memory-only persistence with IP collection disabled and is restricted to a closed allowlist (`page.viewed`, `account.signup.started`) that carries no identifier. The signup screen offers two toggles — analytics and marketing measurement — **both defaulting to OFF (explicit opt-in)** with a link to the privacy policy enumerating each named third party.

**Alternatives considered:**

- *Strict cookie-banner-first*: full block of all telemetry until consent. Rejected because anonymous acquisition attribution is lost and the modal friction hurts the signup conversion measurably in B2C contexts.
- *Implicit consent via privacy policy acceptance*: rejected as legally insufficient under APPI Article 28 for cross-border transfer.
- *Analytics toggle default ON ("opt-out" pattern)*: initially proposed for UX/conversion reasons. **Rejected on review** as internally contradictory: a pre-ticked toggle is the same passive opt-out pattern this same Decision rejects above for being legally insufficient under APPI Article 28. The cross-border transfer rule requires affirmative consent, and a Requirement titled "explicit consent" cannot mandate a default-on toggle in the same Scenario.
- *Drop the APPI Article 28 framing and keep default-on*: rejected. The framing is load-bearing for the legal posture against a Japan-based user base; weakening it would require legal review and a privacy-policy rewrite.

**Rationale:** Anonymous, IP-stripped, memory-persisted, allowlisted events are low-risk under APPI and preserve top-of-funnel measurement. Identified analytics — where the risk lives — is gated behind affirmative, purpose-specific consent. The trade-off is a measurable hit to opted-in conversion rate; this is accepted as the cost of legal posture certainty. Conversion-rate impact is monitored post-launch and informs whether copy or UX refinements (not default changes) can recover the gap.

### Decision 8: PostHog SDK defers initialisation until after first paint and disables autocapture

The PostHog JS SDK initialises after the application's first paint via `requestIdleCallback` (with a 2 s timeout fallback to `setTimeout`). Autocapture is disabled (`autocapture: false`), automatic page-view capture is disabled (`capture_pageview: false`), and all events including page views are emitted manually through a typed `AnalyticsService`. Session replay remains enabled with strict masking (`maskAllInputs: true`, `maskTextSelector: '[data-pii]'`, `blockSelector: '.ph-no-capture'`). Events emitted before initialisation completes are held in an in-memory queue and flushed once the SDK loads.

**Alternatives considered:**

- *Initialise at app startup*: simplest but loads ~80 KB on the critical path and risks emitting identified events before consent state is loaded. Rejected.
- *Enable autocapture with selector allowlist*: rejected because it requires every interactive element to be tagged, the captured event names (`$autocapture`) do not conform to the dot.case taxonomy, and the captured DOM context is a privacy-leakage vector.

**Rationale:** Manual instrumentation enforces the event catalogue, eliminates an entire category of accidental PII capture, and keeps the critical path lean. The cost is that every tracked interaction must be explicitly instrumented — but that is also the discipline the rest of this design depends on.

### Decision 9: Feature-flag operations require an申告 record and a 90-day kill date; significant experiments evaluate post-identify

Every PostHog feature flag MUST have a description block listing: `OWNER`, `HYPOTHESIS`, `KPI`, `KILL_DATE` (creation + 90 days), and `ISSUE` (GitHub link). A monthly review removes or escalates stale flags. Significant A/B experiments (those measuring conversion or revenue) are evaluated only after `posthog.identify()` completes; flags evaluated against anonymous users are restricted to release toggles and emergency kill switches where bucket-flip is harmless.

Frontend flag evaluation uses bootstrap with the last-known value from `localStorage` and a runtime default in case PostHog is unreachable. Backend flag evaluation uses PostHog's local-evaluation mode (periodic flag-definition sync) so that handlers do not block on PostHog availability.

**Alternatives considered:**

- *Flag every new feature*: maximum safety but creates persistent flag debt and code complexity. Rejected as a default; reserved for the narrowest of cases.
- *No flags, use deploys and Kustomize overlays*: simplest but forfeits A/B experimentation and gradual rollout. Rejected.

**Rationale:** The申告 record makes flag creation a deliberate act rather than a reflex, the kill date forces a decision, and the post-identify evaluation rule reduces the risk of unexpected bucket reassignment mid-session by deferring experiment exposure to after `identify`, so analytics records only post-identification variant assignments. The corresponding spec scenario in `specs/feature-flag-management/spec.md` still mandates a deterministic control-to-assigned-variant flip at identify for users in a treatment arm; that is acknowledged as a single bounded transition rather than a continuous source of variant churn.

### Decision 10: Strict separation between PostHog and OpenTelemetry; only `trace_id` bridges

PostHog and OpenTelemetry MUST NOT share concerns. PostHog receives product/user events in domain vocabulary; OpenTelemetry receives traces, metrics, and logs in system vocabulary. The only permitted bridge is including the active OTel `trace_id` as a property on key conversion events so that an analytics event can be correlated to its originating request trace during incident investigation.

**Alternatives considered:**

- *Send PostHog events as OTel events*: rejected because OTel's data model is request-scoped and not designed for product analytics retention; also forces PdM users into Honeycomb/Tempo UIs that do not surface funnels and cohorts.
- *Send OTel spans to PostHog*: rejected because the event volume would dwarf the product-analytics budget and pollute the funnel UI.

**Rationale:** Each tool excels at its native data model; mixing them imposes cost on both communities. The `trace_id` bridge gives operators a one-click path from a suspect event to the underlying trace at near-zero implementation cost.

## Risks / Trade-offs

- **[Risk] Cross-border consent friction at signup measurably reduces opt-in rate → Mitigation**: per Decision 7 both toggles default OFF (explicit opt-in) for APPI Article 28 compliance; the consent screen is limited to two toggles with brief plain-language descriptions and a "Set up later" path that defers to settings without blocking signup. Measure post-launch what fraction grant consent and tune copy / placement (NOT default state) if the analytics opt-in rate trends below 50%.

- **[Risk] PostHog Cloud event-volume cost grows faster than expected → Mitigation**: dashboards in the first 90 days monitor event volume by domain prefix; if approaching 1M events/month, the `analytics-consumer` is the first throttle point (drop low-value events) before paying the paid-tier rate.

- **[Risk] PostHog availability incident blocks app rendering when flags are over-relied-upon → Mitigation**: Decision 9 mandates default fallback values on both frontend and backend so that a PostHog outage degrades gracefully. CI checks for any flag evaluation lacking a default.

- **[Risk] Event-schema drift between FE and BE for paired events → Mitigation**: `docs/analytics/event-catalog.md` is the single source of truth, FE and BE constants are PR-reviewed against it, and an end-to-end smoke test validates that one paired event flow (`artist.follow`) produces both `*.requested` and `*.completed` with matching `distinct_id` (the platform `UserId` UUID) and `artist_id`.

- **[Risk] Session replay captures PII despite masking → Mitigation**: the default-masked posture (`maskAllInputs: true`) errs on the side of over-masking. Selectors that opt back in (`data-ph-unmask`) are forbidden in PR review. A monthly random-sample audit of 10 recordings confirms no PII appears in replays.

- **[Risk] Anonymous-to-identified bucket flip on feature flags causes UI inconsistency mid-session → Mitigation**: Decision 9 confines significant experiments to post-identify evaluation; this is the structural solution rather than a runtime guard.

- **[Trade-off] Manual instrumentation requires discipline that autocapture would absorb**: the cost is that every interactive surface must be instrumented intentionally. We accept this in exchange for taxonomy hygiene and PII safety. Mitigated by the typed `AnalyticsService` and `Events` constants that surface compile-time errors for misspellings.

- **[Trade-off] Backend events arrive via NATS rather than synchronously**: introduces an at-least-once delivery characteristic where some events may be duplicated. Acceptable for analytics; PostHog deduplication by event timestamp + `distinct_id` handles practical cases.

- **[Trade-off] PostHog SDK adds ~80 KB to the bundle**: mitigated by deferred load after first paint and the in-memory queue. Real-user metrics on LCP and INP are monitored for the first month to verify no regression.

## Migration Plan

This is a greenfield introduction, not a migration. There is no existing analytics tool to replace and no historical data to preserve. Deployment proceeds in phases:

1. **Phase 1 — Infrastructure (week 1)**: PostHog Cloud EU project provisioned. API keys stored in GCP Secret Manager. Pulumi stack for cloud-provisioning updated with `posthog_project_api_key` secret references and ArgoCD `ConfigMap` overlays for backend.
2. **Phase 2 — Backend instrumentation (week 1–2)**: `posthog-go` dependency added. `AnalyticsClient` interface defined under `backend/internal/usecase/`. `analytics-consumer` worker created under `backend/internal/adapter/event/` subscribing to `account.>`, `user.>`, `artist.>`, `concert.>`, `ticket.>`, `entry.>`, and `push.>` NATS subjects — the wildcard set that covers every backend-emitted event in the catalogue. Mocks generated via mockery. Tests cover happy path and PostHog-down degraded behaviour.
3. **Phase 3 — Frontend instrumentation (week 2)**: `posthog-js` dependency added. `AnalyticsService` and `Events` catalogue introduced under `frontend/src/lib/analytics/`. App root wires `AttachedLifecycle` to invoke deferred initialisation, page-view emission tied to Aurelia router navigation-end events. Consent screen added to the final step of `frontend-onboarding-flow`.
4. **Phase 4 — Event catalogue and dashboards (week 2)**: `docs/analytics/event-catalog.md` published in the specification repo with the full event list, properties, and source. Initial PostHog dashboards created for the discover → follow → lottery → purchase → entry funnel; retention cohorts created for D7 / D30 by signup month.
5. **Phase 5 — Privacy policy and rollout (week 3)**: Privacy policy updated to enumerate PostHog as a named third party with the cross-border purpose. Feature flag `analytics-enabled` is rolled out from 10% to 100% over three days, observing INP/LCP metrics and event-volume forecast.

**Rollback strategy**: at any phase, the SDK can be feature-flagged off (frontend) or the `analytics-consumer` worker scaled to zero (backend). PostHog data retention is unaffected by a rollback, and there is no schema migration to reverse.

## Open Questions

- *Should `analytics-consumer` participate in distributed tracing?* Yes in principle (`trace_id` propagation from NATS metadata), but the consumer is otherwise simple and the trace fan-out budget is unclear. Decide during Phase 2.
- *Where does the privacy-policy text actually live and who owns updates?* The privacy policy is currently a frontend route under `frontend-onboarding-flow`; this change adds PostHog as a third party but does not propose a generalised policy-management process. Resolved by the time this change is implemented.
- *Should the `ConsentService` persist consent state to the backend (`User.preferences`) or remain frontend-local in `localStorage`?* Frontend-local is simpler and consistent with the per-device nature of cookies, but persisting to backend enables cross-device consistency. Recommend frontend-local for the launch and revisit if cross-device complaints emerge.
- *How are PostHog API keys rotated?* Standard GCP Secret Manager rotation procedures, but a runbook entry is needed. Created as part of Phase 1.
