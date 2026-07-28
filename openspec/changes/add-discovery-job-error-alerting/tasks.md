## 1. cloud-provisioning — alert coverage

- [ ] 1.1 In `src/gcp/components/monitoring.ts`, add two entries to the per-workload `workloads[]` array: `{ displayName: 'Sales Phase Discovery', appLabel: 'sales-phase-discovery' }` and `{ displayName: 'Merch Discovery', appLabel: 'merch-discovery' }`.
- [ ] 1.2 Run `make lint-ts` (biome + tsc) and confirm `pulumi preview` (dev) shows exactly two new `gcp.monitoring.AlertPolicy` resources (`alert-error-log-sales-phase-discovery`, `alert-error-log-merch-discovery`) and no unintended diffs.
- [ ] 1.3 Open the cloud-provisioning PR; on merge, dev applies automatically via Pulumi Cloud Deployments.

## 2. backend — document exit-0 design

- [ ] 2.1 In `cmd/job/sales-phase-discovery/main.go`, add the exit-0-on-failure rationale comment inside `main()` (mirroring `cmd/job/merch-discovery/main.go`): a systemic failure must not retry into the same fault; monitoring relies on ERROR logs. Documentation only — no behavior change.
- [ ] 2.2 Run `make check` (lint + unit tests) green. This rides the next routine backend release; do NOT cut a release solely for a comment.

## 3. prod rollout

- [ ] 3.1 After the cloud-provisioning PR merges, trigger the prod Pulumi Cloud console `up` (prod does not auto-apply on merge). Confirm the two new `AlertPolicy` resources are created and enabled with Slack + Google Chat notification channels attached.

## 4. Verification & close-out

- [ ] 4.1 Confirm both new Alert Policies exist in prod Cloud Monitoring with the correct filter (`labels.k8s-pod/app` = `sales-phase-discovery` / `merch-discovery`, `severity="ERROR"`, namespace `backend`).
- [ ] 4.2 Validate coverage via ONE of (these are genuine alternatives — a log-based `conditionMatchedLog` policy only evaluates entries ingested AFTER it is created, so a pre-existing historical entry can never retroactively open an Incident): (a) trigger a controlled ERROR (or emit/locate a real one after the policy exists) and confirm an Incident opens and notifies Slack + Google Chat; OR (b) validate the policy filter matches a historical entry (e.g., the 2026-07-28 `sales-phase-discovery` DB-ping failure) in Logs Explorer, WITHOUT requiring a new Incident.
- [ ] 4.3 Verify the change (`/opsx:verify`) and archive it once all tasks are complete and shipped to prod.
