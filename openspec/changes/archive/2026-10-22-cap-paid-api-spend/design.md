## Context

See proposal.md - Why. State on 2026-10-22, read from prod:

- Cost guards: one alerts-only Cloud Billing budget, `liverty-music-prod monthly budget` (¥10,000, thresholds 50/90/100%, scoped to the prod project). It is managed in cloud-provisioning `src/gcp/index.ts` ("9. Cost Guardrails"). Its comment still says the budget is dormant, but it has been live since 2026-05-15 (ESC `budgetAmountJpy: '10000'`, `billingAlertEmail` set).
- AI Studio also has a project spend cap of ¥6,000 on `liverty-music-prod` ("Monthly spend cap", Experimental). It can be set only in AI Studio.
- `places.googleapis.com` per-day quotas are at their defaults. Billing export use (2026-05-30 to 2026-10-20, prod): Text Search Pro 2,069 requests in total and at most 588 in a day, Place Details Pro 1, Autocomplete 7. Nothing else is used. All of it fell inside the monthly free usage.

| quota id | default per day | price per 1,000 | worst day at default |
|---|---|---|---|
| SearchTextRequestPerDayPerProject | 75,000 | $32.00 | about ¥377,000 |
| GetPlaceRequestPerDayPerProject | 125,000 | $17.00 | about ¥334,000 |
| AutocompletePlacesRequestPerDayPerProject | 175,000 | $2.83 | about ¥78,000 |

- Gemini API spend in prod (gross): June ¥4,741, July ¥6,086, August ¥6,449, September ¥6,425, October up to the 21st ¥3,171. About 70–90% of it is Google Search grounding at $14 per 1,000 queries beyond 5,000 free queries per month per project.
- Backend error mapping: map catalog calls go through `api.FromHTTP`, which maps HTTP 429 to ResourceExhausted (`backend/pkg/api/errors.go`). The Gemini searchers retry 429 and, when retries run out on a transient error, return empty results (`searcher.go`, "grounded call exhausted retries with transient error").
- A Gemini spend cap has already been enforced once: the AI Studio cap stopped prod on 2026-09-30. Every refused call returned `Error 429, Message: Your project has exceeded its monthly spending cap. ... Status: RESOURCE_EXHAUSTED`. The backend treated it as transient, retried, and stored nothing: concert-discovery logged "executePass exhausted retries with transient network error" once, and sales-phase-discovery logged "exhausted retries, returning empty result" 64 times.

## Goals / Non-Goals

**Goals:**
- A bound on the worst-case spend of each paid external API that the backend calls in prod, enforced by Google and not by our code.

**Non-Goals:**
- A cost guard for GKE, Cloud SQL or other infrastructure. Their cost is bounded by their own configuration, not by request volume.
- dev: dev is stopped, and the dev project has no paid API traffic.
- Per-artist or per-call cost reporting (a separate change: route Gemini response metadata to BigQuery).

## Decisions

### Request quotas for the map catalog, not a budget

The map catalog is not eligible for Cloud Billing spend caps (eligible: Gemini API, Vertex AI, Cloud Run, Cloud Run functions). A budget-triggered function that disables the API or billing acts only after billing data arrives, which takes hours. Disabling billing would also stop every resource in the project, and Google warns that "Resources might be irretrievably deleted". A per-day quota refuses a request at the moment the limit is crossed. A quota is therefore the only guard that stops a loop on the same day.

Values: SearchText 1,000 (about 1.7× the observed peak of 588), GetPlace 100, Autocomplete 100, and 0 for every other `*PerDayPerProject` quota of the service. Worst case after the change: about ¥5,000 per day, and about ¥120,000 per month, beyond the free usage. If a lower monthly bound is needed, it comes from a lower daily value.

They are set with `gcp.cloudquota.SQuotaPreference` inside the existing `if (gcpConfig.quotaContactEmail)` block, which already manages the Compute quotas and enables `cloudquotas.googleapis.com`. Values are fixed in code, as the Compute quotas are. Per-minute quotas stay at their defaults: the daily limit is the cost bound.

Every value is a decrease of more than 10% from the default. The Cloud Quotas API rejects such a preference unless `ignoreSafetyChecks: QUOTA_DECREASE_PERCENTAGE_TOO_HIGH` is set, so each preference sets it. `QUOTA_DECREASE_BELOW_USAGE` is not waived, because every value is above observed use. The provider types the field as a single string.

A refused request costs nothing. Google Maps Platform's response-status table lists `RESOURCE_EXHAUSTED` / HTTP 429 as "Reported to Billing: No" (https://developers.google.com/maps/reporting-and-monitoring/reporting). The table covers Maps API statuses in general, without naming Places API (New).

The values stay in code, not ESC, because there is only one environment that uses them (prod). In dev, the same code would lower dev's quotas too. That is harmless, since dev is stopped.

### Gemini spend cap through the Budget API, outside IaC (workaround)

Cloud Billing spend cap budgets support the Gemini API (service `AEFD-7695-64FA`). The Pulumi GCP provider 10.1.0 `gcp.billing.Budget` and gcloud 586.0.0 `billing budgets create` have no spend-cap field, so the budget was created on 2026-10-22 with a direct `POST https://billingbudgets.googleapis.com/v1/billingAccounts/<billing account>/budgets`:

- displayName `liverty-music-prod Gemini API spend cap`, ¥4,000, projects `[projects/<prod project number>]`, services `[services/AEFD-7695-64FA]`, `EXCLUDE_ALL_CREDITS`, `MONTH`
- thresholds 50/80/100% current spend (the only allowed set), `enableProjectLevelRecipients: true`, `spendCap.inputState: CONFIGURED`. Project-level recipients are the project's owners; the owner confirmed on 2026-10-22 that the budget's email reaches them.
- response `spendCap.outputState: CONFIGURED`

This is a workaround for missing provider support. When the provider exposes the spend cap, the budget moves into `src/gcp/index.ts` with a `pulumi import`.

When the cap is enforced, the budget cannot be edited or deleted. To resume within the month, PATCH it with `updateMask=spendCap.inputState` and `inputState: AWAITING_NEXT_PERIOD`. It lifts itself at the start of the next period.

The AI Studio cap (¥6,000) is left as it is. The lower GCP cap triggers first, and when both exist "the budget that receives usage cost faster is triggered first", so the AI Studio cap only acts if the GCP budget is removed.

### Project budget unchanged

The alerts-only budget stays at ¥10,000. Prod spent ¥15,792–¥21,950 a month from June to September, so the 100% alert fires every month. That is accepted: it is an alert, not a cap.

## Risks / Trade-offs

- [Concert discovery stops for the rest of the month when the Gemini cap triggers. At the October pace, that happens in late October. A refused call returns HTTP 429 RESOURCE_EXHAUSTED, which the searchers retry before giving up, so each run takes longer but bills nothing] → Accepted by the owner on 2026-10-22. The product has no users yet. Lift through the Budget API if needed.
- [A legitimate burst of venue lookups, such as a backfill of place ids, hits the 1,000-per-day limit] → The backfill resumes the next day. Raise the quota preference in code for a planned backfill.
- [Billing data lag lets Gemini spend overshoot the cap by up to the usage of the lag window] → Accepted. The October daily peak was ¥1,883, so the overshoot is expected to be in that order.
- [A request kind set to 0 turns out to be needed] → It fails with ResourceExhausted at once and is visible in logs. Raise the quota in code.

## Migration Plan

1. Merge the cloud-provisioning PR. Merging to `main` runs the dev `pulumi up` automatically. Run the prod `pulumi up` manually, as for every prod change.
2. Read the effective quota values back from the Cloud Quotas API (`quotaInfos` / `quotaPreferences`).
3. Rollback: revert the PR and run `pulumi up`. The quota preferences are deleted and the defaults return.
