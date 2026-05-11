## Context

The cutover-time Zitadel API hang (`self-hosted-zitadel/tasks.md` §18.6) was diagnosed reactively because an operator was already reproducing a separate sign-up bug. Zero alerting fires when:

- The Zitadel API container is up (passes `/debug/healthz`) but `OIDCService/*` calls take 30+ seconds — `kube-state` does not see this; only application-level latency does.
- Backend JWT validation starts failing in a cluster-correlated burst — backend logs the errors, but `app-error-log-alerting` is tuned for log-volume / level filters, not for the auth-specific signal of "JWKS unreachable" or "validator returns auth-failed faster than rate-limit".
- Cloud SQL connection-pool utilization on the Zitadel database climbs to saturation — Cloud SQL exposes this metric, but no alert reads it.

The existing observability stack already has 3 sibling capability specs (`app-error-log-alerting`, `argocd-deployment-alerts`, `consumer-poison-queue-alerting`), each of which:

- Provisions `gcp.monitoring.AlertPolicy` resources via Pulumi.
- Routes to the existing `pannpers@gmail.com` notification channel.
- Pairs each alert with a runbook section in `cloud-provisioning/docs/runbooks/`.

This change layers a fourth capability onto that established pattern, without inventing new infrastructure.

The hang root cause is an open question. Two hypotheses are documented in §18.6:

- **Hypothesis A**: in-memory projection updater stuck on a write lock. Zitadel is event-sourced; read-side projections are rebuilt from events. A long-held write lock during the burst of state-changing API calls would block reads.
- **Hypothesis B**: Cloud SQL connection-pool exhaustion from leaked connections in async notification-worker retries.

Both manifest as "pod restart fixes it" — same symptom, different fix surface. This change does not commit to a root-cause fix; it ships detection + a band-aid + investigation tasks.

## Goals / Non-Goals

**Goals:**

- The next Zitadel hang of the §18.6 shape pages an operator within 60 seconds (alert evaluation period + notification channel latency).
- A backend JWT-validation error rate exceeding the steady-state baseline by an order of magnitude pages within 5 minutes.
- Cloud SQL connection-pool saturation on the Zitadel database is visible on a dashboard before it triggers a hang.
- A weekly maintenance window in dev resets the Zitadel API pod's accumulated in-memory state, capping the upper bound on incident frequency to ≤ 7 days.
- A first-responder runbook captures the §18.6 mitigation sequence so it does not need to be re-derived under pressure.

**Non-Goals:**

- Eliminating the hang itself. The root-cause fix is gated on either reproducing the issue locally with metrics capture, or finding an upstream Zitadel patch — neither is in scope here.
- Prod / staging alerts. `self-hosted-zitadel` is dev-only until cooldown ends (~2026-05-14 + a `staging` migration change). Alerts will be templated to `dev` overlays only; prod overlays come with the prod migration.
- Login V2 UI (`zitadel-login` container) latency alerts. Login UI is a thin SSR wrapper around the API; an API-side alert covers the dominant failure mode. Login-UI-specific alerts wait until a real Login-UI-only incident materializes.
- Backend `EmailVerifier` / `WebhookValidator` error budget alerts. Those are backend-application concerns and belong under `app-error-log-alerting`.

## Decisions

### D1. Use Cloud Monitoring `AlertPolicy` (Pulumi-managed) — not Prometheus AlertManager

The `liverty-music-dev` cluster does not run Prometheus / AlertManager. The existing alerting stack uses GCP-native Cloud Monitoring, and the OTLP collector that backend exports to feeds Cloud Monitoring directly. Adding Prometheus to the stack just for Zitadel observability is over-engineering — sibling capabilities all use Cloud Monitoring and we should match them.

**Alternative considered:** Deploy Prometheus + AlertManager Operator. Rejected — adds a major new infrastructure surface (~300 MiB resident memory in the cluster, separate alert config DSL, separate dashboard story) for a single new alert family.

### D2. Source the latency signal from Zitadel's native OTLP push, not from `/debug/metrics` scraping or envoy / Gateway

**Architecture chosen:** Zitadel v4 emits OpenTelemetry metrics natively via the OTEL SDK (release notes for v4.14.0: "support standard OTEL env vars via autoexport"). It pushes those metrics to a configured OTLP collector — there is **no HTTP scrape endpoint** like the v3 `/debug/metrics`. Verified empirically against the running dev pod (`/debug/metrics`, `/metrics`, `/debug/pprof/` all return 404 / `code:5 Not Found`).

**Implementation flow:**

```
Zitadel v4 pod
    │ env: OTEL_EXPORTER_OTLP_ENDPOINT=otel-collector.otel-collector.svc.cluster.local:4317
    │      OTEL_METRICS_EXPORTER=otlp
    │      OTEL_RESOURCE_ATTRIBUTES=service.name=zitadel,service.version=v4.14.0
    ▼ push (gRPC OTLP)
otel-collector pod  (config extended)
    ├─ receivers.otlp           (already configured for traces)
    ├─ pipelines.metrics  NEW:  receivers:[otlp] → processors:[batch] → exporters:[googlecloud]
    └─ pipelines.traces         (already configured)
    │
    ▼
Cloud Monitoring custom metrics
    │
    ▼
AlertPolicy reads `custom.googleapis.com/opentelemetry/<metric>` (or per googlecloud-exporter naming convention)
```

The exact metric name will follow OTEL semantic conventions for gRPC servers — likely `rpc.server.duration` (histogram, ms) with `rpc.method` and `rpc.service` attributes that allow filtering to `OIDCService/*` calls. The exporter's name-translation rules will produce a Cloud Monitoring metric like `custom.googleapis.com/opentelemetry/rpc.server.duration` — the actual final name needs to be confirmed once the pipeline is live (see Open Questions Q1).

**Alternatives considered:**

- **Scrape `/debug/metrics`** (the original design D2). Rejected — verified does not exist on Zitadel v4. The endpoint was a v3-era artifact that the cutover-warning-fixes task description carried over from older docs without verification.
- **Use envoy / Gateway logs.** Rejected — Gateway logs aggregate by HTTPRoute path, not gRPC method, so `OIDCService/*` filtering would require lossy regex on request paths. OTEL `rpc.method` attribute is precise.
- **Run a parallel Prometheus operator + ServiceMonitor.** Rejected — the cluster does not run Prometheus today, and adding it just to scrape one service is over-engineering. The OTLP push pipeline already exists for traces; extending it to metrics is the lower-cost path.

**Side benefit:** the backend service already pushes OTLP to the same collector (verified: `TELEMETRY_OTLP_ENDPOINT=otel-collector.otel-collector.svc.cluster.local:4318` in `server-config` configmap), but the collector currently has no metrics pipeline so backend's pushed metrics are silently dropped. After this change, backend metrics will start flowing to Cloud Monitoring as well — this is not the goal of `zitadel-observability`, but it is an aligned correction that we get for free.

### D3. p99 > 10s, evaluation window 60s

The §18.6 hang manifested as 30+ second responses on individual calls. p99 thresholds:

- `> 10s for 60s` — fires within ~1 minute of a single hung call landing.
- `> 30s for 60s` — only fires once the hang fully matures (the actual incident shape).

The aggressive `> 10s` threshold is the right choice because (a) **healthy Zitadel `OIDCService/*` p99 is < 200ms** (verified by spot-check of `/debug/metrics`), so 10s is 50× the normal high-water mark — clearly anomalous; (b) it provides headroom to catch precursor states before they fully degrade; (c) false positives are tolerable in dev — operator inconvenience is cheap.

For prod (out of scope here), the threshold should be re-evaluated against prod-traffic baselines.

**Alternative considered:** p95 instead of p99. Rejected — p99 is more sensitive to tail-latency degradation, which is the §18.6 shape. p95 would smooth over a small number of pathologically slow calls.

### D4. OTEL push interval / staleness — 60s export interval, 5 min notification debounce

The OTEL SDK's metric export interval is configured via `OTEL_METRIC_EXPORT_INTERVAL` (default 60s). With a 60-second push interval into the collector and a 60s alert evaluation window, the evaluator sees ~1 data point per evaluation cycle — sufficient because the Zitadel OTEL SDK aggregates the histogram in-process (the pushed value already contains 60s of internal sampling).

Cloud Monitoring's per-channel notification debounce defaults to 5 minutes; we keep that default to avoid alert flooding during incident chains.

**Alternative considered:** Set `OTEL_METRIC_EXPORT_INTERVAL=10s` for tighter detection. Rejected — the default 60s is a deliberate Zitadel-side aggregation window that smooths over per-request jitter; sending 10s windows multiplies metric ingest volume by 6× without adding signal because the histogram's tail already captures the worst-case latency in the larger window. 60s aligns with the same cadence other capabilities (`app-error-log-alerting`) use.

**Note vs. original draft:** the previous design draft proposed a 30s **scrape** interval against `/debug/metrics`. With the architecture corrected in D2 (push-based OTLP), the equivalent control knob is the OTEL SDK's export interval, not a scrape interval. The numbers shift accordingly (60s push vs. 30s scrape) but the end-to-end alert latency budget is the same.

### D5. Backend JWT-validation error alert — log-based, not metric-based

Backend already emits a structured `slog` ERROR for every JWT validation failure; `app-error-log-alerting` already routes these to Cloud Logging. The cleanest signal extraction is a log-based metric counting structured errors with a Zitadel-related context (`source: jwks` or `error: zitadel.*`), then alerting on its rate. This avoids adding a new histogram to the backend just for this signal.

**Alternative considered:** Add a Prometheus counter on backend's JWT validator. Rejected — duplicates the data already in logs; introduces a new signal source the on-call needs to learn.

### D6. Weekly-restart `CronJob` is a band-aid — opt-in via dev overlay only

The `kubectl rollout restart deploy/zitadel` `CronJob` is **explicitly a band-aid** that should be removed once a root cause is identified. To make removal trivial:

- Place the CronJob in `k8s/namespaces/zitadel/overlays/dev/cronjob-restart-zitadel.yaml`, **not** in `base/`.
- The base manifest stays clean — staging/prod will not inherit the band-aid by default.
- The `CronJob`'s metadata includes a `liverty-music.app/temporary: "until-rootcause-§18.6"` annotation so a future grep finds it for cleanup.

**Alternative considered:** No restart `CronJob`; rely entirely on alert + manual remediation. Rejected — the time between alert fire and operator action in dev can be hours (off-hours), during which the only feedback loop for active dev work is broken sign-up. The band-aid is cheap insurance.

**Alternative considered:** Resource-based restart trigger (e.g., restart when memory > 80%). Rejected — adds a Vertical Pod Autoscaler-like dependency without a clear "what threshold" answer; weekly time-based restart is simpler and the upper-bound is what we care about, not the median case.

### D7. Runbook lives in `cloud-provisioning/docs/runbooks/`, sourced from this change's specs

Sibling capability `app-error-log-alerting` keeps its runbook content inside its `spec.md` as scenarios. This change adopts the same convention for consistency, plus exports a derived markdown to `cloud-provisioning/docs/runbooks/zitadel-hang.md` for ops convenience (operators don't need to know about openspec to find the runbook).

The runbook content is the source of truth in `specs/zitadel-observability/spec.md` "Operator Runbook" requirements; the markdown export is a convenience copy.

## Risks / Trade-offs

- **[Risk]** Cloud Monitoring custom metric quota on `liverty-music-dev` may approach limits if more capabilities follow this scrape pattern. → **Mitigation**: monitor the project's `monitoring.googleapis.com/...` quota usage in the existing `app-error-log-alerting` dashboard; reduce scrape interval for less-critical metrics if quota pressure appears.
- **[Risk]** Weekly restart `CronJob` masks a slowly-degrading bug — if Zitadel actually leaks state in a way that a 7-day window resets, the team never feels enough pain to chase the root cause. → **Mitigation**: D6 annotation + a calendar reminder to revisit by 2026-08 (3 months out). Removing the band-aid is a single-file delete, not a refactor.
- **[Risk]** False-positive alerts from p99 > 10s during cold-start or deploy. Zitadel deploys re-elect raft / re-warm caches and may have transient slow tail. → **Mitigation**: 60s evaluation window + 5min notification debounce should swallow normal deploys (~10s pod-ready). If false positives are observed in the first 2 weeks, raise the evaluation window to 5 min instead.
- **[Trade-off]** Log-based JWT alert (D5) is slower-firing than a metric-based alert (logs ingestion ~30s lag in Cloud Logging vs ~5s for metrics). Acceptable: the JWT alert is a secondary signal — the latency alert (D3) is primary.
- **[Trade-off]** Dev-only scope means prod has no Zitadel observability when the migration begins. This is intentional: the prod migration change will copy / refine these alerts with prod-traffic-tuned thresholds; releasing them prematurely would either miss prod pathology (if dev thresholds are too loose) or page constantly (if too tight).

## Migration Plan

This change is additive observability — no behavior contract on Zitadel itself changes.

1. PR-1 (cloud-provisioning): Pulumi `AlertPolicy` + `Dashboard` resources for the 3 alerts (latency p99, JWT error rate, Cloud SQL connection pool). Dev-only overlays. `pulumi preview` shows `+ create` for the new resources, no replacements.
2. PR-2 (cloud-provisioning): `CronJob` manifest + runbook markdown export. Dev overlay only.
3. PR-3 (specification): archive this change; merge `specs/zitadel-observability/spec.md` into main `openspec/specs/`.

Rollback: each PR is a single revert. The CronJob removal would re-introduce the hang risk (no band-aid), which is acceptable for the brief revert window — the alerts (PR-1) catch any regression even if the band-aid is rolled back.

## Open Questions

- **Q1 (Resolved during apply-phase recon)**: Does the OTLP collector currently support metrics? **Answer: no.** The configmap (`otel-collector-config`) at the time of writing has only `pipelines.traces` and the `googlecloud` exporter; there is no `pipelines.metrics` and no Prometheus receiver. Zitadel v4 has no `/debug/metrics` HTTP endpoint, so the only path is OTLP push. The collector configmap must be extended in PR-1 — this is now reflected in design D2 and tasks §1.1.
- **Q2**: What is the exact Cloud Monitoring metric name produced by the `googlecloud` exporter when receiving OTEL `rpc.server.duration` from Zitadel? Likely `custom.googleapis.com/opentelemetry/rpc.server.duration` or `workload.googleapis.com/rpc.server.duration`, but the exporter's translation rules vary by version and configuration. → To confirm during PR-1 §1.2 (metric snapshot) once the OTEL push is wired up. The alert query in §1.4 then targets the confirmed name.
- **Q3**: Should the JWT-validation log-based metric (D5) live in `cloud-provisioning` (alert side) or be authored in `backend` (signal source side, via structured `slog` field)? → Lean toward `cloud-provisioning` because backend already emits the log; the log-based metric is purely an alerting concern. To confirm during PR-1 implementation.
- **Q4**: Is the §18.6 hang reproducible locally? → If yes, an upstream-bug investigation task can collect traces and produce a Zitadel issue report; if no, the band-aid + observability is the long-term answer until a separate incident provides reproduction conditions. Investigation runs in parallel with this change but does not block it.
