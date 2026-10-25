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
| guest follow / timetable ready / follows merged | `artist.follow.guest`, `onboarding.timetable.ready`, `guest.follows.merged` | fan app |
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

The three new commerce subjects use the `ORDER` stream (`messaging/streams.go:19-20`, `ORDER.*`) instead of new `LOTTERY` and `TICKET` streams, so no stream is added. `ARTIST.hype_changed` goes on `ARTIST.*`. Each gets one analytics consumer handler and one row in `consumer.go`, as the existing ones do. `order.paid` uses the CloudEvent id as PostHog's `uuid`, so a redelivered `ORDER.paid` is stored once (spec: "Announcement handled twice"); a charge reported again is a second announcement and is stored again (see Implementation notes, "One kind of CloudEvent id").

- Alternative: call `AnalyticsClient` from the use cases. Rejected for fan signals: the code rule (`analytics_client.go:20-23`) keeps trust-critical events behind the domain event, which also gives retry through JetStream.

### Pipeline signals have no person

Add `AnalyticsClient.Capture` with `Personless: true`. It uses the process's `TELEMETRY_SERVICE_NAME` as distinct id and sets `$process_person_profile: false`, so no person profile is made. The searchers and the three use cases call it directly: these signals are not trust-critical and have no fan. `$ai_trace_id` and the use-case signals' `trace_id` come from the span in `ctx` (after `fix-trace-propagation`).

- Alternative: a domain event per search. Rejected: 3 new subjects and consumers for data that only analytics reads.

### One reporter for both searchers

`internal/infrastructure/analytics/posthog/llm_generation.go` defines `LLMGeneration` and maps it to `$ai_generation` properties: `$ai_trace_id`, `$ai_span_id`, `$ai_model`, `$ai_provider` = `google`, `$ai_input_tokens` (prompt + tool use), `$ai_output_tokens` (candidates + thinking), `$ai_cache_read_input_tokens`, `$ai_latency`, `$ai_is_error`, `$ai_error`, `$ai_stop_reason`, plus custom keys for the rest (`app_version`, `process`, `artist_id`, `official_site_url`, `linked_page_urls`, `search_from`, `series_ids`, `prompt_tokens`, `candidates_tokens`, `thinking_tokens`, `tool_use_tokens`, `web_search_queries`, `grounding_urls`, `url_context` as `{url, status}` objects, `finish_message`, `block_reason`, `draft_count`, `series_count`, `returned_sales`, `kept_sales`, `dropped_sales`). Both searchers fill the same type, which removes today's name and type mismatch. `$ai_input` and `$ai_output_choices` are not sent: the prompt is identified by `app_version`, and full responses come from the A/B harness. PostHog computes token cost from the model; the grounding fee is not in it and stays a billing-export figure.

### Release version from the pod label

Every backend workload sets `TELEMETRY_SERVICE_VERSION` from `metadata.labels['app.kubernetes.io/version']` with the Downward API, through one kustomize patch per overlay, so the OpenTelemetry resource and `app_version` carry the release. The A/B harness uses `git describe --always`.

### Fan app configuration

- `capture_pageview: 'history_change'` and `capture_pageleave: true`. A query-only change is not a page view (spec). posthog-js compares only the path (see Implementation notes), so no `before_send` drop is needed.
- Session recording: `maskAllInputs: true`, `maskTextSelector: '*'`, `maskInputOptions: { password: true }` and a `blockSelector` on the screens never recorded, and the fan app stops recording while one of those screens is shown (`/events/*/checkout`, `/events/*/lottery/*`, `/verify/*`, `/settings*`): AnalyticsService sets `disable_session_recording` from the Analytics and Session replay toggles and the current address, at init, on a consent change and on every navigation end. PostHog's current docs describe no URL blocklist setting, and recommend stopping and starting recording from the app on sensitive screens (posthog.com/docs/session-replay/how-to-control-which-sessions-you-record, "Record or ignore specific screens"). `maskTextSelector` masks text nodes only: a prod check found artist names in `aria-label`s (the unfollow and follow buttons), so `maskAttributeFn` masks `aria-label`, `aria-description`, `aria-roledescription`, `aria-valuetext`, `aria-placeholder`, `title`, `alt` and `placeholder`, and strips the query from own-origin addresses in other attributes; `maskAllElementAttributes` is not used because it also masks `class` and `style` and the replay loses its layout (frontend #861). The recorder is imported from the app's bundle (`posthog-js/dist/posthog-recorder`, a hashed chunk) before recording starts, only for a fan whose recording is on: the SDK otherwise fetches `posthog-recorder.js`, which EasyPrivacy blocks on any host, and it skips that fetch when the recorder is registered (frontend #863).
- `register({ display_mode })` at start from `matchMedia('(display-mode: standalone)')`.
- `api_host` becomes the proxy subdomain from `config.json` (`posthogApiHost`, `shared/config/app-config.ts:80`), with `ui_host: 'https://eu.posthog.com'`. The subdomain name avoids words that block lists match (`analytics`, `posthog`, `track`); it is chosen in task 5.1.

### Langfuse compared with PostHog on the A/B harness

The harness (`TestConcertSearcher_ABEval`, `searcher_integration_test.go:247`) records one run to Langfuse Cloud (Japan region, Hobby: 50k units a month, 30 days) over its OTLP endpoint `/api/public/otel` with the existing `otlptracehttp` exporter, and the same run to PostHog as a dataset with scores. Langfuse has no Go SDK, and its docs show experiments from Python and JS only; whether a Go run can be attached to a dataset is the first thing task 7.1 checks. The result and the choice go in this design under "Evaluation result". (The recorded run was not made; the choice was made from published features, see "Evaluation result".) The data sent is artists, public URLs and model output; no fan data.

## Risks / Trade-offs

- [Masking every text hides what a fan read when they left] → layout, taps and the screen path stay visible; unmasking chosen elements is a later decision.
- [The managed proxy's CNAME must stay DNS-only] → `proxied: false` on the record, as for `cdn.<publicDomain>`.
- [The page-view rules and `capture-client-errors`' error-report rule share `filterAnalyticsEvent`] → add the query-only page-view drop there, with tests next to its existing ones, so one filter decides what leaves the device.
- [Personless events are counted by PostHog like other events] → about 1,500 a month (Gemini calls and search outcomes), inside the free tier.

## Migration Plan

cloud-provisioning first: the event-consumer only binds to durables that NACK has created (`backend/internal/di/consumer.go`), so the five new Consumer CRs (`track-artist-hype-changed`, `track-order-paid`, `track-lottery-entry-drawn`, `track-checkout-expired`, `track-ticket-admitted`) and their KEDA triggers must exist before the backend release; the same PR carries the PostHog env of the two discovery CronJobs and `TELEMETRY_SERVICE_VERSION`. Then the backend (new subjects and consumers are additive; old consumers ignore unknown data keys; a job with no PostHog key reports nothing), then the fan app. Rollback is a revert per repository; no stored data depends on the new events.

## Implementation notes (2026-10-23)

Decisions taken while implementing, and where the code differs from the text above.

- **Page views**: posthog-js 1.438.13 maps `capture_pageview: 'history_change'` to `{ path: true }` and compares only `location.pathname` (`extensions/history-autocapture.js`, `_getCaptureOptions` / `_hasLocationChanged`), so a query-only change sends no page view and `before_send` needs no drop. `src/lib/analytics/page-view.spec.ts` runs the real SDK to show it.
- **Opt-out was undone by `reset()`** (existing defect, fixed here): posthog-js `reset()` clears its consent state (`posthog-core.js` `_reset`: `this.consent.reset()`), and `applyAnalyticsOptOutToSdk` called `opt_out_capturing()` before `reset()`, so a fan who turned Analytics off was captured again. The opt-out now runs after the reset, and a sign-out of an opted-out fan re-applies it.
- **No `$set_once` before identify**: an anonymous visitor's first campaign reaches PostHog as `$initial_utm_*` on the first event after `identify` (person processing is `identified_only`). Absent campaign keys are sent as `null`, which PostHog treats as not set.
- **Recording**: besides the masking above, `input[type="hidden"]` is blocked (rrweb records hidden inputs even with `maskAllInputs`), the blocked screens are the route elements `checkout-route`, `lottery-entry-route`, `lottery-entry-status-route`, `verify-callback-route`, `settings-route`, `passkeys-route` (`src/lib/analytics/session-recording.ts`), and `maskCapturedNetworkRequestFn` strips the query and fragment of the app's own addresses, which also covers the page `href`s a recording carries, so the referral rule holds for recordings.
- **Sign-up starts**: `AuthService` lives in `shared/`, which imports nothing from the fan app, so it publishes `AuthStarted(kind, source)` before the redirect and `AnalyticsService` captures it with `send_instantly` (fetch with keepalive). Left in the batch queue, the event was lost on the redirect in the E2E test.
- **Identify at the auth callback**: only `UserHydrationTask` identified, at the app's start; after a sign-up the app stays loaded, so events (the merge report included) stayed anonymous until the next start. The callback now identifies before it publishes `GuestMigrationRequested`.
- **Merge report**: `guest.follows.merged` is sent when the merge writes the account's receipt on this device for the first time (zero included). It is therefore also sent once on a first sign-in on a device; a merge left with failed items reports on the run that finishes it, counting that run's items.
- **Permission answer**: reported only when the browser actually asked (permission was `default`); sources are `notification_prompt`, `settings`, `post_signup_dialog`, `checkout`; the app's own re-subscribe passes no source and is not reported.
- **Push data keys**: `type` (the Notification type: `new_concerts`, `sales_reminder`, `ticket_sale_announcement`, `order_confirmation`) on every message; `ticket_sale_id` and `milestone` (`apply_open`, `apply_close_24h`, `result_day`) on a sales reminder. The Service Worker reports `type`, `milestone` and `path` (pathname only).
- **Personless distinct id**: a personless `Capture` (`Personless: true`) uses the process's existing `TELEMETRY_SERVICE_NAME` (`liverty-music-concert-discovery`, `liverty-music-consumer`, `liverty-music-sales-phase-discovery`) as distinct id and `process`, and `TELEMETRY_SERVICE_VERSION` as `app_version`. The discovery CronJobs get `POSTHOG_API_HOST` / `POSTHOG_PROJECT_API_KEY`; an empty key turns reporting off.
- **`$ai_generation` has no `trigger`**: the searchers do not know it; join on `$ai_trace_id` = `concert.search.completed.trace_id`, which carries `trigger`. `PublishedSaleSearchInput` gained `ArtistID` (not sent to the search service) so a generation names its Artist.
- **Proxy and project settings in Pulumi**: the bridged Terraform provider `PostHog/posthog` 1.0.25, already used by cloud-provisioning, holds the proxy (`posthog.ProxyRecord`, whose `targetCname` feeds the Cloudflare CNAME in the same program), the time zone (`posthog.Project`, imported with `protect: true`; the import keeps `UTC` and the next update sets `Asia/Tokyo`, because an import whose inputs differ fails) and recording on (`posthog.ProjectSettings` `sessionRecordingOptIn`). The screens never recorded are kept out by the fan app, not by a project URL blocklist (cloud-provisioning `docs/runbooks/posthog-project-settings.md`). The management key needs `organization:write` for the proxy. The subdomain is `beat.liverty-music.app`: PostHog's guide lists `analytics`, `tracking`, `telemetry`, `posthog` and `ph` as names already on block lists, and EasyPrivacy lists many `metrics.*` hosts. `posthogApiHost` switches to it only after the proxy is valid and after the frontend release whose CSP allows the proxy in `script-src` and `img-src` (posthog-js loads the recorder and remote config from `api_host`; `connect-src` already allows `*.liverty-music.app`); the dev overlay uses the same proxy, since the dev project is in the same organization (cloud-provisioning #701; unverified while dev is stopped).
- **No console logs in recordings**: the project has `capture_console_log_opt_in: true`; the fan app sets `enable_recording_console_log: false`, because console output (artist names, ids, errors) is not masked text.
- **Analytics event identity and time**: the analytics consumer sends every forwarded domain event to PostHog with `uuid` = the CloudEvent id and `timestamp` = the time the fact happened, carried in the event data (Order pay time, draw time, hold expiry, admit time, hype set time, and the times added to the 10 existing subjects; truncated to milliseconds). `ce_time` stays the publish time and is not used. PostHog treats events with the same `uuid`, `event`, `timestamp` and `distinct_id` as duplicates and merges them later (posthog.com/docs/data/events.md, "Event deduplication"), so a redelivered message is recorded once. `AnalyticsClient` has one method, `Capture`, whose caller sets every value; an event a use case sends directly (search outcomes, `$ai_generation`) uses a new `entity.NewID()` and the time the work ended.
  Where each forwarded subject's time comes from (backend `internal/entity/event_data.go`). Most rows have no stored creation time (the tables have no `created_at`, and adding one only for analytics is not in scope), so the publisher's clock at the moment of the fact is used:

  | subject | field | source of the time |
  |---|---|---|
  | `USER.created` | `UserCreatedData.CreateTime` | `UserUseCase.Create`'s clock right after the row is stored (`users` has no creation time) |
  | `USER.logged_in` | `UserLoggedInData.LoginTime` | `created_at` of the Zitadel `session.user.checked` event (stored in Zitadel's event store); the handler's clock only if Zitadel sends none |
  | `ARTIST.followed` | `ArtistFollowedData.FollowTime` | `FollowUseCase`'s clock after `Follow.Follow` |
  | `ARTIST.unfollowed` | `ArtistUnfollowedData.UnfollowTime` | `FollowUseCase`'s clock after `Follow.Unfollow` |
  | `ARTIST.hype_changed` | `ArtistHypeChangedData.SetTime` | `FollowUseCase`'s clock after `Follow.SetHype` |
  | `NOTIFICATION.subscribed` | `NotificationSubscribedData.SubscribeTime` | `PushSubscriptionUseCase.Create`'s clock after the row is stored |
  | `NOTIFICATION.unsubscribed` | `NotificationUnsubscribedData.UnsubscribeTime` | `PushSubscriptionUseCase.Delete`'s clock after the row is removed |
  | `NOTIFICATION.delivered` | `NotificationDeliveredData.DeliverTime` | the Notification's delivered time, the value stored as `notifications.delivered_at` |
  | `TICKET_JOURNEY.status_changed` | `TicketJourneyStatusChangedData.ChangeTime` | `TicketJourneyUseCase.SetStatus`'s clock after the upsert |
  | `ORGANIZER.created` | `OrganizerCreatedData.ActivateTime` | `OrganizerUseCase`'s clock when the row turns active |
  | `ORGANIZER.artist_associated` | `OrganizerArtistAssociatedData.AssociateTime` | `OrganizerUseCase.AssociateArtist`'s clock after the row is stored |
  | `ORDER.paid` | `OrderPaidData.PayTime` | the Order's stored pay time (`orders.pay_at`) |
  | `ORDER.lottery_entry_drawn` | `LotteryEntryDrawnData.DrawTime` | `LotteryEntryUseCase.RunDraw`'s clock at the start of the draw (one time for every entry of the draw) |
  | `ORDER.checkout_expired` | `CheckoutExpiredData.HoldExpireTime` | the Checkout's stored hold expiry (`checkouts.hold_expire_at`) |
  | `ORDER.ticket_admitted` | `TicketAdmittedData.AdmitTime` | the admit time `Ticket.Admit` returns, stored as `tickets.admit_at` |

  A message whose data has no time (published before the field existed) is acknowledged without forwarding: its publish time is not when the fact happened.
- **One kind of CloudEvent id**: every publisher uses `PublishEvent`, so every CloudEvent id is a UUIDv7 that nothing else reuses. `PublishEventWithID` (an entity id or a business-key hash as the message id) is removed: an entity id is not an event id. Known limitation, accepted for now: a fact announced twice (FulfillPayment on a repeated Stripe webhook; a notification request rebuilt when its trigger is redelivered) gets two ids, so PostHog can hold two `order.paid` events and a fan can get a second push for one notification. Before, JetStream dropped the second message within the stream's 2-minute window. Consumers of `ORDER.paid` and `RESALE_LISTING.refunded` stay idempotent by their business ids. The fix (a transactional outbox, or durable execution evaluated first on one payment flow) is a follow-up change; BigQuery marts count orders by `order_id`, not by event.
- **SetHype has no previous level**: the signal carries the level set and the time; the previous level is the fan's previous signal for the artist (or the default at follow), derived in BigQuery with `LAG()`. `FollowRepository.SetHype` keeps its original signature. The fan app sends no same-level set (`my-artists-route.ts:338`).
- **Exhausted transient retries fail the search**: Concert.Search fails with Unavailable instead of returning no concerts (spec delta "Transient failures are retried"). The use case's existing error path then records the ConcertSearch as failed, which also lets the next run search the Artist again instead of treating an unsearched Artist as fresh for 24 hours, and the daily job's circuit breaker stops a run during an outage. The ticket-sale searcher already fails on any call error.
- **Release version**: two kustomize patches per overlay (Deployment and CronJob pod templates differ), and each base workload declares `env: []` so the JSON patch applies. The dev overlay has no `app.kubernetes.io/version` label, so dev reports an empty version.

## Evaluation result (2026-10-25)

**PostHog is kept; no Langfuse project was created.** The tools were compared from their published features, not from a recorded run (tasks 7.2, 7.3):

| Need of the harness | Langfuse (Hobby) | PostHog (project 190464) |
| --- | --- | --- |
| Price | free, 50k units a month (a trace, an observation and a score are each a unit) | AI events free up to 100k a month (billing overview, 2026-10-24) |
| Data access | 30 days (Core: 90 days, $29 a month) | not checked |
| Users | 2 | not checked |
| Datasets | yes | yes (`llma-dataset-*`) |
| Runs of an evaluation executed outside the tool | yes (SDK and UI; from Go over OTel span attributes, see Open Questions) | offline evaluations exist but are not enabled in this project (no `llma-offline-*` tools) |
| LLM-as-a-judge | yes | yes, beta, on captured generations |
| Prompt management | yes | yes (`llma-prompt-*`) |
| Go ingestion | no Go SDK; OTLP with `langfuse.*` attributes, scores through the Scores API | `posthog-go`, already sending `$ai_generation` from prod |

Sources: langfuse.com/pricing; langfuse.com/integrations/native/opentelemetry/experiments; PostHog billing overview and MCP tool list for project 190464; posthog.com/docs/llm-analytics/evaluations.

Both tools cover datasets, runs, judges and prompts, so features do not decide. PostHog already holds the prod generations through the SDK the backend uses, and keeping one tool avoids a second service, account and key for the harness alone. Langfuse's advantage is an experiment view available today; Hobby's 30-day data access would also hide the previous run of a harness that is run about monthly (the cadence is an estimate). A recorded `FINAL` vs `LINKS` run to both was not made: with PostHog's offline evaluations off, it would compare Langfuse's experiment view with a hand-written SQL view, a result known in advance, at the cost of dev Gemini spend ($1–4 by the 2026-10-07 runs) and a Langfuse account. It is worth making once offline evaluations are enabled in project 190464; then the harness publishes its runs there and the `cmd/analyze-*` tools are compared against that view.

## Open Questions

- Whether a Go harness run can be attached to a Langfuse dataset run (task 7.1). If it cannot, the comparison uses Langfuse traces and scores without its experiment view, and the result says so.
  - **Answer (2026-10-24, from Langfuse's docs, not yet tried):** yes, without an SDK. Langfuse groups OTLP traces into an experiment run from span attributes ("Experiments via OpenTelemetry", langfuse.com/integrations/native/opentelemetry/experiments): `langfuse.experiment.id`, `.name` and `.dataset.id` as Baggage on every span; on each item's root span `langfuse.experiment.item.id`, `langfuse.experiment.item.root_observation_id` (equal to its own span id), `langfuse.observation.input` / `.output` and optionally `langfuse.experiment.item.expected_output`. The dataset need not exist in Langfuse first: local, stable ids correlate repeated runs. Each item is one trace with no enclosing experiment span. Scores are not span attributes: they go through the Scores API, keyed by the root span's trace id and span id. So the harness needs one root span per cell with these attributes, the existing `otlptracehttp` exporter pointed at Langfuse, and one Scores API call per cell for recall.
