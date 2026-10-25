## Why

The fan app goes public soon, and today the team cannot see what a first-time visitor does. Measured in PostHog project 190464 over the 30 days to 2026-10-22: 16,788 events from 35 people, 96 % of them performance telemetry; no `$pageview` at all (`capture_pageview: false`); the first referrer recorded for 1 person out of 35; no event for a guest's follows, for the sign-up steps, for a notification's type, for leaving the app towards a ticket page, or for any step of a purchase. Three catalogued events (`ticket.purchase.initiated`, `ticket.lottery.entry.submitted`, `entry.checkin.attempted`) are defined in `frontend/src/services/analytics-events.ts` and never sent. Session replay is hard-disabled although the Settings screen already offers a Session replay toggle.

On the backend, each concert and ticket-sale search calls an external search model, and those calls are about 90 % of the Gemini bill (2,055 JPY of 2,741 JPY billed on 2026-10-08..21 was the Google Search grounding fee). The call's usage and outcome are only in 30-day logs, with field names that differ between the two searches, so cost per discovered concert has to be rebuilt by hand.

This change makes the product record what the team needs, from the first visit to a paid ticket, and makes each external search report its usage and result. `fix-trace-propagation` lands first: the search reports use its trace as their key.

## What Changes

**Fan app (frontend)**

- Every screen change sends a page view, and leaving the app sends a page leave.
- The campaign values of the address the fan arrived on (`utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`) are sent as their own properties. The query-string rule for addresses stays as it is; a referral code is still never sent.
- Session replay starts recording, behind the existing Session replay toggle: every text and input is masked, and the checkout, lottery entry, identity check and settings screens are not recorded.
- Every event says whether the app runs installed or in a browser tab.
- New usage events: onboarding started (welcome), every start of sign-up or sign-in with the screen it started from, a guest's follow, the onboarding timetable ready (discovery), the number of guest follows merged at sign-up, the push permission answer, the install banner shown and the app installed, the concert's source link opened and calendar added (event detail sheet), share and calendar added (event page), each checkout step shown, purchase initiated, lottery entry started and submitted.
- A notification opened or dismissed carries the notification's type and, for a sales reminder, its milestone.
- PostHog traffic goes through a reverse proxy on a subdomain of the app's domain, and the project's day boundary moves to Japan time.

**Backend**

- A pushed notification's data carries its type, and a sales reminder's data carries its milestone.
- New product-analytics signals: a hype change, a paid order, each lottery entry's draw result, each expired checkout, each admitted ticket.
- Each concert search and ticket-sale search reports its outcome, and each call to the external search model reports its usage (tokens by kind, search queries, pages read, latency, finish reason, error kind) as an LLM generation, keyed by the trace of the search. The backend's release version is reported with it, which identifies the prompt.

**Evaluation**

- Langfuse (Cloud, Japan region, free plan) and PostHog LLM analytics are compared for the Gemini A/B harness, and the change records which one the team keeps. No production traffic goes to Langfuse.

**Out of scope, and why**

- Browser error reporting, source maps and the privacy-policy purpose 不具合の検出と修正: shipped by `capture-client-errors` (frontend #828).
- An event for a completed identity check: the identity check screens and use case are being built in the in-flight change `identity-ekyc-jpki` and have no main spec yet; the event belongs there.
- Loading this data into BigQuery and the dashboards: the follow-up change for the analytics platform.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/infrastructure/fan/web/global/analytics`: page views and leaves, campaign values, session recording masking, install state (all ADDED; the query-string requirement is untouched, because `capture-client-errors` modifies it).
- `components/infrastructure/fan/web/global/service-worker`: notification interactions carry type and milestone.
- `components/infrastructure/fan/web/global/notification-prompt`: the permission answer is reported.
- `components/infrastructure/fan/web/global/pwa-install-banner`: banner shown and app installed are reported.
- `components/infrastructure/fan/web/global/event-detail-sheet`: source link and calendar are reported.
- `components/infrastructure/fan/web/global/legal-document`: the Privacy Policy discloses session recordings (ADDED; the existing disclosure requirement is modified by `capture-client-errors`).
- `components/infrastructure/fan/web/route/welcome`: onboarding started is reported.
- `stories/sign-up-or-sign-in`: every start of sign-up or sign-in is reported with where it started (six screens and controls start it, so the rule is the story's).
- `components/infrastructure/fan/web/route/discovery`: a guest's follow and the ready timetable are reported.
- `components/infrastructure/fan/web/route/event`: share and calendar are reported.
- `components/infrastructure/fan/web/route/checkout`: steps and purchase initiated are reported.
- `components/infrastructure/fan/web/route/lottery-entry`: entry started and submitted are reported.
- `stories/merge-guest-data-on-signup`: the number of merged follows is reported.
- `components/usecase/notification/deliver`: "The pushed message carries the notification id" also carries the type.
- `components/usecase/ticket-sale-reminder/deliver-reminder`: the reminder's data carries its milestone.
- `components/usecase/follow/set-hype`, `components/usecase/order/fulfill-payment`, `components/usecase/lottery-entry/run-draw`, `components/usecase/checkout/release-expired`, `components/usecase/ticket/admit`: each reports its signal.
- `components/usecase/order/fulfill-payment`, `components/usecase/resale-listing/refund-sold`, `components/usecase/notification/notify-new-concerts`, `components/usecase/ticket-sale/announce-discovered-sale`: every announcement gets a fresh UUIDv7 id, so the broker no longer drops a repeated announcement; consumers of orders and refunds stay idempotent by their ids, and a repeated notification request can reach the fan again until a follow-up change announces each fact once.
- `components/usecase/concert/search-new-concerts`, `components/usecase/concert/create-from-discovered`, `components/usecase/ticket-sale/discover-for-artist`: each reports its outcome.
- `components/entity/concert/search`, `components/entity/ticket-sale/search-published-sales`: each external call reports its usage. Concert search also fails with Unavailable when every attempt fails transiently, instead of returning no concerts, so the search is recorded as failed and searched again on the next run.

The entities behind these use cases (Follow, Order, LotteryEntry, Checkout, Ticket, Notification, ConcertSearch, TicketSale) are unchanged: every signal reads values the entities already have.

## Impact

- **frontend**: `src/lib/analytics/analytics-service.ts`, `src/services/analytics-events.ts`, `src/lib/analytics/notification-interaction.ts`, `src/sw.ts`, the welcome, discovery, event, checkout and lottery-entry routes, `follow-store.ts`, `notification-manager.ts`, `pwa-install-service.ts`, the event detail sheet, and the privacy policy in `src/locales/{ja,en}/translation.json`. The analytics service is also edited by `capture-client-errors`; whichever merges second rebases.
- **backend**: `internal/usecase/analytics_events.go` and the analytics consumer, the use cases above, `internal/entity/push_notification.go`, `internal/infrastructure/gcp/gemini/{searcher,ticket_sale_searcher}.go`, a new LLM-generation reporter in `internal/infrastructure/analytics/posthog`, and the A/B harness.
- **cloud-provisioning**: a Cloudflare CNAME for the PostHog managed proxy, the fan web ConfigMap `posthogApiHost`, and `TELEMETRY_SERVICE_VERSION` from the pod's `app.kubernetes.io/version` label on every backend workload.
- **PostHog project 190464** (set by hand, recorded in a runbook): time zone, session recording, the managed proxy.
- **Cost** at 1,000 monthly fans: 0 JPY added (PostHog free tiers: 1M events, 5,000 recordings, 100k LLM events).
