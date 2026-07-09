## 1. Phase 1 — Backend: fail loud + liveness

- [ ] 1.1 Make consumer startup establish subscriptions synchronously; on any subscribe/bind error, log ERROR with the topic and exit non-zero (crashloop) instead of continuing (`internal/di/consumer.go`, `internal/infrastructure/messaging/subscriber.go`)
- [ ] 1.2 Track in-process the set of expected subscriptions and their bound state + NATS connection status in the subscriber
- [ ] 1.3 Update the consumer `/healthz` (:8081) to report unhealthy when the router is stopped or any expected durable is unbound, with an N-failure grace to avoid flapping
- [ ] 1.4 Unit tests: subscribe error aborts startup; health handler returns unhealthy when a subscription is missing / connection down
- [ ] 1.5 `make check` passes

## 2. Phase 1 — cloud-provisioning: backlog alert + deploy strategy

- [ ] 2.1 Decide the backlog metric pipeline (NATS Prometheus exporter + Google Managed Prometheus vs. `jsz` poller → log-based metric) and wire the metric source
- [ ] 2.2 Add a Cloud Monitoring alert policy: JetStream consumer backlog high and not decreasing for a sustained window, per stream/consumer
- [ ] 2.3 Set the consumer Deployment update strategy to `Recreate` (or `maxSurge=0, maxUnavailable=1`) so rollouts never run two pods over one durable set
- [ ] 2.4 Confirm the liveness/readiness probe config points at the consumption-aware endpoint from task 1.3

## 3. Phase 1 — Ship to prod & verify

- [ ] 3.1 Open backend PR (fail-loud + liveness), pass CI, merge, cut release, bump prod pin
- [ ] 3.2 Open cloud-provisioning PR (alert + strategy), pass CI, merge; confirm ArgoCD syncs
- [ ] 3.3 Verify in prod: consumer healthy and draining; then force a transient stall (e.g. temporarily remove a durable) and confirm the backlog alert opens an incident and the pod fails loud / restarts; restore

## 4. Phase 2 — Backend: startup reconciliation + bare durable names

- [ ] 4.1 Add a raw JetStream pre-flight reconcile in consumer startup: for each topic, compare desired vs. existing `ConsumerInfo` and delete+recreate on drift (name / deliver group / delivery policy)
- [ ] 4.2 Change `consumerName(topic)` to return the bare per-subject name (drop the `consumer_` prefix); keep per-subject uniqueness for durable and deliver group
- [ ] 4.3 Ensure reconciliation removes superseded/no-longer-desired durables (the `consumer_*` and stale bare orphans) or documents which are left to age out
- [ ] 4.4 Unit tests: reconcile recreates a drifted durable, leaves a matching one untouched; name helper produces bare names
- [ ] 4.5 `make check` passes

## 5. Phase 2 — cloud-provisioning: KEDA + probes

- [ ] 5.1 Confirm KEDA ScaledObject triggers reference the bare durable names (already the case) and are consistent with the app after the rename; adjust any that drifted
- [ ] 5.2 Confirm probe config still valid after the naming change

## 6. Phase 2 — Ship to prod, migrate durables & verify

- [ ] 6.1 Open backend PR (reconciliation + bare names), pass CI, merge, cut release, bump prod pin (ship only after Phase 1 is live so any issue fails loud + alerts)
- [ ] 6.2 During the rollout, verify reconciliation converges: all durables bare-named, `push_bound=true`, backlog draining, KEDA reading real backlog
- [ ] 6.3 Re-publish any critical events left pending by the migration if needed (stream 7d retention), as in the incident recovery
- [ ] 6.4 Confirm the backlog alert is green and no orphan durables remain

## 7. Cleanup & runbook

- [ ] 7.1 Remove any leftover orphan durables from the 2026-07 incident
- [ ] 7.2 Document the durable-reconciliation path as the required procedure for any future durable name/config change (release runbook)
- [ ] 7.3 Update the incident memory / postmortem reference with the shipped controls
