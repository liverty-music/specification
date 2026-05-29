## Why

Production launch is imminent and the platform currently has no instrumentation for understanding user behavior. Without product analytics we cannot measure the live-music conversion funnel that is the core of the business — artist discovery → follow → ticket lottery entry → purchase → entry verification — and we will be unable to iterate on product decisions with evidence after launch. Observability via OpenTelemetry covers system health, but tells us nothing about whether users are finding the artists they care about or completing the journeys we designed.

## What Changes

- Introduce **PostHog Cloud EU** as the single product-analytics platform, covering event tracking, funnels/cohorts/retention, session replay, and feature flags.
- Decline GA4 / GA4 + BigQuery for the initial scope. With no paid-ad or SEO-driven acquisition planned, GA4's unique value is limited to BigQuery export, which is better served by a dedicated backend → Pub/Sub → BigQuery pipeline if/when ML or recommendation workloads need raw events.
- Establish a **dot.case event naming convention** (`domain.action[.outcome]`) and a versioned event catalog shared by frontend and backend.
- Define an explicit **FE / BE event sourcing split**: UI/intent events fire from the Aurelia 2 PWA; trust-critical events (ticket purchases, ZK proof verification, push delivery) fire from the Go backend via the existing NATS event bus and a new `analytics-consumer` worker.
- Use the platform-internal **Liverty `UserId` (UUID)** as the analytics `distinct_id`, not the Zitadel `sub` claim. This preserves analytics history across identity-provider migrations and aligns with the domain model where `UserId` is the canonical foreign key in all business entities.
- Add an **APPI-compliant consent screen** at signup that obtains explicit cross-border data-transfer agreement for PostHog (Netherlands). Anonymous pre-login telemetry is restricted to non-PII, IP-anonymized, memory-persisted page views.
- Define an **operational policy for PostHog feature flags**: flags require an owner, a hypothesis, a 90-day kill date, and a linked issue. Significant experiments are evaluated only after user identification to eliminate anonymous-to-identified bucket flips.
- Establish a **strict separation between OpenTelemetry (system observability) and PostHog (user behavior)**. The only permitted bridge is including the OTel `trace_id` as a property on key conversion events so individual events can be correlated to traces during incident investigation.
- Configure PostHog SDK initialization to defer until after first paint (via `requestIdleCallback`), disable autocapture in favor of manual instrumentation, and disable automatic page-view capture in favor of explicit emission tied to the Aurelia router.

## Capabilities

### New Capabilities

- `product-analytics`: end-to-end product analytics covering event taxonomy and naming, frontend/backend instrumentation roles, user identification via `UserId`, the `analytics-consumer` NATS subscriber, SDK initialization patterns in the Aurelia 2 PWA, PII redaction in session replay, and the OpenTelemetry/PostHog separation boundary.
- `analytics-consent`: APPI-compliant cross-border data-transfer consent integrated into the signup flow, with per-purpose toggles (analytics vs. marketing measurement), persistent user-controlled opt-out from the settings page, and anonymous-mode behaviour when consent is absent.
- `feature-flag-management`: operational policy and runtime evaluation patterns for PostHog feature flags, including the flag-creation申告制 (owner, hypothesis, KPI, kill date), the post-identify evaluation rule for significant experiments, and PostHog-down fallback defaults on both frontend and backend.

### Modified Capabilities

None. Existing observability (`backend-otel-instrumentation`, `frontend-observability`), identity (`identity-management`, `user-auth`), and onboarding (`frontend-onboarding-flow`) capabilities are not amended; instead, the new capabilities document the boundaries and integration points.

## Impact

- **New SaaS dependency**: PostHog Cloud EU subscription (initially free tier, paid tier expected within 6–12 months as event volume grows past 1M/month).
- **New frontend dependency**: `posthog-js` SDK (~80 KB, deferred load).
- **New backend dependency**: `github.com/posthog/posthog-go` server SDK.
- **New backend service**: `analytics-consumer` — a NATS subscriber under `backend/internal/adapter/event/` that forwards selected domain events to PostHog with sanitized properties.
- **Modified user-facing flow**: signup gains a final consent screen with two opt-in toggles (PostHog analytics, future ad-measurement). Settings page gains an analytics opt-out control.
- **New documentation**: `docs/analytics/event-catalog.md` in the specification repo, listing every event name, source (FE/BE), required properties, and consuming dashboards.
- **Privacy policy update**: PostHog (Klant Solutions B.V., Netherlands) added as a named third party for cross-border data transfer under APPI Article 28.
- **No changes to**: existing OpenTelemetry instrumentation, Connect-RPC service contracts (no new RPCs required), existing NATS event subjects (analytics-consumer subscribes to existing subjects), database schema.
- **Out of scope**: GA4 integration, BigQuery raw-event pipeline, ML/recommendation event sourcing, A/B testing tooling beyond PostHog feature flags, server-side rendering analytics. These are deferred to future changes.
