# Tasks

## 1. Generative AI spend cap (components/infrastructure/backend/process/paid-api-spend-cap)

- [x] 1.1 Create the Gemini API spend cap budget (¥4,000, prod project, `services/AEFD-7695-64FA`) through the Cloud Billing Budget API and verify the response shows `spendCap.outputState: CONFIGURED` (done 2026-10-22)

## 2. Map catalog daily quotas (cloud-provisioning, components/infrastructure/backend/process/paid-api-spend-cap)

- [x] 2.1 In `src/gcp/index.ts`, add `gcp.cloudquota.SQuotaPreference` resources for `places.googleapis.com` inside the `quotaContactEmail` block: SearchText 1,000, GetPlace 100, Autocomplete 100, and 0 for every other `*PerDayPerProject` quota the Cloud Quotas API lists for the service; verify `make check` passes and `pulumi preview` on prod shows these 10 creates and no other GCP resource change
- [x] 2.2 Correct the "9. Cost Guardrails" comment that calls the budget dormant, and note the out-of-IaC Gemini spend cap budget there with its name; verify with `make check`
- [ ] 2.3 After the PR merges, have the owner run the prod `pulumi up` from the Pulumi Cloud console, and read back each quota's effective value from the Cloud Quotas API; verify every value matches 2.1

## 3. Verification in prod

- [ ] 3.1 Check the scenarios that need no load, read-only: the quota values from 2.3 cover "Text searches beyond the daily limit", "Next day after the limit" and "Unused request kind" (Google enforces them); the spend cap budget's thresholds and `outputState` cover "Cap reached mid-month", "New month after the cap" and "Half of the project budget"; record the evidence under the @spec-manual lines below

@spec-manual components/infrastructure/backend/process/paid-api-spend-cap "Text searches beyond the daily limit" -- task 2.3 (effective SearchText quota 1,000 read from the Cloud Quotas API; enforced by Google)
@spec-manual components/infrastructure/backend/process/paid-api-spend-cap "Next day after the limit" -- task 2.3 (per-day quota resets at midnight Pacific Time; enforced by Google)
@spec-manual components/infrastructure/backend/process/paid-api-spend-cap "Unused request kind" -- task 2.3 (effective value 0 for every other per-day quota)
@spec-manual components/infrastructure/backend/process/paid-api-spend-cap "Cap reached mid-month" -- task 1.1 (spend cap budget CONFIGURED; status code recorded when it first triggers)
@spec-manual components/infrastructure/backend/process/paid-api-spend-cap "New month after the cap" -- task 1.1 (spend caps lift at the start of the next budget period per Cloud Billing docs)
@spec-manual components/infrastructure/backend/process/paid-api-spend-cap "Half of the project budget" -- task 3.1 (budget threshold rules read from the Budget API)
