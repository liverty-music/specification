## 1. Fan app analytics surface (frontend, components/infrastructure/fan/web/global/analytics)

- [x] 1.1 Set `capture_pageview: 'history_change'` and `capture_pageleave: true` in `analytics-service.ts`, and drop a `$pageview` whose path equals the previous one in `before_send` if posthog-js sends one for a query-only change; verify with unit tests annotated `// @spec components/infrastructure/fan/web/global/analytics "<scenario>"` for "In-app navigation", "Leaving the app" and "Analytics off"
- [x] 1.2 Add unit tests for "Campaign link with a referral code" and "No campaign keys" that run a capture through `before_send` on a URL with `utm_*` and `ref`, and confirm `utm_*` survive and `ref` appears nowhere; fix the strip only if a test fails
- [x] 1.3 Enable session recording behind the Session replay toggle with `maskAllInputs`, `maskTextSelector: '*'`, password masking and a `blockSelector` on the checkout, lottery entry, identity check and Settings screens; verify with tests for "Masked text", "Screen that is never recorded" and "Session replay off", and replace the "hard-disabled" comments and design Decision 12 note in `analytics-service.ts`
- [x] 1.4 `register({ display_mode })` at start; verify with a test for "Installed app"

## 2. Fan app events (frontend)

- [x] 2.1 Add the new events to `src/services/analytics-events.ts` with typed properties, and remove `entry.checkin.attempted`; verify `npm run typecheck` and the catalogue test pass
- [x] 2.2 Welcome: `onboarding.started` on `[Get Started]`; test annotated for components/infrastructure/fan/web/route/welcome "Get Started"
- [x] 2.2a Sign-up and sign-in starts: add a `source` option to `AuthService.signIn` / `signUp` and send `auth.started` with `kind` and `source` before the redirect; pass a source from each of the six callers (design Context "Sign-up starts"); tests annotated for stories/sign-up-or-sign-in "Sign-up from a banner", "Sign-in from the landing page" and "Analytics off"
- [x] 2.3 Discovery and follow store: `artist.follow.guest` in the guest branch of `FollowStore.follow` (`follow-store.ts:152`) and `onboarding.coachmark.shown` when the coach mark appears (renamed `onboarding.timetable.ready` and sent when the progress row becomes ready, by rework-fan-onboarding, which removes the coach mark); tests for components/infrastructure/fan/web/route/discovery "Guest follows a fifth artist" and "Timetable becomes ready"
- [x] 2.4 Guest merge: `guest.follows.merged` with the merged count when the merge finishes (`follow-store.ts:336`); test for stories/merge-guest-data-on-signup "Guest with five follows signs up"
- [x] 2.5 Push permission: `notification.permission.result` after `Notification.requestPermission()` (`notification-manager.ts:68`) with the answer and the start; test for components/infrastructure/fan/web/global/notification-prompt "Fan denies"
- [x] 2.6 Install: `pwa.install.banner_shown`, `pwa.install.answered` and `pwa.installed` (`pwa-install-service.ts:70-78`); test for components/infrastructure/fan/web/global/pwa-install-banner "Install from the banner"
- [x] 2.7 Event detail sheet and Event page: `concert.source.clicked` and `concert.calendar.added` (`event-detail-sheet.html:225, 234`), `concert.shared` and `concert.calendar.added` (`event-route.ts:420, 446`); tests for event-detail-sheet "Source link" and route/event "Share"
- [x] 2.8 Checkout and lottery entry: `checkout.step.viewed` on each step change and `ticket.purchase.initiated` in `hold()` (`checkout-route.ts:409`), `ticket.lottery.entry.started` in `toPersonalDetails()` (`lottery-entry-route.ts:278`) and `ticket.lottery.entry.submitted` after `confirm` succeeds (`:421`); tests for route/checkout "Fan reaches the final confirmation" and "Unverified fan on a verified sale", and route/lottery-entry "Entry submitted"
- [x] 2.9 Service worker: put `type`, `milestone` and the opened path in the opened and dismissed events (`notification-interaction.ts:242-260`, `sw.ts:131-158`); tests for components/infrastructure/fan/web/global/service-worker "Opened sales reminder" and "Older message without a type"
- [x] 2.10 Privacy Policy (ja and en) states masked session recordings, the screens never recorded, the transfer to PostHog, the purpose and the Settings toggle; test for components/infrastructure/fan/web/global/legal-document "Recording disclosed"

## 3. Backend fan signals (backend)

- [x] 3.1 Deliver adds the Notification type to the message data (`entity/push_notification.go`, `usecase/notification_delivery.go:99`); test for components/usecase/notification/deliver "Message names its type" next to the existing "Message identifies its notification"
- [x] 3.2 DeliverReminder adds the TicketSale and the milestone to the message data; test for components/usecase/ticket-sale-reminder/deliver-reminder "Apply-close reminder"
- [x] 3.3 Publish `ARTIST.hype_changed` from SetHype on every set (the level and the set time), and `ORDER.lottery_entry_drawn`, `ORDER.checkout_expired`, `ORDER.ticket_admitted` from RunDraw, ReleaseExpired and Admit, with entity event data types carrying `json` tags; usecase tests for set-hype "Hype raised" and "Signal failure", run-draw "Two entries, one place", release-expired "Hold lapsed", admit "Two tickets admitted in one scan"
- [x] 3.4 Add analytics consumer handlers and `consumer.go` rows for the four new subjects and for `ORDER.paid` (Order id as the PostHog `uuid`), and the event names in `usecase/analytics_events.go`; tests for fulfill-payment "Paid checkout" and "Announcement handled twice"
- [x] 3.5 Replace `AnalyticsClient.Enqueue` with one `Capture(ctx, AnalyticsEvent{Name, UUID, Time, DistinctID, Personless, Properties})`; the analytics consumer sends every forwarded event with UUID = the CloudEvent id and Time = the time the fact happened, read from the event data; add that time to the data of the 10 existing forwarded subjects (stored time of the fact where one exists, else the publisher's clock), with a table of the choice in design.md
- [x] 3.6 Remove `EventPublisher.PublishEventWithID` and `messaging.NewEventWithID`; every publisher uses `PublishEvent` (CloudEvent id = UUIDv7); revert `FollowRepository.SetHype` to return only an error

## 4. Backend search usage (backend; needs fix-trace-propagation)

- [x] 4.1 Add `AnalyticsClient.EnqueueSystem` (process name as distinct id, `$process_person_profile: false`) with unit tests for the property set and the validation of the event name
- [x] 4.2 Add `LLMGeneration` and its `$ai_generation` mapping in `internal/infrastructure/analytics/posthog/llm_generation.go`; fill it from both searchers for every request, retries and failures included; tests annotated for components/entity/concert/search "Search with a retry" and "Grounded search", and components/entity/ticket-sale/search-published-sales "Discarded sale"
- [x] 4.3 Send `concert.search.completed` from SearchNewConcerts (`concert_uc.go:466`, in the deferred outcome), `concert.ingest.completed` from CreateFromDiscovered and `ticket_sale.search.completed` from DiscoverForArtist; usecase tests for search-new-concerts "Nothing new" and "Search failed", create-from-discovered "Mixed batch", discover-for-artist "One new sale"

## 5. Infrastructure (cloud-provisioning)

- [x] 5.1 Create the PostHog managed proxy in the PostHog organization settings with a neutral subdomain of the public domain, add its CNAME as a `cloudflare.DnsRecord` with `proxied: false`, and set `posthogApiHost` in the prod and dev fan web ConfigMaps; verify `pulumi preview` shows one new record and the proxy status reaches live
- [x] 5.2 Set `TELEMETRY_SERVICE_VERSION` from the `app.kubernetes.io/version` label with the Downward API on every backend workload; verify `kustomize build` of the prod overlay shows the env on each Deployment and CronJob
- [x] 5.3 Write `docs/runbooks/posthog-project-settings.md`: time zone Asia/Tokyo, session recording on (the screens never recorded are kept out by the fan app, not by a project setting), the managed proxy; apply the settings in project 190464 and record the date

## 6. Production check (read-only, after all three releases)

- [x] 6.1 In PostHog, confirm for a fresh visit with `?utm_source=test`: page views per screen, `utm_source` on events, no `ref`, a masked recording, and `display_mode`; confirm the checkout is not in the recording
- [x] 6.2 After the next concert-discovery run, confirm `$ai_generation` events with `app_version` equal to the deployed release, and `concert.search.completed` and `concert.ingest.completed` in the same trace
- [x] 6.3 Confirm in PostHog billing that the month's projected usage stays inside the free tiers

## 7. Evaluation tool comparison (backend harness)

- [x] 7.1 Check whether a run from the Go harness can be attached to a Langfuse dataset run over `/api/public/otel`; record the answer in design.md Open Questions
- [x] 7.2 Compare Langfuse and PostHog from their published features for the harness's needs (datasets, experiment runs, judges, prompt management, Go ingestion, free tier, data access period, the PostHog project's enabled features); a recorded `FINAL` vs `LINKS` run to both is deferred until PostHog offline evaluations are enabled in project 190464
- [x] 7.3 Write the result and the choice under "Evaluation result" in design.md; if PostHog is kept, delete the Langfuse project (none was created)

## 8. Verification fixes (2026-10-25)

- [x] 8.1 Frontend: re-register `display_mode` (and `internal_traffic`) after `reset()` when analytics is on again
- [x] 8.2 Frontend: send `ticket.purchase.initiated` only after Start holds the tickets
- [x] 8.3 Frontend: keep an `auth.started` sent before the SDK loads and send it on the return with its time
- [x] 8.4 Frontend: report the ready timetable only while the progress row is shown
- [x] 8.5 Frontend: rename the `@spec` markers of the renamed scenarios; strengthen the tests of masked recording (real recorder in E2E), timetable ready (through `@watch`), the push offer's permission source and the install banner sequence
- [x] 8.6 Backend: fail Search when the caller's deadline passed during a call that succeeded, and on a normal response without text
- [x] 8.7 Backend: send `concert.ingest.completed` for a failed batch with its outcome
- [x] 8.8 Backend: assert the shared notification tag in the "notified twice" tests; correct the `order.paid` and `artist.hype.changed` comments in `analytics_events.go`

