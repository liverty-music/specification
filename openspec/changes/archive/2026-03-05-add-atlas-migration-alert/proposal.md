## Why

Atlas Operator migration failures on the dev cluster went undetected for a week (2026-02-28 to 2026-03-05), blocking all schema changes. The existing Cloud Monitoring alerts only cover backend application workloads (server, consumer, concert-discovery) in the `backend` namespace. Atlas Operator runs in `atlas-operator` namespace and has no alerting.

## What Changes

- Add a Cloud Monitoring log-based alert policy for Atlas Operator migration failures in `cloud-provisioning/src/gcp/components/monitoring.ts`
- The alert detects WARNING-level events from the Atlas Operator containing migration errors (e.g., `TransientErr`, `BackoffLimitExceeded`)
- Notifications sent to the same Slack channel used by existing backend error alerts

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `app-error-log-alerting`: Extend alerting scope to include Atlas Operator migration failures in the `atlas-operator` namespace

## Impact

- `cloud-provisioning/src/gcp/components/monitoring.ts`: Add new alert policy for atlas-operator namespace
- Cloud Monitoring: New alert policy created via Pulumi
- Slack: Migration failure notifications sent to existing alert channel
