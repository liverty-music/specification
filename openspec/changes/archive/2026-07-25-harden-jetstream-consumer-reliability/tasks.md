## 1. Phase 1 — Backend: fail loud + liveness

- [x] 1.1 Make consumer startup establish subscriptions synchronously; on any subscribe/bind error, log ERROR with the topic and exit non-zero (crashloop) instead of continuing (`internal/di/consumer.go`, `internal/infrastructure/messaging/subscriber.go`)
- [x] 1.2 Track in-process the set of expected subscriptions and their bound state + NATS connection status in the subscriber
- [x] 1.3 Update the consumer `/healthz` (:8081) to report unhealthy when the router is stopped or any expected durable is unbound, with an N-failure grace to avoid flapping
- [x] 1.4 Unit tests: subscribe error aborts startup; health handler returns unhealthy when a subscription is missing / connection down
- [x] 1.5 `make check` passes

## 2. Phase 1 — cloud-provisioning: backlog alert + deploy strategy

- [x] 2.1 Decide the backlog metric pipeline (NATS Prometheus exporter + Google Managed Prometheus vs. `jsz` poller → log-based metric) and wire the metric source — chose exporter + GMP: prometheus-nats-exporter sidecar (prod nats overlay) + GMP `PodMonitoring` (`nats-jetstream-backlog`)
- [x] 2.2 Add a Cloud Monitoring alert policy: JetStream consumer backlog high and not decreasing for a sustained window, per stream/consumer — `consumerBacklogAlertPolicy` (PromQL `min_over_time(...[15m]) > 0`)
- [x] 2.3 Set the consumer Deployment update strategy to `Recreate` (or `maxSurge=0, maxUnavailable=1`) so rollouts never run two pods over one durable set
- [x] 2.4 Confirm the liveness/readiness probe config points at the consumption-aware endpoint from task 1.3 — livenessProbe already targets `/healthz:8081`, now consumption-aware; app grace composes with probe `failureThreshold: 3`

## 3. Phase 1 — Ship to prod & verify

- [x] 3.1 Open backend PR (fail-loud + liveness), pass CI, merge, cut release, bump prod pin — PR #365 merged (unblocked via Go 1.26.5 bump #367 for GO-2026-5856); release v1.21.0 cut; automated Bump Prod Pin set backend prod overlay to v1.21.0 (ArgoCD rolling out)
- [x] 3.2 Open cloud-provisioning PR (alert + strategy), pass CI, merge; confirm ArgoCD syncs — PRs #388/#389/#390/#391 merged; ArgoCD synced exporter+PodMonitoring+strategy(maxSurge:0); prod pulumi up v208 succeeded → alert policy `Consumer JetStream Backlog Stall` live+enabled with real GMP data. Follow-up fixes found in prod verify: metric name `nats_consumer_num_pending` (#389), Recreate→maxSurge:0 (#389), disableMetricValidation (#390), notificationRateLimit is log-based-only so removed from the metric-based policy (#391 — the real cause of the aborted ups)
- [x] 3.3 Verify in prod: consumer healthy and draining; then force a transient stall and confirm the backlog alert opens an incident; restore — VERIFIED 2026-07-21. consumer healthy (v1.21.0, 0 restarts, num_pending drains to 0). Stall injected safely via a throwaway PULL consumer `TEST_backlog_probe` on CONCERT (deliver=all → num_pending=2, never drains, zero impact on real consumers). GMP PromQL `min_over_time(nats_consumer_num_pending[15m])>0` went true immediately (min over partial window) and, after the 300s sustain, the `Consumer JetStream Backlog Stall` incident opened and fired the Slack/Chat notification (user-confirmed). Probe deleted → series gone → condition clears → incident auto-closes. NOTE: a single-durable stall is caught by the backlog ALERT, not liveness (liveness catches router-stopped / conn-down / startup-bind-failure); the two are complementary per design D3+D4.

## 4. Phase 2 — Backend: behavior-named per-handler consumers + reconciliation (D5/D7/D9)

- [x] 4.1 Add a raw JetStream pre-flight reconcile in consumer startup (D1/D9): list all consumers on owned streams and delete any that are not a desired behavior-named durable — i.e. delete when name ∉ desired set (old `consumer_*`, old subject-named like `CONCERT_created`), OR `deliver_group != own name` (the shared `"consumer"` group), OR delivery policy drifted; leave correct ones untouched. watermill then (re)creates the correct per-behavior durables.
- [x] 4.2 Replace `consumerName(topic)` with **behavior-based** naming: build one watermill subscriber per handler via `NewSubscriberWithNatsConn` sharing a single `*nats.Conn`, each with `DurableCalculator`/`SubjectCalculator` fixed to the handler's behavior name (durable = deliver group = behavior; filter = subject). Names per design D5 table (`ingest-concert`, `notify-concert`, `resolve-artist-name/image`, `verify-user-email`, `track-*`, `notify-sales-*`, `log-poison`).
- [x] 4.3 Fan-out fix (D7): confirm the two multi-handler subjects (`ARTIST.created`, `USER.created`) now produce two independent consumers each, and reconciliation removes all superseded durables (old `consumer_*`, subject-named, dead `ACCOUNT.login`).
- [x] 4.4 Subject normalization (D8): `internal/entity/event_data.go` `SALES_PHASE.reminder.due`→`SALES_PHASE.reminder_due`; `ACCOUNT.login`→`USER.logged_in`; `streams.go` drop the `ACCOUNT` stream and change `SALES_PHASE.>`→`SALES_PHASE.*`; update all publisher call sites + `specification/docs/analytics/event-catalog.md`.
- [x] 4.5 Unit tests: reconcile deletes a shared-group/subject-named/prefixed durable and leaves a correct behavior-named one; per-handler subscriber factory produces behavior-named durables + matching deliver group; multi-handler subject yields two durables.
- [x] 4.6 `make check` passes

## 5. Phase 2 — cloud-provisioning: KEDA + streams (D5/D8)

- [x] 5.1 Rename KEDA ScaledObject triggers to the behavior-based durable names (`notify-concert`, `resolve-artist-name`, `track-*`, …); update stream refs for `USER.logged_in` (drop `ACCOUNT`); verify HPA `currentMetrics` has no `<unknown>`
- [x] 5.2 Confirm probe config still valid after the naming change

## 6. Phase 2 — Ship to prod, migrate durables & verify (also remediates the live partial-outage)

- [x] 6.1 Open backend PR — #368 merged (unblocked via x/text bump #370 for GO-2026-5970); release v1.22.0; auto pin-bump set prod overlay to v1.22.0
- [x] 6.2 cloud-provisioning KEDA PR #392 merged; ArgoCD syncing behavior-named triggers
- [x] 6.3 During the rollout, verify reconciliation converges: every behavior has its own durable with `deliver_group == name` and `push_bound=true` — including the previously-missing `notify-concert`, `notify-sales-*`, `track-*`, and the two-way `resolve-artist-*` fan-out; backlog draining; KEDA reading real backlog
- [x] 6.4 Re-publish any critical events left unconsumed by the pre-fix broken state / migration (stream 7d retention), as in the incident recovery
- [x] 6.5 Confirm the backlog alert is green and no orphan durables remain

## 7. Cleanup & runbook

- [x] 7.1 Remove any leftover orphan durables (old `consumer_*`, old subject-named `CONCERT_created` etc., dead `ACCOUNT.login`)
- [x] 7.2 Document the durable-reconciliation path + behavior-naming convention as the required procedure for any future durable/subject change (release runbook)
- [x] 7.3 Update the incident memory / postmortem reference with the shipped controls
