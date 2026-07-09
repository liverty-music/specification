## Context

The backend `consumer` app subscribes to NATS JetStream via watermill-nats. Durables are created lazily by the watermill router the first time it subscribes to each topic; their names and deliver groups come from one helper (`consumerName(topic)`), currently `consumer_<subject>`. JetStream never rewrites an existing durable's config, and nats.go refuses to bind a subscription whose requested config conflicts with a pre-existing consumer on the same filter subject. During the 2026-07 incident, a stale durable (old shared `deliver_group="consumer"`) made the new subscription fail; that one failure aborted the whole router's startup, every subject wedged, and nothing alerted because the pod stayed `Running` (HTTP liveness only) and emitted no ERROR/poison. Constraints: prod consumer runs `min=max=1` (KEDA); GKE Autopilot; Cloud Monitoring for alerting; watermill-nats hides consumer creation behind `QueueSubscribe`.

## Goals / Non-Goals

**Goals:**
- A stalled consumer is detected within minutes, independent of logs.
- A subscription/config failure crashes the pod (loud) instead of silently disabling consumption.
- A wedged pod is auto-restarted by Kubernetes.
- A durable name/config change can never again wedge on a stale durable.
- Durable names drop the meaningless `consumer_` prefix, which also re-aligns KEDA.

**Non-Goals:**
- Redesigning the event model, streams, or moving off watermill-nats.
- Guaranteed zero-loss replay of already-published events (streams retain 7d; lost events are re-published operationally as in the incident).
- Multi-replica consumer scaling (stays `min=max=1` in prod).

## Decisions

**D1 — Startup durable reconciliation via a raw JetStream pre-flight.** Before starting the watermill router, run a reconcile step using a raw nats.go `JetStreamContext`: for each owned topic compute the desired consumer config, fetch `ConsumerInfo`, and if it is missing or drifted (name / deliver group / delivery policy differ) delete and recreate it. watermill then binds to a now-correct durable. *Alternative rejected:* relying on watermill to reconcile — it only `QueueSubscribe`s and cannot detect drift.

**D2 — Fail loud.** The reconcile + subscription establishment is synchronous at startup; any error is logged at ERROR (with topic) and returns a non-zero exit so the pod crashloops. This makes the pre-existing `Consumer ERROR Log` alert fire and lets Kubernetes restart. *Alternative rejected:* logging-and-continue (today's behavior) — it hides missing consumers.

**D3 — Liveness reflects consumption.** The subscriber tracks, in-process, whether every expected subscription is established and the NATS connection is up; `/healthz` reports unhealthy when the router is stopped or any expected durable is unbound (with a small failure-count grace to avoid flapping). *Alternative considered:* probe the NATS monitoring endpoint from the health handler — heavier and adds a cross-service dependency in the hot path; keep it in-process, optionally cross-checked by the backlog alert.

**D4 — Backlog alert pipeline.** Add a Cloud Monitoring alert on JetStream consumer `num_pending`. Preferred source: a NATS Prometheus exporter/surveyor scraped by Google Managed Prometheus (available on Autopilot), alerting on `consumer backlog high & not decreasing` per stream. *Fallback:* a lightweight poller that reads the `:8222/jsz` endpoint KEDA already uses and emits a structured metric/log-based metric. Exact pipeline finalized in implementation; the requirement only fixes the behavior.

**D5 — Drop the `consumer_` prefix → bare per-subject names.** `consumerName(topic)` returns `strings.ReplaceAll(topic, ".", "_")`. Per-subject uniqueness (what actually fixed the original shared-group bug) is preserved; only the redundant app prefix is removed. Because the KEDA triggers already reference bare names, this needs **no KEDA change** — it fixes the drift for free. *Alternative rejected:* keep `consumer_*` and rename KEDA to match — leaves a meaningless prefix and still needs a KEDA edit; the user chose removal.

**D6 — Deploy strategy.** Set the consumer Deployment to `Recreate` (or `maxSurge=0, maxUnavailable=1`) so a rollout never runs two pods that fight over the single durable set.

## Risks / Trade-offs

- **Recreating a durable drops its pending messages (DeliverNew).** → Run the naming migration in low traffic; streams retain 7d, so critical pending can be re-published operationally (as done in the incident). Only today's events matter in practice.
- **Bare names collide with the existing stale orphans (`CONCERT_created`).** → That is exactly what reconciliation (D1) handles: the drifted orphan is deleted and recreated with correct config; the superseded `consumer_*` durables are cleaned as no-longer-desired.
- **Over-aggressive liveness → crashloop flapping.** → Require N consecutive failures + an initial grace period before reporting unhealthy.
- **Backlog alert false positives on low-traffic/slow subjects.** → Per-stream threshold + sustained no-decrease window; tune after observing baselines.
- **Phase-2 rollback re-introduces drift** (bare ↔ prefixed is itself a config change). → Reconciliation (D1) makes any direction safe; fail-loud + alert (Phase 1) remain regardless, so a bad rollback is caught, not silent.

## Migration Plan

1. **Phase 1 (safety first, low risk):** ship fail-loud (D2), liveness-reflects-consumption (D3), the backlog alert (D4), and the `Recreate` strategy (D6). No naming change. After this, any wedge — including the current one recurring — is detected loudly (crashloop + backlog alert); self-healing a stale-durable conflict still requires Phase 2's reconciliation (D1).
2. **Phase 2 (naming + reconciliation):** ship startup reconciliation (D1) together with the bare-name change (D5). On rollout, reconciliation deletes drifted/stale durables and recreates correct bare-named ones; KEDA already matches. Verify all durables bound (`push_bound=true`), backlog draining, and the alert green.
3. **Cleanup:** remove any remaining orphan durables from the incident; document the reconciliation path as the required procedure for any future durable name/config change.

**Rollback:** revert the backend image pin; reconciliation on the prior image re-converges durables. Phase 1 controls are independent and safe to keep even if Phase 2 is reverted.

## Open Questions

- Backlog metric pipeline: NATS Prometheus exporter + Google Managed Prometheus vs. a `jsz` poller emitting a log-based metric — decide in implementation based on what is already deployed.
- Alert threshold and sustained-window per stream (need baseline observation).
- Whether reconciliation should also proactively delete all no-longer-desired durables, or only fix the drifted desired ones and leave harmless orphans to age out.
