## Context

Backend workload failures are surfaced through per-workload Cloud Monitoring Log-Based Alert Policies defined in `cloud-provisioning/src/gcp/components/monitoring.ts`. Each policy matches `severity="ERROR"` logs for one `labels.k8s-pod/app` value and opens an Incident routed to Slack + Google Chat. The `app-error-log-alerting` capability enumerates coverage for `server`, `consumer`, and `concert-discovery`.

The discovery CronJobs are designed to exit 0 on failure. `cmd/job/merch-discovery/main.go` documents the rationale explicitly ("a systemic failure should not make the CronJob retry into the same fault. Monitoring relies on ERROR logs."); `cmd/job/sales-phase-discovery/main.go` has the identical behavior but no comment. Because the Job always reports `succeeded=1`, the ERROR-log alert is the sole failure signal — yet `sales-phase-discovery` and `merch-discovery` were never added to the alert-policy list. On 2026-07-28 a `sales-phase-discovery` run failed at startup with a database ping timeout, exited 0, and opened no Incident, confirming the gap in production.

The pod `app` labels are already correct and consistent: `kubectl get cronjob` shows `sales-phase-discovery-app → app=sales-phase-discovery` and `merch-discovery-app → app=merch-discovery` (same shape as `concert-discovery`), so no label plumbing is required.

## Goals / Non-Goals

**Goals:**
- Every backend discovery CronJob has an ERROR-log Alert Policy, so a failed run (which exits 0) reliably opens an Incident.
- Encode the exit-0-on-failure ⇒ alert-coverage-mandatory relationship at the capability level so the gap cannot silently recur when a future discovery job is added.
- Make the `sales-phase-discovery` entrypoint self-document its exit-0 design, matching `merch-discovery`.

**Non-Goals:**
- Retrying transient infra faults (e.g., a DB ping timeout) inside the job before giving up. That is a separate reliability improvement, orthogonal to alert coverage, and is deliberately deferred.
- Changing the exit-0 semantics themselves (they are intentional; this change reinforces them).
- Grounding-consistency / recall work for the sales-phase searcher (tracked under #639).
- Job-level Kubernetes failure alerting (e.g., `kube_job_failed`) — on the *handled*-failure path the jobs exit 0 by design, so a Job-status alert would not fire and ERROR-log alerting is the correct layer. NOTE: this holds only for handled failures. Abrupt-termination failures (OOM-kill, image-pull failure, node preemption/eviction) DO report the Job as failed and emit no ERROR log, so they are covered by neither mechanism — a separate, currently-uncovered gap this change deliberately does not close (a future Job-status alert would be the right layer for it).

## Decisions

**Decision: Reuse the existing per-workload `workloads[]` array rather than a bespoke policy.**
The two new jobs share the exact filter shape, label extractors, rate limit (12h), auto-close (1h), and notification channels of the existing policies. Adding two entries to the `workloads` array produces two more `AlertPolicy` resources with zero new code paths. Alternative considered: a single combined policy matching all discovery jobs via a regex on `labels.k8s-pod/app` — rejected because it loses per-workload Incident separation and the per-workload `displayName` that operators rely on, and diverges from the established one-policy-per-workload pattern.

**Decision: Encode the exit-0 ⇒ alert-coverage invariant as a new capability requirement.**
The root cause is not two missing entries but a missing invariant: discovery jobs exit 0, so alert coverage is their only failure signal, yet nothing in the spec said coverage was mandatory. The new "Discovery CronJob failure observability" requirement makes adding a discovery job without a policy a spec violation, closing the class of gap. Alternative considered: just add the two workloads and file an issue — rejected because it fixes the instances but not the recurrence risk.

**Decision: Add the rationale comment to `sales-phase-discovery/main.go` (documentation only).**
The behavior is already correct and intentional; the divergence is that only merch documents it. Copying the comment removes the "is this a bug?" ambiguity for future readers without any behavior change.

## Risks / Trade-offs

- **New AlertPolicy for a not-yet-ingested metric/label could fail `pulumi up`** → These are Log-Based (conditionMatchedLog) policies, not metric-threshold policies; they do not require a pre-existing ingested metric, so the not-yet-ingested-metric failure class (seen with GMP metric-threshold policies) does not apply. The `k8s-pod/app` labels already exist on running pods.
- **Alert noise from benign per-artist errors** → The 12-hour `notificationRateLimit` and 1-hour `autoClose` already bound noise to at most one notification per policy per 12h, matching the existing workloads. Benign, expected non-errors (no upcoming series, missing official site) are logged at INFO/WARN, not ERROR, so they do not trigger the policy.
- **prod deploy is a manual Pulumi console `up`** → Merging the cloud-provisioning PR only runs `pulumi preview` for prod. The policies must be applied via the prod Pulumi Cloud console `up` after merge; the task list calls this out so coverage is actually live, not just merged.

## Migration Plan

1. Merge the specification change (delta → `app-error-log-alerting` spec on archive).
2. Merge the cloud-provisioning PR adding the two `workloads` entries; dev applies automatically via Pulumi Cloud Deployments.
3. Trigger the prod Pulumi console `up`; confirm the two new `AlertPolicy` resources exist and are enabled.
4. Merge the backend comment-only change (rides the next routine backend release; no release needed solely for a comment).
5. Verify: emit or locate a real ERROR log from each job and confirm an Incident opens (or validate the policy filter against a historical ERROR entry, e.g., the 2026-07-28 DB-ping failure).

**Rollback:** remove the two `workloads` entries and re-run `pulumi up`; the policies are deleted. No data or behavior impact.

## Open Questions

- None blocking. (Whether to also add transient-fault retry inside the jobs is intentionally out of scope and left to a follow-up.)
