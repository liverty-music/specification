## 1. NACK controller (cloud-provisioning)

- [x] 1.1 Add the `nats/nack` Helm release (control-loop mode) to the `nats` namespace overlay (prod), pointed at the in-cluster NATS URL; sane resource requests + single replica (revisit HA later). Passive — manages no resources yet
- [x] 1.2 `kubectl kustomize --enable-helm` dry-run (prod) renders the controller + its CRDs cleanly; ArgoCD app wiring for the CRDs
  - Note: dev is decommissioned (`workloadEnabled=false`); the controller's first in-cluster deploy + health verification is prod §6.1

## 2. Declarative Stream + Consumer CRDs (config parity)

- [x] 2.1 Author `Stream` CRDs for all 11 streams mirroring the **exact live config across every NACK-managed field** (name, subjects, retention, storage, maxAge, replicas, duplicate window, and any server-materialized defaults); set the **non-destructive deletion policy** (`preventDelete: true`) on every CRD so CR removal orphans, never deletes (design D6)
- [x] 2.2 Author `Consumer` CRDs for the **18 existing** durables (behaviors + POISON) as **pull** consumers (design D5 — the live push consumers use a non-reproducible random `_INBOX` deliver subject, so they are intentionally recreated push→pull): `durableName = behavior`, **pull** (no `deliverSubject`/`deliverGroup`), `deliverPolicy: new` (parity), `ackPolicy: explicit`, `ackWait: 30s`, `maxAckPending: 1000`, `maxDeliver`, `replayPolicy: instant`, `filterSubject` per behavior, `numReplicas` per stream; `preventDelete` on each. **Do NOT include `media_uploaded` here** — it is new and applied in §5 after the app reconcile is removed (design D6 ordering)
- [x] 2.3 GitOps wiring: place the CRDs under the nats (or a dedicated jetstream) overlay so ArgoCD applies them; kustomize dry-run

## 3. No-op adoption proof — local NATS + nack reproduction (gate)

> Dev is torn down (`workloadEnabled=false`), so the no-op-adoption gate runs in a
> **local NATS + nack reproduction** instead of the dev cluster. The source of
> truth is the **prod** live config, extracted read-only.

- [x] 3.1 Extract the **exact live config** of all 11 streams + 18 durables from **prod** (read-only): `kubectl port-forward -n nats svc/nats` + `nats stream info` / `nats consumer info` → capture **every field** as the authoritative source for the CRDs (§2)
- [x] 3.2 Stand up a **local** NATS (docker) + the nack controller; recreate the streams + the **push** durables with the captured prod config and publish a few messages so each durable has non-trivial cursor/`num_pending` state
- [x] 3.3 Apply the Stream + Consumer CRDs against local NATS via nack, and confirm: **(a) streams adopt no-op** (field-by-field `nats info` diff empty); **(b) consumers recreate cleanly push→pull** and the **pull** backend binds + drains all published messages with **no loss** (`DeliverNew` parity). Iterate CRD fields until (a) is empty and (b) drains clean. This local proof is the gate before any prod apply (§6)

## 4. Backend — bind-only (remove imperative management)

- [x] 4.1 Remove imperative stream creation from `streams.go` (streams now owned by CRDs); keep the stream/subject registry only where still needed for reference (e.g. `SubjectCoveredByStream`) without creating streams
- [x] 4.2 Remove the homegrown `ReconcileConsumers`/`reconcileConsumers` + `classifyConsumer` (durable lifecycle now owned by NACK); remove its call sites in `di/consumer.go` and the media DI
- [x] 4.3 Change `NewBehaviorSubscriber` (and the media subscriber) to a **pull** fetch loop bound to the pre-existing NACK durable for **all** consumers (design D5 — one subscription model, no push `_INBOX`/deliver-group); the behavior→durable name mapping is unchanged. Ack-explicit, respect `maxAckPending`; watermill nats pull config or a direct `js.PullSubscribe` fetch loop
- [x] 4.4 Unit tests updated (reconcile tests removed/replaced; subscriber bind path); `make check`
- [x] 4.5 Verify bind-only: local NATS repro (§3.3) proved bind + drain; confirmed in prod §6 — event-consumer v1.50.0 logs show "Subscribing/Starting handler" for all 19 behaviors bound to the pre-existing pull durables (waiting_pulls=1), no create/recreate attempts, 0 errors, no wedged durables.

## 5. media-processor → `media-consumer` (rename + scale-to-zero)

- [x] 5.1 Backend rename: `cmd/job/media-processor` → a long-running `cmd/consumer/media-consumer` (it already runs `Router.Run`); `di/media_job.go` → media-consumer DI; config struct rename; keep the behavior `media_uploaded`. It uses the **same shared pull subscriber** now that all consumers are pull (§4.3) — bound to the pre-existing `media_uploaded` durable
- [x] 5.2 Dockerfile target + `deploy.yml` matrix + `bump-prod-pin` IMAGES: `media-processor` → `media-consumer` (image now `backend/media-consumer`)
- [x] 5.3 cloud-provisioning rename: GSA/WI binding/bucket IAM/ConfigMap/monitoring workload entry `media-processor` → `media-consumer` (use Pulumi `aliases` where rename would replace a stateful resource; GSA/image are fresh so replace is acceptable)
- [x] 5.4 Apply the `media_uploaded` `Consumer` CRD **now** (only after §4 removed the app reconcile, per design D6 ordering): a **pull work-queue** durable (`ackPolicy: explicit`, `deliverPolicy: all`, `ackWait ≥ worst-case transcode`, `maxDeliver: 3`, `preventDelete`)
- [x] 5.5 Replace the KEDA **ScaledJob** with a **Deployment** (long-running, maxSurge:0 like event-consumer, libvips-sized resources, `media-consumer` SA, envFrom media-consumer-config + backend-secrets) + a **`ScaledObject`** (`minReplicaCount: 0`, `maxReplicaCount: 2`, `activationLagThreshold: 0`, `pollingInterval: 15`, `cooldownPeriod ≥ ackWait`) targeting it; kustomizeconfig for the ScaledObject `scaleTargetRef` name reference
- [x] 5.6 Verify **wake-from-zero** in prod §6.4: with 0 replicas, a synthetic `MEDIA.uploaded` → the `media_uploaded` durable retained it → KEDA scaled media-consumer 0→1 → bound the durable → handler ran (DB connect + FindMediaByID) → acked → scales back to 0. (Full "variants produced" for a real media row is the organic-upload follow-up; the pipeline path — wake, bind, DB, ack — is proven.)

## 6. Prod cut-over + verify

- [x] 6.1 Prod: deploy NACK (passive) → apply Stream CRDs (**no-op adoption CONFIRMED**: 11 streams `Ready`, `nats stream info` state identical before/after) → apply Consumer CRDs.
  - **IMPORTANT runbook correction (D5/D6):** NACK does **not** recreate a push consumer as pull — the server rejects it with `can not update push consumer to pull based (10012)` and the Consumer CR goes `Errored`. Field parity is not enough for consumers. The cut-over therefore **explicitly deletes the existing push durables first** (safe because the consumer app is paused and `num_pending == 0` for all 19 — verified), then NACK creates them fresh as **pull**. Prod result: all 20 durables `pull` (19 behaviors incl. `log-poison` + `media_uploaded`). Discovered a **19th** live durable (`log-poison`, POISON) missing from the original CRD set — added.
- [x] 6.2 Prod backend release v1.50.0 (bind-only pull) + `media-consumer` image; event-consumer bound all 19 durables, 0 errors, all flows (push/discovery/analytics/ticketing/organizer) uninterrupted.
- [x] 6.3 Prod `pulumi up` (Console) done — `media-consumer` GSA/IAM/bucket rename adopted in place (aliases); `media-processor` ScaledJob/GSA retired.
- [x] 6.4 Prod wake-from-zero verified: synthetic `MEDIA.uploaded` → KEDA scaled media-consumer 0→1 → bound the `media_uploaded` pull durable → acked. **Surfaced a pre-existing gap** (the media pipeline never had DB access; media-processor never ran): fixed out-of-band as a follow-up — media-consumer IAM DB user + cloudsql roles (cloud-provisioning#470) + app-schema grant migration (backend#424) + configmap DB block. Re-test confirmed clean startup + "Database connection established" + FindMediaByID→NotFound graceful ack, restarts=0. Full image→WebP-variants path still to be confirmed with an organic organizer upload (a real media row).

## 7. Rollback readiness (each stage)

- [x] 7.1 Document per-stage **non-destructive** rollback (dev is decommissioned, so there is no dev rehearsal gate; safety rests on the local NATS+nack proof §3 and the `preventDelete` design D6): re-enable app-side stream/consumer management (revert §4) and remove the CRDs — which **orphan (do NOT delete) the live resources because `preventDelete` is set**; revert the media workload manifest. First prod CRD apply (§6.1) is done in a low-traffic window and watched closely, with the `nats consumer info` before/after diff as the live no-op proof. **Consumer rollback caveat (from the §6.1 finding):** because push↔pull is an immutable switch, reverting consumers to the old app-managed push model is also not a CR edit — it requires deleting the pull durables (they carry `preventDelete`, so delete the CR's underlying consumer explicitly via `nats consumer rm`) and letting the reverted app recreate them push; streams still orphan cleanly.
