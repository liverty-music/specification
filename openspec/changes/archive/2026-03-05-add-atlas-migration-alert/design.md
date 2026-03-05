## Context

Cloud Monitoring currently has log-based alert policies for backend workloads (server, consumer, concert-discovery) that filter on `severity="ERROR"` in the `backend` namespace. Atlas Operator logs migration events as Kubernetes events with `type: "Warning"` and reasons like `TransientErr` and `BackoffLimitExceeded`. These appear in Cloud Logging under `resource.type="k8s_container"` in the `atlas-operator` namespace.

## Goals / Non-Goals

**Goals:**
- Detect Atlas Operator migration failures within minutes via Cloud Monitoring
- Send Slack notifications using existing notification channels
- Manage as IaC in the existing `MonitoringComponent`

**Non-Goals:**
- Alerting on Atlas Operator pod health (OOM, CrashLoopBackOff) — covered by GKE default monitoring
- Alerting on migration duration or performance
- Creating new Slack notification channels

## Decisions

### 1. Log filter strategy

**Decision**: Filter on atlas-operator container logs containing error keywords rather than Kubernetes events.

Atlas Operator logs migration errors at `DEBUG` level with event type `Warning`. The log entries contain identifiable strings: `TransientErr` and `BackoffLimitExceeded`.

**Verified (2026-03-05)**: Atlas Operator uses controller-runtime with zap. By default it uses the console encoder (plain text to `textPayload`). After enabling `--zap-encoder=json` via Kustomize patch (cloud-provisioning PR #130), logs arrive as `jsonPayload` with structured fields including `reason`, `msg`, `logger`, `level`, and `type`.

Filter (verified against actual Cloud Logging entries with JSON encoder enabled):
```
resource.type="k8s_container"
resource.labels.namespace_name="atlas-operator"
resource.labels.container_name="manager"
jsonPayload.reason=~"TransientErr|BackoffLimitExceeded"
```

**Alternative considered**: Filtering on `textPayload`. Initially used when Atlas Operator logged in plain text (default console encoder). After enabling JSON structured logging, logs arrive as `jsonPayload`, so `textPayload` filters no longer match. Using `jsonPayload.reason` provides precise field-level matching.

**Alternative considered**: Filtering on `severity="ERROR"` alone. Rejected because ALL Atlas Operator logs have severity ERROR (GKE maps stderr → ERROR), which would alert on every normal log line.

**Alternative considered**: Including `Error:` as a filter keyword. Rejected because `Error:` is too generic and appears in non-failure log lines (e.g., error field labels in structured debug output), which would cause false-positive alerts.

### 2. Alert policy structure

**Decision**: Add a single alert policy for Atlas migration failures, separate from the existing workload error alerts.

**Rationale**: Atlas Operator is infrastructure (not a backend workload), so it needs a different log filter, different label extractors, and different documentation. Adding it to the existing workload loop would conflate concerns.

### 3. Implementation location

**Decision**: Add to `MonitoringComponent` as a separate alert policy alongside the existing workload alerts.

The component already handles alert policies and notification channels. Adding another `gcp.monitoring.AlertPolicy` resource follows the established pattern.

## Risks / Trade-offs

- **[Risk] Atlas Operator log format changes across versions** → Pin to known log patterns. Review on operator upgrades.
- **[Risk] Alert fatigue from repeated failures** → Same 12-hour rate limit as existing alerts. Atlas Operator also has a `backoffLimit` that stops retries.
