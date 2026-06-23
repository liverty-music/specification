## Why

Production launch is imminent and the platform currently has no instrumentation for understanding user behavior. Without product analytics we cannot measure the live-music conversion funnel that is the core of the business — artist discovery → follow → ticket lottery entry → purchase → entry verification — and we will be unable to iterate on product decisions with evidence after launch. Observability via OpenTelemetry covers system health, but tells us nothing about whether users are finding the artists they care about or completing the journeys we designed.

## What Changes

- Introduce **PostHog Cloud EU** as the single product-analytics platform, covering event tracking, funnels/cohorts/retention, session replay, and feature flags.
- Decline GA4 / GA4 + BigQuery for the initial scope. With no paid-ad or SEO-driven acquisition planned, GA4's unique value is limited to BigQuery export, which is better served by a dedicated backend → Pub/Sub → BigQuery pipeline if/when ML or recommendation workloads need raw events.
- Establish a **dot.case event naming convention** (`domain.action[.outcome]`) and a versioned event catalog shared by frontend and backend.
- Define an explicit **FE / BE event sourcing split**: UI/intent events fire from the Aurelia 2 PWA; trust-critical events (ticket purchases, ZK proof verification, push delivery) fire from the Go backend via the existing NATS event bus and a new `analytics-consumer` worker.
- Use the platform-internal **Liverty `UserId` (UUID)** as the analytics `distinct_id`, not the Zitadel `sub` claim. This preserves analytics history across identity-provider migrations and aligns with the domain model where `UserId` is the canonical foreign key in all business entities.
- Adopt a **transparency-and-opt-out model** for analytics rather than an opt-in gate. Cross-border transfer to PostHog Cloud EU (Netherlands) is already permitted under APPI Article 28's EU adequacy designation (in force since January 2019), so identified analytics is **enabled by default** for authenticated users; the user can opt out at any time from the settings page. The APPI obligation that survives adequacy — **notification/publication of the purpose of use (利用目的の通知・公表)** — is discharged by naming PostHog in the privacy policy and surfacing an always-available opt-out, not by a signup consent gate. (The platform is pre-launch, so there are no previously-collected opt-in/decline decisions to migrate.)
- Capture the **full non-PII event catalogue anonymously before identification** (anonymous users and authenticated-but-opted-out users): persistence is `localStorage` with an anonymous id (so anonymous funnels survive page reloads), IP collection is configurable, and on login the anonymous profile is **merged into the identified profile** via `posthog.identify` so pre-signup discovery behaviour stays connected to post-signup conversion. The earlier closed pre-consent allowlist (`page.viewed`, `account.signup.started` only) is replaced by this anonymous-full-capture posture.
- **Structurally exclude APPI 要配慮個人情報 (sensitive personal information: race, creed, social status, medical history, criminal record, etc.) and any minor-identifying data from all capture paths**, including session replay. Sensitive categories can never be acquired under an opt-out model, so the guarantee is enforced in code (event-property allowlist + replay masking) rather than by consent.
- Define an **operational policy for PostHog feature flags**: flags require an owner, a hypothesis, a 90-day kill date, and a linked issue. Significant experiments are evaluated only after user identification to eliminate anonymous-to-identified bucket flips.
- Establish a **strict separation between OpenTelemetry (system observability) and PostHog (user behavior)**. The only permitted bridge is including the OTel `trace_id` as a property on key conversion events so individual events can be correlated to traces during incident investigation.
- Configure PostHog SDK initialization to defer until after first paint (via `requestIdleCallback`), disable autocapture in favor of manual instrumentation, and disable automatic page-view capture in favor of explicit emission tied to the Aurelia router.

## Capabilities

### New Capabilities

- `product-analytics`: end-to-end product analytics covering event taxonomy and naming, frontend/backend instrumentation roles, user identification via `UserId`, the `analytics-consumer` NATS subscriber, SDK initialization patterns in the Aurelia 2 PWA, PII redaction in session replay, and the OpenTelemetry/PostHog separation boundary.
- `analytics-consent`: APPI-aligned analytics governance under the EU-adequacy opt-out model — identified analytics enabled by default, a single user-controlled **analytics opt-out** toggle on the settings page, anonymous full-catalogue capture before/without identification with anonymous→identified merge on login, structural exclusion of 要配慮個人情報 and minor-identifying data, and the privacy-policy purpose-of-use notification that satisfies the surviving APPI obligation. (The second settings toggle is redefined — see Modified Capabilities below.)
- `feature-flag-management`: operational policy and runtime evaluation patterns for PostHog feature flags, including the flag-creation申告制 (owner, hypothesis, KPI, kill date), the post-identify evaluation rule for significant experiments, and PostHog-down fallback defaults on both frontend and backend.

### Modified Capabilities

- `frontend-onboarding-flow`: the final onboarding step is **no longer a consent gate**. Under the opt-out model there is no signup decision to collect, so the step becomes a one-time **transparency notice** that names PostHog and the cross-border purpose, links to the privacy policy, and points to the settings opt-out. It never blocks progression and never disables default analytics.

**Settings toggle redefinition.** The settings "Privacy & Analytics" section keeps **two** toggles, but their meaning changes under the opt-out model:
  - Toggle 1 — **Analytics** (`analytics`): now defaults **on** for authenticated users (opt-out). Off ⇒ `posthog.opt_out_capturing()`, drop to anonymous memory-only, sever the identified profile.
  - Toggle 2 — was **Marketing measurement** (`marketingMeasurement`). With cross-border transfer covered by EU adequacy, a separate cross-border consent toggle no longer has a distinct legal meaning. It is **repurposed to "Session replay"** — a genuinely separable, higher-sensitivity capability the user may want to disable independently of event analytics. (Field rename `marketingMeasurement → sessionReplay` is tracked in tasks; the persisted-state version bumps to migrate `v1` payloads.)

Existing observability (`backend-otel-instrumentation`, `frontend-observability`) and identity (`identity-management`, `user-auth`) capabilities are not amended; the new capabilities document the boundaries and integration points.

## Impact

- **New SaaS dependency**: PostHog Cloud EU subscription (initially free tier, paid tier expected within 6–12 months as event volume grows past 1M/month).
- **New frontend dependency**: `posthog-js` SDK (~80 KB, deferred load).
- **New backend dependency**: `github.com/posthog/posthog-go` server SDK.
- **New backend service**: `analytics-consumer` — a NATS subscriber under `backend/internal/adapter/event/` that forwards selected domain events to PostHog with sanitized properties.
- **Modified user-facing flow**: the final onboarding step becomes a one-time transparency notice (not a consent gate). The settings page carries two opt-out controls (Analytics, Session replay), both defaulting on for authenticated users.
- **Backend event-coverage gap**: a gap analysis found that 10 of the 17 backend catalogue events are defined in `analytics_events.go` but have **no publisher** wired yet (notably `account.signup.completed`, `account.login`, `notification.delivered`, and the entire `ticket.lottery.*` / `ticket.purchase.*` funnel tail). Closing this gap is the single largest lever for funnel completeness and is tracked in tasks; the `analytics-consumer` alone is insufficient without the upstream publishers.
- **New catalogue events**: high-value domain signals currently uninstrumented are added to the catalogue — `ticket.journey.status.changed`, `ticket.email.parsed`, `notification.unsubscribed`, `sales_reminder.delivered`, `concert.search.completed`, `ticket.mint.completed`.
- **Internal/E2E traffic exclusion**: the Pulumi-managed E2E user and developer/internal sessions are excluded from PostHog (or from production dashboards) so they do not skew funnels.
- **Session-replay free-tier ceiling**: at 100% capture the PostHog free tier's 5,000 recordings/month is exhausted at roughly 600–1,000 MAU — far below the ~5,000 MAU the 1M-event tier allows. Replay therefore ships with sampling (target ~10%) from day one.
- **New documentation**: `docs/analytics/event-catalog.md` in the specification repo, listing every event name, source (FE/BE), required properties, and consuming dashboards.
- **Privacy policy update**: PostHog (Klant Solutions B.V., Netherlands) added as a named third party for cross-border data transfer under APPI Article 28.
- **No changes to**: existing OpenTelemetry instrumentation, Connect-RPC service contracts (no new RPCs required), existing NATS event subjects (analytics-consumer subscribes to existing subjects), database schema.
- **Out of scope**: GA4 integration, BigQuery raw-event pipeline, ML/recommendation event sourcing, A/B testing tooling beyond PostHog feature flags, server-side rendering analytics. **APPI data-subject rights for analytics data (deletion / disclosure / stop-of-use, including PostHog `distinct_id` erasure on account deletion)** are split into a dedicated change (`manage-analytics-data-rights`) rather than handled here. These are deferred to future changes.
