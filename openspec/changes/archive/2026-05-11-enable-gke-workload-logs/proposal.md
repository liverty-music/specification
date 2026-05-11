## Why

The dev GKE cluster's `loggingConfig.enableComponents` is restricted to `['SYSTEM_COMPONENTS']`, meaning workload pod stdout is **never sent to Cloud Logging**. Discovered while running §1.13 of the archived `zitadel-observability` change: synthetic ERROR logs from a `backend` namespace pod were never ingested. Verified via `gcloud container clusters describe` and the Pulumi source at `cloud-provisioning/src/gcp/components/kubernetes.ts:439-441`.

The current setup contradicts the comment in the same source file — *"all alerts are log-based"* — yet log-based alerts cannot fire when workload logs are not collected. Five existing alert policies in `MonitoringComponent` (`Server ERROR Log`, `Consumer ERROR Log`, `Concert Discovery ERROR Log`, `Consumer Poison Queue Message`, `Atlas Operator Migration Failure`) plus the two newly added in `ZitadelMonitoringComponent` have been **silently non-functional** since the cluster was created. Any past incident that should have paged the operator went undetected — including §18.6 cutover-incident hangs unless an operator happened to be watching.

## What Changes

- Set `loggingConfig.enableComponents: ['SYSTEM_COMPONENTS', 'WORKLOADS']` on the dev GKE cluster via Pulumi.
- Update the `gke-standard-infrastructure` spec to reflect the new configuration. The intent of the original requirement (cost reduction by restricting Cloud Logging volume) is preserved for monitoring but relaxed for logging — log-based alerting is the actual cost lever, and it does not work without workload logs.
- Verify post-deploy that workload logs flow into Cloud Logging and the existing log-based alerts now fire on real ERROR events. Re-run the §1.13 smoke-test deferred from `zitadel-observability`.

## Capabilities

### New Capabilities

- (none)

### Modified Capabilities

- `gke-standard-infrastructure`: the requirement *"Dev cluster SHALL disable Google Managed Prometheus and restrict logging and monitoring to system components only"* SHALL be split — monitoring stays system-only (GMP disabled, `monitoringConfig.enableComponents` unchanged at `['SYSTEM_COMPONENTS']`), but logging SHALL include `WORKLOADS` so log-based alerts can fire.

## Impact

- **Pulumi**: one-line change in `cloud-provisioning/src/gcp/components/kubernetes.ts`. GKE supports the update in-place (no cluster recreation, no node disruption).
- **Cloud Logging cost**: workload log ingestion is billed at ~$0.50/GiB. Dev traffic is low-volume so the projected increase is small but non-zero — estimated < 1 GiB/month based on backend stdout volume during incident-free operation. Spike during incidents (which is exactly when we *want* the logs). Worth tracking via the existing `gcp-cost-guardrails` capability's billing budget.
- **Existing log-based alerts** (`alert-error-log-server`, `alert-error-log-consumer`, `alert-error-log-concert-discovery`, `alert-poison-queue-message`, `alert-atlas-migration-failure`, `alert-backend-jwt-zitadel-errors`): start functioning after this lands. Expect a small initial spike of paged ERRORs as legacy backlog clears — operator should be aware.
- **Out of scope**: workload monitoring (Prometheus / `monitoringConfig.enableComponents`) stays system-only. We do not have metric-based alerts on workloads today; opening this for the first time requires its own cost-vs-value analysis.
- **Coordinates with**: archived `zitadel-observability` §1.13 (smoke-test the latency alert). That task was blocked by this missing precondition and can be retried after this change deploys.
