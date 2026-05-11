## Why

The cutover to self-hosted Zitadel landed on 2026-04-30 (`self-hosted-zitadel` change), but **the system has zero alerting on Zitadel itself**: when the Zitadel API container hung on `GetAuthRequest` for 30+ seconds during the cutover incident chain (3.5-day-old pod + ~30 minutes of high-density state-changing API calls within), it was discovered only because an operator was actively reproducing a separate sign-up bug. With dev as the proving ground for `prod` migration, every operational gap that would page someone at 3am in `prod` should be resolved here first — and "Zitadel hangs silently for 30+ seconds" is exactly that class of gap. The `self-hosted-zitadel` change deferred this as `§18.6` follow-up; this change picks it up.

## What Changes

- Add a Cloud Monitoring alert on Zitadel API request `duration_p99 > 10s` for `OIDCService/*` paths, paging the on-call channel when the next hang occurs (closes `self-hosted-zitadel` §18.6.2).
- Add a Cloud Monitoring alert on backend JWT validation error rate, so that a Zitadel-induced auth failure cascade reaches the operator before users do (existing `app-error-log-alerting` capability covers backend errors generically; this adds the auth-specific signal extraction).
- Add a Cloud Monitoring dashboard panel for Cloud SQL connection-pool utilization on the Zitadel database, addressing **hypothesis B** of the §18.6 hang root cause (connection-pool exhaustion from accumulated leaked connections in async notification-worker retries).
- Add a weekly `kubectl rollout restart deploy/zitadel` CronJob in the `dev` overlay only, as a band-aid against the hang until the root cause is identified (closes `self-hosted-zitadel` §18.6.3, dev half).
- Capture a runbook for the §18.6 incident shape — symptom recognition (`GetAuthRequest` 30s timeout + `code: internal`), immediate mitigation (`kubectl rollout restart deploy/zitadel`), forensic data to capture before restart (Zitadel API `/debug/metrics`, Cloud SQL connection metrics, recent state-changing API call log) — so the next responder does not need to re-derive the response (closes §18.6.1).
- Capture upstream-bug-investigation tasks (search Zitadel issue tracker for similar reports; if reproducible, file an issue with traces; revisit the weekly-restart band-aid once a root-cause fix lands or is documented).

## Capabilities

### New Capabilities

- `zitadel-observability`: Defines the alert thresholds, dashboard panels, and operator-facing runbook contracts for the self-hosted Zitadel API and Login UI containers running in the dev cluster. Covers both upstream-supplied metrics (Zitadel `/debug/metrics`) and infrastructure-supplied metrics (Cloud SQL connection pool, GKE pod health). Sibling to the existing `app-error-log-alerting` (backend), `argocd-deployment-alerts` (deploy), and `consumer-poison-queue-alerting` (consumer) capabilities — same alerting pattern, different subject system.

### Modified Capabilities

None. All work lands as additive new alerts/dashboards/runbooks under the new `zitadel-observability` capability. The existing `app-error-log-alerting` capability is sibling, not modified — its scope is "backend application error log signals", which does not include "Zitadel API latency".

## Impact

**Affected repositories**

- `cloud-provisioning/`:
  - `src/gcp/components/zitadel-monitoring.ts` (new) — Pulumi resources for `gcp.monitoring.AlertPolicy` (Zitadel latency p99, JWT validation error rate, Cloud SQL connection pool) and `gcp.monitoring.Dashboard` panels.
  - `k8s/namespaces/otel-collector/base/configmap.yaml` — extend the OTLP collector configuration with a `metrics` pipeline (currently `traces`-only) so Zitadel's pushed OTLP metrics are exported to Cloud Monitoring. Side effect: backend metrics, which currently push to the same collector but get silently dropped, also start flowing to Cloud Monitoring after this change.
  - `k8s/namespaces/zitadel/base/deployment-api.yaml` (or its associated configmap) — add `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_METRICS_EXPORTER=otlp`, and related OTEL env vars so Zitadel v4's native OpenTelemetry exporter pushes metrics to the collector. Zitadel v4 has no `/debug/metrics` HTTP endpoint — push-only is the supported path.
  - `k8s/namespaces/zitadel/overlays/dev/` — new `CronJob` manifest for the weekly `kubectl rollout restart deploy/zitadel`. Dev overlay only; base unchanged.
  - `docs/runbooks/zitadel-hang.md` (new) — incident runbook for the §18.6 hang shape, including the data-capture checklist before mitigation.
- `specification/`:
  - This change's `specs/zitadel-observability/spec.md` lands the alert thresholds, dashboard contract, and runbook obligations as the source-of-truth contract.

**Affected systems**

- Cloud Monitoring (GCP): new `AlertPolicy` resources + dashboard panels in `liverty-music-dev`.
- Notification channel routing: alerts go through the existing `pannpers@gmail.com` notification channel (re-used from `app-error-log-alerting`); no new channel created.
- `dev` GKE cluster: new weekly `CronJob` in the `zitadel` namespace; consumes negligible resources but does cause a brief (~30s) downtime window once a week. The `:9090` backend webhook port and the public Zitadel endpoint share that window — acceptable in dev per `self-hosted-zitadel` §18.6.3.

**Dependencies**

- None on external services or upstream version bumps.
- Reuses the existing Workload Identity / `gcp.monitoring` provisioning patterns from `app-error-log-alerting`.
- Compatible with the in-progress `pulumi-deploy-safeguards` change (no overlap; `pulumi-deploy-safeguards` covers Pulumi state import safety, this covers Zitadel runtime observability).

**Out of scope**

- Root-cause fix for the Zitadel hang itself. The §18.6 hypothesis A (in-memory projection updater write-lock) and hypothesis B (Cloud SQL connection pool exhaustion) require live reproduction and possibly an upstream Zitadel patch; this change documents the investigation as a task but does not commit to closing it. Once a root cause is confirmed, a follow-up change retires the weekly-restart band-aid.
- Prod-environment alerts. This change targets `dev` only, mirroring `self-hosted-zitadel`'s dev-only scope. Prod alerts will be added when self-hosted Zitadel extends to staging / prod (currently gated on `self-hosted-zitadel` archive + cooldown).
- Login V2 UI (`zitadel-login` container) observability. The Login UI is a thin Next.js wrapper; latency alerting on it is deferred until the API-side alerts have been validated and a real Login-UI-specific incident materializes.
- Backend `EmailVerifier` / `WebhookValidator` alerts. Those are backend-application concerns and belong under `app-error-log-alerting`'s scope.
