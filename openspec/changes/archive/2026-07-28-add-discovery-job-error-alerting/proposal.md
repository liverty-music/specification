## Why

The `sales-phase-discovery` and `merch-discovery` CronJobs intentionally exit 0 on failure (to avoid a broken run retrying into the same fault), relying on ERROR-log alerting as the sole failure-detection mechanism. But the `app-error-log-alerting` capability enumerates alert coverage for only `server`, `consumer`, and `concert-discovery` — the two newer discovery jobs were never added. As a result their failures are completely silent: the process exits 0, Kubernetes reports the Job as succeeded, and no Incident opens. A live example was observed on 2026-07-28, when a `sales-phase-discovery` run failed at startup with a database ping timeout, exited 0, and produced no alert — the design's stated compensating control did not exist for that job.

## What Changes

- Extend ERROR-log alert coverage to the `sales-phase-discovery` and `merch-discovery` CronJob workloads, so an ERROR-level log entry from either opens an Incident with Slack + Google Chat notification (identical filter, rate-limit, auto-close, and label-extractor behavior as the existing per-workload policies).
- Make explicit, at the capability level, that every backend discovery CronJob exits 0 on failure by design and therefore MUST have ERROR-log alert coverage — so adding a new discovery job without alert coverage is a spec violation, not a silent omission. This closes the class of gap rather than just the two current instances.
- Align the implementation: add the two workloads to the Pulumi alert-policy list, and document the deliberate exit-0-on-failure semantics in `sales-phase-discovery`'s job entrypoint (it currently lacks the explanatory comment that `merch-discovery` already carries).

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `app-error-log-alerting`: The "Error log detection per workload" requirement's enumerated workload set changes from `(server, consumer, concert-discovery)` to also include `sales-phase-discovery` and `merch-discovery`, with a scenario for each. A new requirement is added mandating ERROR-log alert coverage for every backend discovery CronJob, on the basis that these jobs exit 0 on failure by design.

## Impact

- **Capability spec**: `openspec/specs/app-error-log-alerting/spec.md` (modified requirement + new requirement).
- **cloud-provisioning**: `src/gcp/components/monitoring.ts` — add `{ displayName: 'Sales Phase Discovery', appLabel: 'sales-phase-discovery' }` and `{ displayName: 'Merch Discovery', appLabel: 'merch-discovery' }` to the per-workload alert-policy list. Two new `gcp.monitoring.AlertPolicy` resources are created on `pulumi up` (prod is a manual console `up`).
- **backend**: `cmd/job/sales-phase-discovery/main.go` — add the exit-0-on-failure rationale comment to match `cmd/job/merch-discovery/main.go` (documentation only; no behavior change).
- **Out of scope** (tracked separately): retrying transient infra faults (e.g., DB ping timeout) inside the job before giving up, and the grounding-consistency work already tracked under #639. This change is scoped to closing the alerting-coverage gap for the exit-0 design.
