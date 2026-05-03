## ADDED Requirements

### Requirement: Alert on Zitadel API request latency p99

The system SHALL provision a Cloud Monitoring `AlertPolicy` that fires when the p99 of Zitadel API request duration for `OIDCService/*` gRPC methods exceeds 10 seconds over a 60-second evaluation window. The alert SHALL route to the existing `pannpers@gmail.com` notification channel reused from the `app-error-log-alerting` capability.

The latency signal SHALL be sourced from Zitadel v4's native OpenTelemetry SDK (push-based OTLP to the cluster OTLP collector), NOT from GKE Gateway access logs (Gateway logs aggregate by HTTPRoute path and dilute the per-gRPC-method signal) and NOT from a Prometheus `/debug/metrics` scrape (Zitadel v4 has no such endpoint — verified empirically). The collector SHALL have a `metrics` pipeline that exports to Cloud Monitoring via the `googlecloud` exporter, and Zitadel SHALL be configured with `OTEL_EXPORTER_OTLP_ENDPOINT` and `OTEL_METRICS_EXPORTER=otlp` env vars to enable the push.

**Rationale**: The §18.6 incident shape was a 30+ second hang on `GetAuthRequest`. Healthy Zitadel `OIDCService/*` p99 is < 200 ms, so a 10-second threshold is 50× the steady-state high-water mark — clearly anomalous. The 60-second window catches a single hung call as well as a sustained degradation. False positives are tolerable in dev.

#### Scenario: Healthy Zitadel emits no alert

- **WHEN** Zitadel API responds to `OIDCService/*` calls within steady-state latency (p99 ≤ 200 ms) for any 60-second window
- **THEN** the alert policy SHALL evaluate as `OK`
- **AND** no notification SHALL be sent

#### Scenario: Sustained hang triggers an alert

- **WHEN** Zitadel API `OIDCService/*` p99 exceeds 10 seconds for at least one 60-second evaluation window
- **THEN** the alert policy SHALL transition to `OPEN`
- **AND** a notification SHALL be sent to the `pannpers@gmail.com` channel within 5 minutes (Cloud Monitoring per-channel debounce)

#### Scenario: Alert auto-resolves after pod restart

- **WHEN** an operator runs `kubectl rollout restart deploy/zitadel` in response to the alert
- **AND** the new pod's `OIDCService/*` p99 returns to < 1 second within a 60-second window
- **THEN** the alert policy SHALL transition to `CLOSED` automatically
- **AND** an auto-close notification SHALL be sent

#### Scenario: Cold-start latency does not false-fire

- **WHEN** the Zitadel API pod is restarted (planned deploy or band-aid CronJob)
- **AND** the cold-start window (~10 seconds for Ready) shows transient elevated latency
- **THEN** the 60-second evaluation window SHALL absorb the cold-start blip
- **AND** no notification SHALL be sent unless degraded latency persists past pod-Ready

### Requirement: Alert on backend JWT validation error rate

The system SHALL provision a Cloud Monitoring `AlertPolicy` that fires when the rate of backend JWT validation ERROR-level log entries exceeds 10 events per minute, evaluated over a 5-minute window. The alert SHALL route to the same notification channel as the latency alert.

The signal SHALL be a Cloud Logging log-based metric `backend_jwt_validation_zitadel_errors` scoped to the `backend/server` workload's `severity=ERROR` entries whose `jsonPayload.msg` OR `jsonPayload.error` field matches the case-insensitive regex `jwt|jwks|token|authn|invalid token|failed to validate`. No new application code is required; the alert reads existing structured `slog` ERROR entries that the backend's `JWTValidator` already emits.

The filter is intentionally broad-then-tight: scoped tightly by namespace + workload + severity (the only place that validates Zitadel-issued JWTs), then keyword-filtered. False positives are tolerable in dev — the 10/min threshold is well above steady-state JWT validation noise.

**Rationale**: A Zitadel hang or JWKS unreachability surfaces in backend as a burst of JWT validation failures. `app-error-log-alerting` covers backend errors generically (high log volume), but does not extract the Zitadel-specific signal — without that, a JWT-validation cascade would be dampened by other backend ERROR traffic. This requirement adds the auth-specific signal extraction.

#### Scenario: Steady-state JWT validation errors do not trigger

- **WHEN** the backend's JWT validation error rate stays below 10 events / minute (e.g., occasional expired tokens from cached frontend sessions)
- **THEN** the alert policy SHALL evaluate as `OK`

#### Scenario: Burst of JWT failures triggers within 5 minutes

- **WHEN** the backend's JWT validation Zitadel-related error rate exceeds 10 events / minute for a 5-minute window
- **THEN** the alert policy SHALL transition to `OPEN`
- **AND** a notification SHALL be sent within 5 minutes of crossing the threshold

#### Scenario: Auto-close after Zitadel recovery

- **WHEN** the JWT validation error rate returns to baseline (< 1 event / minute) for 5 minutes
- **THEN** the alert policy SHALL transition to `CLOSED`

### Requirement: Cloud SQL connection-pool dashboard panel for Zitadel database

The system SHALL provision a Cloud Monitoring dashboard panel showing the Cloud SQL connection-pool utilization (`cloudsql.googleapis.com/database/postgresql/num_backends`) for the `zitadel` database on the `postgres-osaka` instance. The panel SHALL be added to the existing dev observability dashboard (or a new dashboard if none exists for the dev project).

The panel SHALL include a horizontal threshold line at 80% of the configured `max_connections` (rendered in YELLOW, not RED, since the panel is observation-only and does not page) to make connection pressure visually obvious. The threshold value SHALL be derived from the dev `postgres-osaka` instance's GCP-default `max_connections` for its tier (currently `db-f1-micro` → default 25 → threshold 20). If the tier is changed, the threshold value must be re-derived because GCP's default `max_connections` scales with tier memory.

**Rationale**: §18.6 hypothesis B is connection-pool exhaustion from leaked connections in async notification-worker retries. The dashboard panel is **observation-only** (not alerting) because connection-pool saturation precedes the hang by an unknown lead time; we do not yet have data to set a meaningful alert threshold. The panel exists so the next responder (or a curious engineer) can correlate a hang event with connection-pool history. Once a hang reproduces and we have data, an alert threshold can be derived and added in a follow-up change.

#### Scenario: Healthy connection pool

- **WHEN** the `zitadel` database on `postgres-osaka` shows `num_backends` < 80% of `max_connections`
- **THEN** the dashboard panel SHALL render the metric in the green region of the chart

#### Scenario: Connection-pool saturation visible

- **WHEN** `num_backends` rises above 80% of `max_connections`
- **THEN** the dashboard panel SHALL render the metric crossing the threshold line
- **AND** the chart SHALL retain at least 7 days of history so post-incident correlation is possible

### Requirement: Weekly Zitadel API restart CronJob in dev

The system SHALL provision a Kubernetes `CronJob` in the `zitadel` namespace, dev overlay only, that runs `kubectl rollout restart deploy/zitadel` weekly (e.g., Sunday 03:00 UTC, low-traffic window). The CronJob SHALL carry a `liverty-music.app/temporary` annotation referencing the `self-hosted-zitadel` §18.6 root-cause investigation, so it can be programmatically discovered and removed once the root cause is fixed.

The CronJob SHALL be defined in `k8s/namespaces/zitadel/overlays/dev/cronjob-restart-zitadel.yaml`. It MUST NOT be added to `k8s/namespaces/zitadel/base/`, so that staging / prod overlays do not silently inherit the band-aid.

The CronJob's ServiceAccount SHALL be granted minimum-privilege RBAC to perform `kubectl rollout restart` on the `zitadel` Deployment only — not on any other Deployment in the namespace.

**Rationale**: The §18.6 hang takes ~3.5 days of pod uptime + a high-density burst of state-changing API calls to manifest. A weekly forced restart caps the upper-bound on incident frequency to ≤ 7 days. This is **explicitly a band-aid** that should be removed once a root cause is found.

#### Scenario: Weekly restart fires successfully

- **WHEN** the CronJob's scheduled time arrives (Sunday 03:00 UTC)
- **THEN** Kubernetes SHALL create a Job that runs `kubectl rollout restart deploy/zitadel`
- **AND** the deploy SHALL roll out a new pod within the configured `RollingUpdate` strategy (`maxUnavailable: 0`, `maxSurge: 1`)
- **AND** the Zitadel API SHALL remain reachable through at least one Ready pod throughout the rollout

#### Scenario: CronJob is dev-only

- **WHEN** the staging or prod overlay of `k8s/namespaces/zitadel/` is rendered via `kustomize build`
- **THEN** the rendered manifest SHALL NOT contain the `cronjob-restart-zitadel` resource
- **AND** the dev overlay rendering SHALL contain it

#### Scenario: Annotation enables programmatic cleanup

- **WHEN** an engineer searches the cluster for temporary band-aid resources via `kubectl get cronjob -A -o yaml | grep liverty-music.app/temporary`
- **THEN** the `cronjob-restart-zitadel` SHALL appear in the results with an annotation value referencing `self-hosted-zitadel §18.6`

### Requirement: Operator runbook for the Zitadel hang incident shape

The system SHALL maintain an operator runbook at `cloud-provisioning/docs/runbooks/zitadel-hang.md` that captures the §18.6 incident response procedure. The runbook SHALL be authored from this spec's content as the source of truth and exported to the docs path for ops convenience.

The runbook SHALL include:

- **Symptom recognition**: how to confirm the incident matches §18.6 (e.g., `OIDCService/*` p99 alert + 30s+ timeouts + `code: internal`).
- **Forensic data capture before mitigation**: list of metrics / logs / API responses to capture **before** restarting, so the next root-cause investigation has data (Zitadel `/debug/metrics` snapshot, Cloud SQL connection-pool metric snapshot, last 30 minutes of Zitadel access log filtered to state-changing API calls, output of `kubectl describe pod` for the affected pod).
- **Mitigation command**: the exact `kubectl rollout restart deploy/zitadel` invocation, including the `kubeconfig` context selection.
- **Post-mitigation verification**: confirm `/debug/healthz` returns 200, confirm a sample `OIDCService/*` call succeeds with normal latency (< 1s).
- **Escalation path**: when to involve upstream Zitadel maintainers (e.g., if the same shape recurs within 24 hours of restart).

#### Scenario: First responder follows the runbook successfully

- **WHEN** an operator receives the §18.6 latency alert for the first time
- **AND** the operator opens `cloud-provisioning/docs/runbooks/zitadel-hang.md`
- **THEN** the runbook SHALL provide enough detail that the operator captures forensic data and runs the mitigation command without needing to re-derive the response from scratch

#### Scenario: Forensic data is captured before restart

- **WHEN** the operator follows the runbook's "Forensic data capture before mitigation" section
- **THEN** the runbook SHALL list each artifact (metric snapshot, log range, API response) explicitly with the command or URL to obtain it
- **AND** the runbook SHALL specify a target storage location for the captured artifacts (e.g., `/tmp/zitadel-hang-<timestamp>/`) so the data is not lost when the operator's terminal session closes

#### Scenario: Runbook stays in sync with the spec

- **WHEN** the spec content for the runbook (this requirement's bullets) is modified in `openspec/specs/zitadel-observability/spec.md`
- **THEN** the markdown export at `cloud-provisioning/docs/runbooks/zitadel-hang.md` SHALL be regenerated in the same PR
- **AND** a reviewer SHALL be able to spot the divergence by comparing the two files
