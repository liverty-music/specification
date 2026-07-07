## 1. Specification: catalogue and spec deltas

- [ ] 1.1 In `docs/analytics/event-catalog.md`, remove the following rows from the live catalogue table AND record each in a new "Removed events" section with its removal reason (phantom / redundant / double-count / firehose / wrong-altitude): `page.viewed`, `account.signup.started`, `artist.discovery.viewed`, `artist.follow.requested`, `user.deleted`, `sales_reminder.delivered`, `account.preferred_language.updated`, and the never-wired `ticket.lottery.entry.accepted/.rejected`, `ticket.lottery.result.assigned`, `ticket.purchase.completed/.failed`.
- [ ] 1.2 Rename the `account.login` row to `account.signin` (keep BE source, `trace_id?` only).
- [ ] 1.3 Add a `Collection status` column with two values (`active` / `dormant`) to the live table and mark `entry.zk_proof.verified/.rejected`, `ticket.mint.completed`, `ticket.email.parsed`, `ticket.purchase.initiated`, `entry.checkin.attempted` as `dormant` with an activation note (each has a real emitter; removed events live in the Removed events section from 1.1, not as a table status).
- [ ] 1.4 Re-cut the "Funnels and dashboards" section: primary funnel terminates at `concert.detail.viewed`; note `preferred_language` is now a person property, not an event.
- [ ] 1.5 Open the specification PR, get review + `buf-pr-checks.yml` green, merge to main.

## 2. Backend: remove deleted events and rename login

- [ ] 2.1 In `internal/usecase/analytics_events.go`, delete the constants `EventUserDeleted`, `EventTicketLotteryEntryAccepted`, `EventTicketLotteryEntryRejected`, `EventTicketLotteryResultAssigned`, `EventTicketPurchaseCompleted`, `EventTicketPurchaseFailed` and their `knownBackendEvents` entries.
- [ ] 2.2 Rename `EventAccountLogin` value `account.login` → `account.signin`; update the doc comment; update `SubjectAccountLogin` handling if the subject name is analytics-only.
- [ ] 2.3 Remove `sales_reminder.delivered`: delete `publishDeliveryOutcome`'s `PublishEvent(SubjectSalesReminderDelivered, ...)`, the `HandleSalesReminderDelivered` consumer handler, `EventSalesReminderDelivered`, `SubjectSalesReminderDelivered`, `SalesReminderDeliveredData`, and their `AllSubjects`/stream/KEDA references.
- [ ] 2.4 Remove the `preferred_language` analytics event: delete `HandleUserPreferredLanguageUpdated`, `EventAccountPreferredLanguageUpdated`; grep all consumers of `USER.preferred_language_updated` — if analytics is the only subscriber, remove the publish and subject too, otherwise keep the publish and remove only the analytics forwarding.
- [ ] 2.5 Update `analytics_consumer_test.go` and any affected unit tests; run `make check`.
- [ ] 2.6 Verify at merge time that PostHog has zero production `account.login` events (hard rename); if any exist, register a PostHog alias instead of a bare rename.

## 3. Backend ops: preserve reminder delivery-failure visibility

- [ ] 3.1 Add a log-based metric (or OTel counter) for sales-reminder delivery outcomes `no_subscription` / `failed` per `phase_stage`, replacing the visibility removed with `sales_reminder.delivered`.
- [ ] 3.2 Confirm the metric appears in Cloud Monitoring after deploy.

## 4. Frontend: remove deleted capture sites

- [ ] 4.1 In `src/services/analytics-events.ts`, remove `PageViewed`, `AccountSignupStarted`, `ArtistDiscoveryViewed`, `ArtistFollowRequested` from `Events`, `EventPropsMap`, and their prop types; keep the compile-time coverage guard green.
- [ ] 4.2 Delete the `capture(Events.PageViewed, ...)` call in `src/app-shell.ts` and the navigation-end subscription that feeds it.
- [ ] 4.3 Delete the `ArtistDiscoveryViewed` + `ArtistFollowRequested` captures in `src/routes/discovery/discovery-route.ts` (`onArtistSelected`, `onFollowFromSearch`), keeping the follow calls themselves.
- [ ] 4.4 Update affected specs/tests; run `make check`.

## 5. Ship and verify in production

- [ ] 5.1 Merge backend PR; cut a backend release; confirm ArgoCD rollout of the new consumer image.
- [ ] 5.2 Merge frontend PR; cut a frontend release; confirm the prod pin bump + ArgoCD sync.
- [ ] 5.3 In PostHog, confirm the deleted events stop arriving and `account.signin` arrives on login; confirm `notification.delivered` with `type = "sales_reminder"` still records reminder reach.
- [ ] 5.4 Run `openspec validate --strict`, mark all tasks done, and archive the change.
