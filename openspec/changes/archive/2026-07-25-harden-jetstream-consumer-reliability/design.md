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

**D5 — Name consumers by *behavior*, not by subject.** (Supersedes the earlier "bare per-subject name" idea.) A JetStream **subject** answers *"what happened"* (the event, producer vocabulary, past tense); a **consumer/durable** answers *"what we do about it"* (the reaction, consumer vocabulary). So the durable name **and** its deliver group are the **behavior name** — i.e. the watermill handler name — not the subject. Naming grammar: `<verb>-<object>` kebab-case, drawn from a controlled 6-verb vocabulary — `ingest` (pull external data into our domain), `resolve` (enrich an entity via external lookup), `verify` (send a verification), `notify` (push to users), `track` (forward to analytics), `log` (dead-letter). Analytics forwarders collapse the verbose `forward-…-to-analytics` to `track-…`. The invariant that fixes the incident: **deliver group is unique per consumer** (`deliver group == durable == behavior`); no two consumers share a group. *Alternative rejected (old D5):* per-subject names — still names the consumer after the *event*, and collides when two behaviors react to one subject (breaks fan-out; see D7).

**D6 — Deploy strategy.** Set the consumer Deployment to `Recreate` (or `maxSurge=0, maxUnavailable=1`) so a rollout never runs two pods that fight over the single durable set. *(Shipped in Phase 1 as `maxSurge=0, maxUnavailable=1`.)*

**D7 — One consumer per *handler* (behavior), sharing a single NATS connection.** Two handlers on the same subject (`ARTIST.created` → resolve-artist-name + resolve-artist-image; `USER.created` → verify-user-email + track-user-created) must **each** receive **every** message (fan-out). In NATS that means **one Consumer per handler** (the GCP Pub/Sub analogy: subject≈Topic, consumer≈Subscription, deliver group≈competing-consumers within one subscription). watermill's `DurableCalculator` is `func(prefix, topic)` and cannot key by handler, and one shared subscriber makes same-topic handlers collapse onto one competing consumer. So build **one watermill subscriber per handler** via `NewSubscriberWithNatsConn`, all sharing **one** `*nats.Conn`, each with a `DurableCalculator`/`SubjectCalculator` fixed to that handler's behavior name (durable = deliver group = behavior; filter = the subject). *Alternative rejected (method b — merge the multi-handler subjects into one composite handler):* it re-introduces the exact failure mode this change fixes — a partial failure (e.g. analytics send fails after email verification already sent) re-delivers the whole message and re-runs the succeeded behavior (double side-effect), forcing per-behavior idempotency and hand-rolling the "1 consumer = 1 ack" guarantee; it also loses per-behavior backlog observability and couples unrelated behaviors. Method a wins on fan-out correctness, failure isolation, per-behavior observability, decoupling, and naming fit; connection count is a tie (both 1 conn). Prod stays **1 pod** (KEDA `min=max=1`); all ~20 per-handler consumers run in that single pod.

**D8 — Consistent subject naming (past-tense events) + fold the dead `ACCOUNT` stream.** Subjects are `<DOMAIN>.<event_past_tense>`. Normalize the outliers: `SALES_PHASE.reminder.due` → `SALES_PHASE.reminder_due` (two tokens, so the stream filter can drop the `>` wildcard back to `.*`), and `ACCOUNT.login` → `USER.logged_in` — folding the **vestigial `ACCOUNT` stream** into `USER` (the `account.login` webhook was reverted 2026-07-02 and nothing currently publishes it, so the ACCOUNT stream and its lone subject are dead weight). Subjects are **backend-internal Go constants** (`internal/entity/event_data.go`), not proto — so this is a backend + cloud-provisioning(KEDA/stream) change plus a one-line update to `specification/docs/analytics/event-catalog.md`; **no proto/BSR release**. *Alternative considered:* keep `ACCOUNT` for a future auth-events redesign — rejected: it's currently dead and can be re-added when that work resumes.

**D9 — Reconcile rule = "delete any durable that is not a correctly-named, self-grouped, desired behavior".** The startup pre-flight (D1) deletes a durable when: its name is not in the desired behavior set (old `consumer_*` prefixed, old subject-named like `CONCERT_created`, or a no-longer-desired orphan), OR its `deliver_group != its own name` (the shared `"consumer"` group — the incident), OR its delivery policy drifted. watermill then re-creates the correct per-behavior durable. A durable whose name, self-group, and policy all match is left untouched.

## Risks / Trade-offs

- **Recreating a durable drops its pending messages (DeliverNew).** → Run the naming migration in low traffic; streams retain 7d, so critical pending can be re-published operationally (as done in the incident). Only today's events matter in practice.
- **Bare names collide with the existing stale orphans (`CONCERT_created`).** → That is exactly what reconciliation (D1) handles: the drifted orphan is deleted and recreated with correct config; the superseded `consumer_*` durables are cleaned as no-longer-desired.
- **Over-aggressive liveness → crashloop flapping.** → Require N consecutive failures + an initial grace period before reporting unhealthy.
- **Backlog alert false positives on low-traffic/slow subjects.** → Per-stream threshold + sustained no-decrease window; tune after observing baselines.
- **Phase-2 rollback re-introduces drift** (bare ↔ prefixed is itself a config change). → Reconciliation (D1) makes any direction safe; fail-loud + alert (Phase 1) remain regardless, so a bad rollback is caught, not silent.

## Migration Plan

1. **Phase 1 (safety first, low risk):** ship fail-loud (D2), liveness-reflects-consumption (D3), the backlog alert (D4), and the `Recreate` strategy (D6). No naming change. After this, any wedge — including the current one recurring — is detected loudly (crashloop + backlog alert); self-healing a stale-durable conflict still requires Phase 2's reconciliation (D1).
2. **Phase 2 (behavior naming + per-handler consumers + reconciliation):** ship startup reconciliation (D1, D9) together with the behavior-based, per-handler consumers (D5, D7), the subject normalization + `ACCOUNT`→`USER` fold (D8), and the matching KEDA trigger rename. On rollout, reconciliation deletes the stale shared-group/subject-named/prefixed durables and watermill re-creates the correct per-behavior ones. Verify every behavior has its own durable with `deliver_group == name` and `push_bound=true` (including the previously-missing `notify-concert`, `notify-sales-*`, and `track-*` fan-out consumers), backlog draining, and the alert green. **Note:** prod is currently in the broken pre-fix state (all durables share `deliver_group="consumer"`, ~10 subjects have no consumer) — this phase is the fix, so it doubles as incident remediation.
3. **Cleanup:** remove any remaining orphan durables (old `consumer_*`, old subject-named, the dead `ACCOUNT.login`); document the reconciliation path as the required procedure for any future durable name/config change.

**Rollback:** revert the backend image pin; reconciliation on the prior image re-converges durables. Phase 1 controls are independent and safe to keep even if Phase 2 is reverted.

## Open Questions

- Backlog metric pipeline: NATS Prometheus exporter + Google Managed Prometheus vs. a `jsz` poller emitting a log-based metric — decide in implementation based on what is already deployed.
- Alert threshold and sustained-window per stream (need baseline observation).
- Whether reconciliation should also proactively delete all no-longer-desired durables, or only fix the drifted desired ones and leave harmless orphans to age out.
