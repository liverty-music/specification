## Context

See proposal.md for why. The constraints that shape the approach, all read from the code on 2026-10-23:

- **Fan app**: PostHog is initialised in `frontend/src/lib/analytics/analytics-service.ts:440-476` with `autocapture: false`, `capture_pageview: false`, `disable_session_recording: true`, `capture_exceptions: false` and `before_send: filterAnalyticsEvent` (`src/lib/analytics/error-report-filter.ts`, from `capture-client-errors`, frontend #828). Events can only be sent from the catalogue in `src/services/analytics-events.ts:214-227`. The installed `posthog-js` is 1.438.13 (`package-lock.json`); its config type accepts `capture_pageview: 'history_change'`, `capture_pageleave`, `session_recording.{maskAllInputs, maskTextSelector, blockSelector}` and `register()` (`@posthog/types` 1.416.0, `posthog-config.d.ts:1347, 1355, 531-599`; `posthog.d.ts:358`).
- **UTM**: posthog-js already reads `utm_*` from `document.URL` inside `capture()` and registers them as their own properties and as `$initial_utm_*` person properties (`save_campaign_params: true` by default, `posthog-core.js:218, 1522-1530`), before `before_send` runs (`:1663`). Today's 0 UTM events mean no campaign link has been used yet, not that the strip removes them.
- **Service worker**: it posts opened and dismissed events itself with only `notification_id` (`src/lib/analytics/notification-interaction.ts:242-260`); it reads the push message's `data.url` and `data.notification_id` (`src/sw.ts:131-158`).
- **Backend signals**: use cases publish domain events, and `internal/adapter/event/analytics_consumer.go` forwards them to PostHog (`internal/usecase/analytics_client.go:20-23`; subscriptions in `internal/di/consumer.go:327-337`). `AnalyticsClient.Enqueue` requires a user UUID as distinct id (`internal/infrastructure/analytics/posthog/posthog_client.go:141-146`). `ORDER.paid` exists but has no analytics subscription.
- **Search calls**: both searchers already gather the usage fields (`PassMetadata` and `SearchMetadata` in `internal/infrastructure/gcp/gemini/searcher.go:193-262`; `logResponseMetadata` in `ticket_sale_searcher.go:486-553`) but log them under different names and types (`usage_metadata` vs `usage`; `url_context_retrieved` as an int vs a string array).
- **Version**: pods carry `app.kubernetes.io/version` (`cloud-provisioning/k8s/namespaces/backend/overlays/prod/kustomization.yaml:52`), but `TELEMETRY_SERVICE_VERSION` is unset and defaults to `1.0.0` (`backend/pkg/config/config.go:404`).
- **Proxy**: PostHog's managed reverse proxy is free on Cloud and needs one DNS-only CNAME; Cloudflare records are already created with `cloudflare.DnsRecord` and `proxied: false` (`cloud-provisioning/src/gcp/components/object-storage.ts:424-439`).
- **Overlap**: `capture-client-errors` shipped its frontend in #828 (2026-10-23) and is not archived yet; it MODIFIES the query-string requirement and the Privacy Policy disclosure requirement, and this change only ADDS requirements to those specs, so the two archive in either order. #828 also added error-report steps (`IErrorBoundaryService.addBreadcrumb`) at several actions this change reports: `follow-store.ts:147`, `checkout-route.ts:413`, `lottery-entry-route.ts:404`, `event-detail-sheet.ts:207` and every sign-in or sign-up start. A step is kept on the device for an error report; an analytics event is sent at once and obeys the opt-out. They stay two calls, placed next to each other.
- **Sign-up starts**: the fan app starts hosted login from six places: `auth-status.ts:16,22`, `dashboard-route.ts:1130`, `event-route.ts:468`, `my-artists-route.ts:391`, `settings-route.ts:603,609` and `welcome-route.ts:487` (sign-in only; `[Get Started]` starts the guest flow, not sign-up). All go through `AuthService.signIn` / `signUp`.

## Goals / Non-Goals

**Goals:**

- Every requirement in this change's specs, with one PostHog event name per signal and one property name per meaning across frontend and backend.
- Fan-level server signals keep the existing path (domain event → analytics consumer); pipeline signals have no fan and need a path without a person.

**Non-Goals:**

- Error reporting (`capture-client-errors`), identity check events (`identity-ekyc-jpki`), BigQuery and dashboards (follow-up change).
- Sampling performance events. Volumes stay inside the free tier at 1,000 monthly fans (proposal, Impact).

## Decisions

### Event names

One namespace per subject, dot-separated, as the catalogue already does.

| signal | event | sent by |
|---|---|---|
| onboarding started | `onboarding.started` | fan app (welcome) |
| sign-up or sign-in started | `auth.started` with `kind` (sign_up / sign_in) and `source` (the screen or control) | fan app, inside `AuthService.signIn` / `signUp`, which take a `source` option |
| guest follow / coach mark / follows merged | `artist.follow.guest`, `onboarding.coachmark.shown`, `guest.follows.merged` | fan app |
| permission answer | `notification.permission.result` | fan app |
| install banner / install answer / installed | `pwa.install.banner_shown`, `pwa.install.answered`, `pwa.installed` | fan app |
| source link / calendar / share | `concert.source.clicked`, `concert.calendar.added`, `concert.shared` | fan app |
| checkout step / purchase start | `checkout.step.viewed`, `ticket.purchase.initiated` (existing) | fan app |
| lottery entry start / submit | `ticket.lottery.entry.started`, `ticket.lottery.entry.submitted` (existing) | fan app |
| hype changed | `artist.hype.changed` | backend, `ARTIST.hype_changed` |
| order paid | `order.paid` | backend, `ORDER.paid` (existing subject) |
| lottery result | `ticket.lottery.result` | backend, `ORDER.lottery_entry_drawn` |
| checkout expired | `checkout.expired` | backend, `ORDER.checkout_expired` |
| ticket admitted | `ticket.admitted` | backend, `ORDER.ticket_admitted` |
| search outcomes | `concert.search.completed`, `concert.ingest.completed`, `ticket_sale.search.completed` | backend, direct |
| external call | `$ai_generation` | backend, direct |

`entry.checkin.attempted` stays unsent and is removed from the catalogue: `ticket.admitted` from the server replaces it.

### Commerce signals go on the existing ORDER stream

The three new commerce subjects use the `ORDER` stream (`messaging/streams.go:19-20`, `ORDER.*`) instead of new `LOTTERY` and `TICKET` streams, so no stream is added. `ARTIST.hype_changed` goes on `ARTIST.*`. Each gets one analytics consumer handler and one row in `consumer.go`, as the existing ones do. `order.paid` uses the Order id as PostHog's `uuid`, so a redelivered `ORDER.paid` is stored once (spec: "Announcement handled twice").

- Alternative: call `AnalyticsClient` from the use cases. Rejected for fan signals: the code rule (`analytics_client.go:20-23`) keeps trust-critical events behind the domain event, which also gives retry through JetStream.

### Pipeline signals have no person

Add `AnalyticsClient.EnqueueSystem(ctx, process, event, props)`. It uses the process name (`concert-discovery`, `event-consumer`, `sales-phase-discovery`) as distinct id and sets `$process_person_profile: false`, so no person profile is made. The searchers and the three use cases call it directly: these signals are not trust-critical and have no fan. `$ai_trace_id` and the use-case signals' `trace_id` come from the span in `ctx` (after `fix-trace-propagation`).

- Alternative: a domain event per search. Rejected: 3 new subjects and consumers for data that only analytics reads.

### One reporter for both searchers

`internal/infrastructure/analytics/posthog/llm_generation.go` defines `LLMGeneration` and maps it to `$ai_generation` properties: `$ai_trace_id`, `$ai_span_id`, `$ai_model`, `$ai_provider` = `google`, `$ai_input_tokens` (prompt + tool use), `$ai_output_tokens` (candidates + thinking), `$ai_cache_read_input_tokens`, `$ai_latency`, `$ai_is_error`, `$ai_error`, `$ai_stop_reason`, plus custom keys for the rest (`app_version`, `process`, `trigger`, `artist_id`, `official_site_url`, `linked_page_urls`, `search_from`, `series_ids`, `prompt_tokens`, `candidates_tokens`, `thinking_tokens`, `tool_use_tokens`, `web_search_queries`, `grounding_urls`, `url_context` as `{url, status}` objects, `finish_message`, `block_reason`, `draft_count`, `series_count`, `returned_sales`, `kept_sales`, `dropped_sales`). Both searchers fill the same type, which removes today's name and type mismatch. `$ai_input` and `$ai_output_choices` are not sent: the prompt is identified by `app_version`, and full responses come from the A/B harness. PostHog computes token cost from the model; the grounding fee is not in it and stays a billing-export figure.

### Release version from the pod label

Every backend workload sets `TELEMETRY_SERVICE_VERSION` from `metadata.labels['app.kubernetes.io/version']` with the Downward API, through one kustomize patch per overlay, so the OpenTelemetry resource and `app_version` carry the release. The A/B harness uses `git describe --always`.

### Fan app configuration

- `capture_pageview: 'history_change'` and `capture_pageleave: true`. A query-only change is not a page view (spec). Whether posthog-js sends a page view when only the query string changes is not confirmed from its source; task 1.1 tests it, and if it does, `before_send` drops a `$pageview` whose path equals the previous one.
- Session recording: `maskAllInputs: true`, `maskTextSelector: '*'`, `maskInputOptions: { password: true }` and a `blockSelector` on the screens never recorded, plus PostHog's URL blocklist for `/events/*/checkout`, `/events/*/lottery/*`, `/verify/*` and `/settings*`. `disable_session_recording` follows the Session replay toggle, which `ConsentService` already stores.
- `register({ display_mode })` at start from `matchMedia('(display-mode: standalone)')`.
- `api_host` becomes the proxy subdomain from `config.json` (`posthogApiHost`, `shared/config/app-config.ts:80`), with `ui_host: 'https://eu.posthog.com'`. The subdomain name avoids words that block lists match (`analytics`, `posthog`, `track`); it is chosen in task 5.1.

### Langfuse compared with PostHog on the A/B harness

The harness (`TestConcertSearcher_ABEval`, `searcher_integration_test.go:247`) records one run to Langfuse Cloud (Japan region, Hobby: 50k units a month, 30 days) over its OTLP endpoint `/api/public/otel` with the existing `otlptracehttp` exporter, and the same run to PostHog as a dataset with scores. Langfuse has no Go SDK, and its docs show experiments from Python and JS only; whether a Go run can be attached to a dataset is the first thing task 7.1 checks. The result and the choice go in this design under "Evaluation result". The data sent is artists, public URLs and model output; no fan data.

## Risks / Trade-offs

- [Masking every text hides what a fan read when they left] → layout, taps and the screen path stay visible; unmasking chosen elements is a later decision.
- [The managed proxy's CNAME must stay DNS-only] → `proxied: false` on the record, as for `cdn.<publicDomain>`.
- [The page-view rules and `capture-client-errors`' error-report rule share `filterAnalyticsEvent`] → add the query-only page-view drop there, with tests next to its existing ones, so one filter decides what leaves the device.
- [Personless events are counted by PostHog like other events] → about 1,500 a month (Gemini calls and search outcomes), inside the free tier.

## Migration Plan

Backend first (new subjects and consumers are additive; old consumers ignore unknown data keys), then cloud-provisioning (DNS, ConfigMap, Downward API), then the fan app. Rollback is a revert per repository; no stored data depends on the new events.

## Open Questions

- Whether a Go harness run can be attached to a Langfuse dataset run (task 7.1). If it cannot, the comparison uses Langfuse traces and scores without its experiment view, and the result says so.
