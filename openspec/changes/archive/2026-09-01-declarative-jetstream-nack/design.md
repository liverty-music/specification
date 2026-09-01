## Context

See proposal.md — Why. Today streams are created in code (`streams.go`) and
durables are managed by an app-side `reconcileConsumers` that walks **all**
streams and deletes any consumer not in the calling app's `desired` set
(`classifyConsumer` → `reasonNotDesired`). Durables are **push** consumers with
`deliverGroup = behaviorName`, `DeliverPolicy = New`, `ackPolicy = explicit`,
`ackWait = 30s`, created lazily by `NewBehaviorSubscriber` on worker startup.
KEDA (`nats-jetstream` scaler) reads a durable's `num_pending`. NATS runs via the
official Helm chart; there is **no** declarative JetStream controller yet.

## Goals / Non-Goals

**Goals:** a single declarative owner of streams/consumers (workload-independent
lifecycle); remove the cross-consumer mutual-deletion hazard; enable a hack-free
scale-to-zero media consumer; a **zero-downtime, reversible** migration proven in
dev before prod.

**Non-Goals (design-level):** migrating KeyValue/ObjectStore to CRDs; changing
event subjects, payloads, or the behavior→durable mapping; changing the media
upload/attach RPCs (shipped in `organizer-media-pipeline`); NACK controller HA
tuning beyond a sane default.

## Decisions

**D1 — Declarative management via NACK (control-loop), exclusive owner. [★]**
Adopt the official NATS controller (`nats/nack` Helm, `--control-loop`) as the
**sole** manager of `jetstream.nats.io/v1beta2` `Stream`/`Consumer` resources.
NACK enforces declared state and forbids external mutation. *Alternatives:*
(a) keep imperative management + minimal fixes — scope `reconcileConsumers`
per-stream and have an always-on service pre-create `media_uploaded`; rejected —
the per-stream scoping is a clean fix but the durable pre-creation is a layering
hack (a publisher provisioning another workload's consumer), and it leaves the
homegrown reconcile as a bespoke reimplementation of what an operator does.
(b) always-on `min=1` media consumer (no scale-to-zero) — clean but pays the
Autopilot floor 24/7 for a rarely-used workload. NACK is the k8s/GitOps + NATS
best practice and generalizes to future consumers.

**D2 — Full migration, not partial (exclusivity forces it). [★]**
Because NACK-managed resources must be **exclusively** NACK-managed, we cannot
half-adopt. Declare **all** streams (11) and consumers (~19) as CRDs and remove
app-side management for all of them in the same change. Mixing app-created and
CRD-managed resources on the same stream causes enforcement conflicts.

**D3 — Backend becomes bind-only. [★]**
Remove `streams.go` stream creation and `reconcileConsumers`; change
`NewBehaviorSubscriber` to **bind** to the pre-existing NACK durable (do not
create/recreate). The behavior→durable name mapping and KEDA trigger names are
unchanged, so this is transparent to consumers.

**D4 — media-processor → `media-consumer`: ScaledObject + Deployment, min=0. [★]**
Rename for consistency with `event-consumer` (the `-processor` name came from the
abandoned ScaledJob framing; `cmd/job/media-processor` is actually a long-running
`Router.Run` — a consumer, not a batch job). Convert to a **Deployment** driven
by a KEDA **`ScaledObject`** with `minReplicaCount: 0`, `maxReplicaCount: 2`,
`activationLagThreshold: 0`, `pollingInterval: 15`, `cooldownPeriod ≥ ackWait`.
Its `media_uploaded` durable is a declarative `Consumer` CRD, so it persists at
zero replicas and KEDA can wake it. Idle ≈ $0.

**D5 — ALL consumers become **pull, durable, work-queue** consumers. [★]**
The existing durables are **push** consumers whose `deliver_subject` is a
**server-generated random `_INBOX.*`** (watermill/nats.go picks a fresh ephemeral
inbox per subscription — confirmed in prod, e.g. `ingest-concert`'s
`deliver_subject: _INBOX.qlPYpyK5E9…`). A declarative CRD **cannot reproduce a
random inbox**, so a NACK push consumer would never match the live one — adoption
could not be a no-op (it would force a durable recreate → the wedge). Rather than
special-case push, **convert every consumer to a pull durable** (`ackPolicy:
explicit`, `DeliverNew` to match current no-replay-on-restart semantics,
`ackWait: 30s`, `maxAckPending: 1000`): pull has **no `deliver_subject`**, so it
is fully declarative and matches exactly, it is uniform with the `media_uploaded`
consumer, and it is the idiomatic KEDA shape (KEDA reads `num_pending`; a
scale-to-zero pull consumer just lets messages wait to be fetched). *Backend
implication:* `NewBehaviorSubscriber` (and the media consumer) switch to a **pull
fetch loop** bound to the pre-existing NACK durable, for **all** consumers — one
subscription model, not two. `media_uploaded` uses `DeliverAll` (new work queue);
the adopted behaviors use `DeliverNew` (parity with today).

**D6 — Streams adopt as a no-op; consumers are a controlled one-time recreation
to pull; both dev-... (local-)proven, staged, reversible. [★]**
**Streams** ARE declaratively reproducible, so their CRDs MUST mirror the live
config across **every managed field** (subjects, retention, storage, maxAge,
replicas, `duplicate_window`, `discard`, …) and adopt as a **no-op** (no
recreate). **Consumers** cannot be adopted no-op (D5: random `_INBOX` deliver
subject), so migrating them is a **deliberate, one-time recreation** from push to
**pull** — an *intended* change, not accidental drift. The pull `Consumer` CRDs
still mirror the intended config across every managed field (`ackPolicy`,
`deliverPolicy`, `ackWait`, `maxAckPending`, `maxDeliver`, `replayPolicy`,
`filterSubject`, `numReplicas`, …) so the result is exactly what we declare.
Prove the whole thing in a **local NATS + nack reproduction first** (dev is torn
down): recreate the prod push consumers, apply the pull CRDs, confirm NACK
converts them cleanly, the backend pull-binds and drains, and **no message is
lost** (`DeliverNew` parity + doing it in a low-traffic window). Streams get a
field-by-field no-op diff; consumers get a clean recreate + drain check. The prod
apply (§6) is gated on that local proof, done in a low-traffic window, watched
closely.

**Ordering (avoid the "both managers fight"):** adopting the ~18 **existing**
durables is safe while the old backend still runs, because both keep the same
set at the same config (NACK no-ops, the app reconcile keeps its own). But the
**new** `media_uploaded` consumer must NOT be created while the old backend
reconcile is still live — event-consumer's global reconcile would delete it
(not in its desired set) and fight NACK. So: **NACK adopt existing (no-op) →
backend release removes app-side reconcile → only then apply the
`media_uploaded` CRD**. Each stage independently reversible.

**Non-destructive deletion policy (safe rollback) — critical.** By default NACK
**deletes the underlying stream/consumer when its CR is deleted**. A naive
rollback of "delete the CRDs" would therefore **destroy live prod streams and
durables**. All `Stream`/`Consumer` CRDs MUST set NACK's **non-destructive
deletion policy** (`preventDelete: true` / the control-loop equivalent) so that
removing a CR **orphans** the resource (leaves it intact on the server) rather
than deleting it. Rollback = remove the CRD (orphan) **and** re-enable app-side
management; it never deletes a live resource.

**D7 — Naming/identity churn for the media rename.**
`media-processor` → `media-consumer` across image repo, GSA, WI binding, K8s
objects, ConfigMap, monitoring, bump-prod-pin. Use Pulumi `aliases` where a
rename would otherwise replace a stateful resource; GSA/image are freshly created
(today) and not yet doing real work, so replace is acceptable. Do this rename
inside this change since the workload is being reworked anyway.

## Risks / Trade-offs

- **Stream adoption mismatch** (D6) → if a `Stream` CRD omits/differs on any
  managed field, NACK recreates the stream → a 2026-07-class wedge. Mitigation:
  full field parity + local-repro no-op proof.
- **Consumer recreation gap** (D5/D6) → consumers are intentionally recreated
  push→pull; between deleting the old push durable and the new pull durable
  binding, an event published in that window could be missed (`DeliverNew` skips
  pre-creation messages). Mitigation: do it in a **low-traffic window**, one
  controlled step, local-repro-proven; the affected events (discovery,
  notifications, analytics) tolerate a sub-second planned gap, and rollback
  re-establishes the push consumers.
- **Rollback deleting live resources** (D6) → NACK deletes the stream/consumer on
  CR deletion by default; a rollback that removes CRDs would destroy prod
  streams. Mitigation: the non-destructive deletion policy (`preventDelete`) is
  mandatory on every CRD so CR removal orphans, never deletes.
- **Exclusive-management cut-over window** → after NACK adopts but before the app
  stops managing, both "manage" the resource; safe only because configs match
  (no-op). Ordered cut-over + short window.
- **NACK controller as a new dependency / SPOF for config** → if the controller
  is down, drift isn't corrected (existing durables keep working; only
  create/update stalls). Acceptable; run it like other cluster controllers.
- **KEDA #7657 (missing-consumer → scale-to-max)** → avoided because the durable
  is always present (declared), so the scaler never hits the missing-consumer
  path.
- **Scope touches every prod event flow** → staged, dev-first, reversible.

## Migration Plan

1. cloud-provisioning: deploy `nats/nack` (control-loop) **passive** (manages
   nothing yet); verify controller healthy.
2. Author `Stream` ×11 CRDs (field-parity, adopt **no-op**) + `Consumer` ×18
   **pull** CRDs (the existing behaviors, intentionally recreated push→pull;
   `DeliverNew`), all with `preventDelete`, from the **prod** live config
   (read-only). In a **local NATS + nack reproduction** (dev is down): prove the
   streams adopt no-op (field diff) and the consumers recreate cleanly to pull +
   the backend pull-binds + drains with no loss. **Do NOT add `media_uploaded`
   yet** (ordering, D6). *Legacy orphan streams* (ACCOUNT/ENTRY/SALES_REMINDER…,
   left from past subject renames) are **not** declared — NACK ignores
   undeclared resources, so they simply orphan (inert); the old app reconcile
   used to delete them, but that cleanup is dropped (harmless).
3. backend release: remove `streams.go` creation + `reconcileConsumers`;
   subscribers bind-only. Deploy to dev → verify all consumers still drain.
4. media rename + scale-to-zero (only after §3 removes the reconcile): apply the
   `media_uploaded` `Consumer` CRD (**pull work-queue**, `preventDelete`) +
   `media-consumer` Deployment + `ScaledObject` (min=0); retire the ScaledJob and
   the `media-processor` names. Verify wake-from-zero on a test event in dev.
5. Prod: repeat 1→4 as ArgoCD syncs + a prod backend release + prod `pulumi up`;
   verify every event flow (push, discovery, analytics, ticketing, organizer) and
   the media pipeline.
- Rollback (per stage, non-destructive): re-enable app-side stream/consumer
  management and **remove the CRDs — which orphan (do NOT delete) the live
  resources thanks to `preventDelete`**; revert the media workload to its prior
  manifest.

## Open Questions

- NACK controller replica count / leader election for the prod cluster — set from
  the chart defaults; revisit if config-apply latency matters.
- Whether to also declare the POISON stream's consumer via CRD or leave the
  poison consumer app-managed — default: declare it too (full exclusivity), unless
  dev adoption reveals a config it cannot express.
- Exact `media-consumer` `ackWait`/`cooldownPeriod` vs worst-case transcode time —
  tuned during implementation from observed libvips durations.
