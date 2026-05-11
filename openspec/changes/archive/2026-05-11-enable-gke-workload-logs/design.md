## Context

The dev GKE cluster (`standard-cluster-osaka`) was provisioned with `loggingConfig.enableComponents: ['SYSTEM_COMPONENTS']` — only kube-system stdout is shipped to Cloud Logging; workload (`backend`, `zitadel`, `otel-collector`, etc.) stdout is dropped at the node-level fluent-bit before reaching the Cloud Logging API. The original code comment frames this as "all alerts are log-based" (i.e., metric-based alerts via GMP are off), but the actual log-based alerts read from Cloud Logging, which the configuration prevents.

The discrepancy was observed empirically while validating §1.13 of the archived `zitadel-observability` change. A synthetic ERROR log pod (`smoke-test-jwt-log` in the `backend` namespace) was confirmed to emit to its container stdout (visible via `kubectl logs`) but did not appear in Cloud Logging. A broader query (`gcloud logging read 'resource.type="k8s_container"' --freshness=24h`) returned only `kube-system` entries, never `backend`/`zitadel`/`otel-collector`. `gcloud container clusters describe ... --format='value(loggingConfig.componentConfig.enableComponents)'` returned `SYSTEM_COMPONENTS` — confirming the gap is the cluster's logging-collection scope, not a per-pod or per-namespace filter.

Affected alerts that have been silently non-functional:

- `alert-error-log-server` (Server ERROR Log)
- `alert-error-log-consumer` (Consumer ERROR Log)
- `alert-error-log-concert-discovery` (Concert Discovery ERROR Log)
- `alert-poison-queue-message` (Consumer Poison Queue Message)
- `alert-atlas-migration-failure` (Atlas Operator Migration Failure)
- `alert-backend-jwt-zitadel-errors` (Backend JWT validation error rate — added in `zitadel-observability` PR-1b)

## Goals / Non-Goals

**Goals:**

- Make existing log-based alerts in `MonitoringComponent` and `ZitadelMonitoringComponent` start functioning by ensuring workload container stdout reaches Cloud Logging.
- Preserve the cost-minimisation intent of the original configuration — only loosen what's necessary for log-based alerting; keep metric-based monitoring (GMP) off.
- Make the contradiction in `kubernetes.ts:437-441` impossible to recreate by updating both the code comment and the spec wording so a future reader sees the rationale explicitly.

**Non-Goals:**

- Enabling Google Managed Prometheus (`monitoringConfig.enableComponents += WORKLOADS`). We do not have metric-based workload alerts today; opening this lane requires its own cost-vs-value analysis. `monitoringConfig` stays `['SYSTEM_COMPONENTS']`.
- Reducing log volume through filters or log routing. If cost grows materially we will revisit, but the projection is small relative to current GCP spend.
- Retroactive analysis of which past incidents went undetected. The alerts are off; any historical no-alert state is a fact, not actionable.

## Decisions

### D1: Update `loggingConfig.enableComponents` to `['SYSTEM_COMPONENTS', 'WORKLOADS']`

The GKE cluster's `loggingConfig.componentConfig.enableComponents` field accepts an enum list. `WORKLOADS` is the canonical component for non-system pod stdout. We pick this rather than `WORKLOADS` alone (which would also drop kube-system logs, breaking control-plane visibility) or `APISERVER`/`SCHEDULER`/`CONTROLLER_MANAGER` (those are GKE control-plane variants we don't want to pay for in dev). Reference: https://cloud.google.com/kubernetes-engine/docs/how-to/configure-logging.

**Alternative considered**: per-pod logging filters via fluent-bit configmap. Rejected — GKE Standard's fluent-bit is managed; user-level config would require deploying a separate agent and is more operational complexity than the one-flag change buys back.

### D2: GKE handles the change in-place; no node-pool recreation or pod disruption

The GKE `loggingConfig` update is a control-plane property. GCP applies it by re-rolling the cluster's managed logging agents on each node — this happens during the standard maintenance window or immediately on update, depending on cluster setup. No node pool recreation, no workload pod restart. Verified via GKE documentation that node disruption is not part of the change surface for logging-config updates.

**Alternative considered**: blue-green cluster swap. Rejected — heavyweight, unnecessary for a non-destructive update.

### D3: Preserve the original cost-restriction intent by splitting the spec requirement

The current `gke-standard-infrastructure` spec bundles "no GMP" and "logging system-only" and "monitoring system-only" under one Requirement: *"Dev cluster SHALL disable Google Managed Prometheus and restrict logging and monitoring to system components only."* This conflates three independent decisions. The delta keeps "no GMP" + "monitoring system-only" but moves "logging" out into its own Requirement that now permits `WORKLOADS`.

**Why this matters for the spec**: future readers should see *why* logging differs from monitoring (logging is the input to log-based alerts; monitoring isn't tied to alerting in dev today). Bundling them obscures that distinction.

### D4: No new tests in the Pulumi component beyond what `make check` already enforces

The change is a one-line config update. The `KubernetesComponent` unit tests in `cloud-provisioning/src/gcp/components/__tests__/` (if any cover GKE cluster config) should be updated. Behaviour is verified post-deploy via `gcloud container clusters describe` (which we ran during diagnosis — same command works for verification).

## Risks / Trade-offs

- **[Cost increase]** Workload log volume becomes Cloud Logging billable. → Mitigation: dev traffic is light. Projected < 1 GiB/month in steady-state. The existing `gcp-cost-guardrails` billing budget already alerts at 50/90/100% of monthly target — any unexpected spike will surface there.

- **[Initial alert noise]** Pre-existing ERROR conditions in workloads that were never paged will now fire. → Mitigation: review existing alert documentations (each AlertPolicy has a `documentation.content` triage block); be prepared to triage one or two real issues that the cluster has been hiding from us. This is intended — surfacing the backlog is the point.

- **[GKE schedule unpredictability]** `gcloud container clusters describe` will reflect the new config immediately, but the managed logging agent rollout may lag depending on maintenance window. → Mitigation: monitor for the first workload log entry in Cloud Logging after the Pulumi deploy completes; if not seen within 15 min, force a manual maintenance via `gcloud container clusters update --no-async`.

- **[Audit-log noise]** Some workload pods (e.g., `cloud-sql-proxy` sidecar) emit large volumes of routine connection logs. → Mitigation: out of scope for this change. If volume becomes a problem, add Cloud Logging exclusion filters at the project level — separate openspec change.

## Migration Plan

1. Pulumi PR to `cloud-provisioning` updating `kubernetes.ts:437-441`: `enableComponents` array gains `'WORKLOADS'`; the surrounding comment is rewritten to explain the intent (cost minimisation for monitoring, alert-enablement for logging).
2. CI must pass: `make check` (biome + tsc + vitest) + `pulumi preview` shows only the cluster `~ loggingConfig` diff plus any pre-existing unrelated drift.
3. Merge → Pulumi Cloud Deployments auto-applies the cluster update.
4. Post-merge verification:
   - `gcloud container clusters describe standard-cluster-osaka --zone=asia-northeast2-a --format='value(loggingConfig.componentConfig.enableComponents)'` → `SYSTEM_COMPONENTS;WORKLOADS`
   - `gcloud logging read 'resource.type="k8s_container" AND resource.labels.namespace_name="backend"' --freshness=15m` returns recent workload logs.
   - Retry the `zitadel-observability` §1.13 smoke-test (synthetic ERROR pod, lowered JWT alert threshold) — alert now fires, notification confirmed in Slack + Google Chat. Revert threshold.

**Rollback**: revert the Pulumi PR. GKE applies the previous `enableComponents` list — workload logs stop flowing on the next agent rollout. State is the same as before the change. No data loss (logs already ingested remain in Cloud Logging until retention expires).

## Open Questions

- (none — the change is small enough that no decisions are deferred)
