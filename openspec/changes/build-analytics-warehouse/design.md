## Context

See proposal.md for why. What shapes the approach, read on 2026-10-23:

- `billing_export` is a prod-only Pulumi `BillingExportComponent` in asia-northeast1 (`cloud-provisioning/src/gcp/components/billing-export.ts:61-77`, wired in `src/gcp/index.ts:415-420`). It holds the standard, detailed (resource-level, with GKE `k8s-namespace` labels) and pricing exports.
- BigQuery joins only datasets in the job's location (`docs.cloud.google.com/bigquery/docs/locations`). Osaka has no BigQuery Studio code assets and no remote models; Dataform and Data Studio work with both regions.
- The prod `_Default` log bucket keeps 30 days; there is no sink besides `_Default` and `_Required`. Logging ingestion is about 21 GiB a month against a free 50 GiB (billing export, 2026-09 and 2026-10).
- A Log Router sink to BigQuery fixes each table's columns from the first entry and sends mismatching entries to an `export_errors` table (`docs.cloud.google.com/logging/docs/export/bigquery`).
- `@pulumi/gcp` 10.1.0 has `logging.ProjectBucketConfig` (with `enableAnalytics`), `logging.ProjectSink`, `logging.LinkedDataset` and `bigquery.Table` with `view`.
- Dataform needs `workflow_settings.yaml` and `package.json` at the repository root (`docs.cloud.google.com/dataform/docs/manage-repository`).
- PostHog's BigQuery batch export needs `bigquery.jobs.create` on the project and data-editor rights on the dataset, and supports impersonation of our service account (`posthog.com/docs/cdp/batch-exports/bigquery`). The events table is partitioned by day on `timestamp`. Its free tier is 1M exported rows a month. An event filter ("events to exclude") is documented for the Redshift export; for BigQuery it is not confirmed.

## Goals / Non-Goals

**Goals:**

- The requirement in `specs/components/infrastructure/backend/process/structured-logging`.
- All analytics data and views in one location, managed in Pulumi except what PostHog and Data Studio only offer in their own UI.

**Non-Goals:**

- Cloud SQL data in BigQuery. It is planned when ticket sales start, comparing federated queries (the connection must be in Osaka, next to the instance) with Datastream.
- Budgets and spend caps (a separate decision).
- Copying performance telemetry (Web Vitals, slow interactions, RPC telemetry) into BigQuery; it is read in PostHog.

## Decisions

### Datasets

| dataset | content | written by |
|---|---|---|
| `billing_export` | exists | Cloud Billing |
| `posthog_raw` | `events`, `persons` | PostHog batch export |
| `logs_analytics` | linked view of the analytics log bucket | Cloud Logging (read-only link) |
| `analytics_staging` | views: one row per meaning, JST dates, typed columns | Pulumi |
| `analytics_marts` | views read by Data Studio | Pulumi |

All in asia-northeast1, created by one new prod-only `AnalyticsWarehouseComponent` next to `BillingExportComponent`. No default table expiry: history is the point, and the volume is small.

### Logs go through an analytics log bucket, not a BigQuery sink

A `ProjectBucketConfig` `analytics` in asia-northeast1 with `enableAnalytics: true` and `retentionDays: 400`, one `ProjectSink` with the filter `labels.sink="analytics"` into it, and a `LinkedDataset` `logs_analytics`. The linked view keeps each entry's payload as JSON, so a field whose type differs between two lines is not lost, which the BigQuery sink would do.

- Alternative: a sink straight to BigQuery with partitioned tables. Kept as the fallback if task 3.2 finds that an analytics bucket cannot be made in asia-northeast1 or cannot be joined with `billing_export`. The check runs on the real `analytics` bucket instead of a hand-made test bucket first, which saves the manual create-and-delete; the cost is that a failure means replacing Pulumi resources, and a deleted bucket's name stays reserved for 7 days.

Checked on 2026-10-24 after the prod `pulumi up` (update 279, `+12-0~0`; task 3.2):

- The bucket was created in asia-northeast1.
- The link `logs_analytics` is ACTIVE.
- Marked lines of three topics (`job_result`, `notification_delivery`, `catalog_review`) are in `logs_analytics._AllLogs`, from 00:55 UTC on. The first line, at 00:45, came before the sink existed.
- A query that joins `_AllLogs` with `billing_export.gcp_billing_export_v1_01AE48_33F12F_3C7200` by JST day ran in asia-northeast1 and returned 7 marked lines and 6.15 of cost for 2026-10-24.

The fallback is not needed.

### The mark is a log entry label

The backend adds `slog.Group("logging.googleapis.com/labels", slog.String("sink", "analytics"), slog.String("topic", topic))` through one helper, `analyticslog.Attrs(topic, attrs...)` in `backend/pkg/analyticslog` (named so because `logging` is the package name of `pannpers/go-logging`, which every caller already imports). The topics are typed constants. The helper takes the line's attributes and leaves the line unmarked when one of them carries personal data: a key ending in `email`, `phone`, `phone_number` or `address`, a person's name key (`name`, `display_name`, `user_name`, ...), or an email-shaped string value, nested groups included; `artist_name` and `venue_name` stay markable. Attributes added through `logging.SetAttrs` or `Logger.With` are not inspected; no marked line uses them.

Two lines were added beyond the first list in tasks.md, because `mart_pipeline_health_daily` needs them from `logs_analytics` alone: `notification_delivery.go` now also logs a delivered notification (`notification delivered`, INFO), so the delivery rate has a denominator (it logged failures only); and the two lines that put a concert into the review queue (`concert_creation_uc.go`: unresolved venue, same-slot conflict) carry `catalog_review`, so the queue has an "in" next to approve/reject. A re-discovered candidate is upserted again and logs again with a freshly generated `concert_candidate_id` (the upsert keeps the stored id), so the mart counts the queue's in-flow by distinct (`artist_id`, `series_id`, `local_date`). The GKE logging agent turns the `logging.googleapis.com/labels` object into LogEntry labels, which is what Cloud Logging's structured-logging special fields describe; GKE's own docs do not state it, so task 1.1 checks it with one line in prod before anything is built on it. If it fails, the helper writes `sink` and `topic` as plain payload keys and the filter becomes `jsonPayload.sink="analytics"`.

Checked on 2026-10-23 after backend v1.99.0 (#686) reached prod: the `sales-reminders: scan complete` entry at 18:00:05Z carries the LogEntry labels `sink: analytics` and `topic: job_result`, and its `jsonPayload` no longer holds the `logging.googleapis.com/labels` key, so the agent promotes the field on GKE Autopilot. The sink filter stays `labels.sink="analytics"`. The concert discovery job itself was checked on a manual run of the CronJob (`concert-discovery-manual-202610240645`, backend v1.100.0, 2026-10-24 06:51 UTC). Its summary line `concert discovery job complete` (134 artists, 0 failures) carries `sink: analytics` and `topic: job_result`, and it reached `logs_analytics._AllLogs` and `mart_pipeline_health_daily`.

### Views in Pulumi instead of Dataform

Staging and mart views are `bigquery.Table` resources with `view.query` read from `.sql` files under `cloud-provisioning/src/gcp/analytics/sql/`, so they are reviewed in pull requests with the rest of the infrastructure. Dataform would need its own repository (its config must sit at a repository root) and a Git connection for about 6 views. Views cost nothing to keep; at 1,000 monthly fans a mart query scans well under 1 GiB. When a mart needs materialization or tests, Dataform in its own repository is the next step.

The staging views (in `analytics_staging`, all with JST dates):

| view | one row per | from |
|---|---|---|
| `stg_events` | PostHog event, deduplicated by `uuid`, `perf.*` dropped; `has_person` is false for pipeline events | `posthog_raw.events` |
| `stg_persons` | person, latest version, deleted dropped; first `utm_source` / `utm_campaign` | `posthog_raw.persons` |
| `stg_ai_generations` | `$ai_generation`, with `process` and `search` (`concert` when the request has `search_from`, `ticket_sale` when it has `series_ids`) | `stg_events` |
| `stg_billing_daily` | day, service, SKU; `net_cost` = cost + credits, `list_cost` | standard billing export |
| `stg_billing_resource_daily` | day, service, GKE namespace | detailed billing export |
| `stg_log_lines` | marked log line, with `topic`, `app` and `msg` | `logs_analytics._AllLogs` |

Each view's SQL passed `bq query --dry_run` against prod on 2026-10-24 (task 3.3). Views that read other views were dry-run with those views inlined, because they did not exist yet.

After the prod `pulumi up` (update 282, `+12-0~0`), one query per mart returned rows on 2026-10-24:

- `mart_gemini_cost_daily` sums to the bill: 4,729.68 JPY for 2026-10-01 to 10-23 in both the mart and `stg_billing_daily`. All of it was `(unattributed)`, because backend#685 was not yet released.
- `mart_pipeline_health_daily` shows the day's 14 sales-reminders runs, one `new_concerts` delivery that failed with `no_subscription`, three fan-outs that sent nothing, and one candidate queued for review.
- The fan counts in `mart_unit_economics_monthly` and `mart_campaign_value` were partial: the PostHog backfill from 2026-08-01 (events) and 2026-05-31 (persons) was still running.

- `mart_infra_cost_daily` reads the whole detailed export, about 0.7 GB per query today. At that size, the free 1 TiB of queries allows about 1,400 report loads a month. It is the first mart to materialize if reports load it often.
- `mart_gemini_cost_daily` (per process) and `mart_cost_per_concert_monthly` need `$ai_generation`, `concert.ingest.completed` and `ticket_sale.search.completed`. These events come from backend#685 (`expand-product-analytics`), merged and released on 2026-10-24. Gemini cost before 2026-10-24 stays `(unattributed)`. The first attributed day is 2026-10-24: 676.03 JPY to concert-discovery, concert search.
- October 2026 gives no cost per new concert. The Gemini API spend cap (¥4,000 a month, `cap-paid-api-spend`) refused every call from 2026-10-24 11:25 UTC on, with `Error 403 ... Spend cap breached ... PERMISSION_DENIED`. October's bill reached 4,729.68 JPY by 10-23, and billing data lags. From 10-25 to 10-28, all 45 `$ai_generation` events are errors with 0 tokens, so no new concert was found and `mart_cost_per_concert_monthly` shows 0 new concerts. The cap lifts on 2026-11-01, and November is the first month that can check this mart.

### Billing views keep the project

The billing export covers the whole billing account, so it holds `liverty-music-dev` as well as `liverty-music-prod`. The staging views first summed every project, which put development cost into the per-fan and per-concert marts. Measured on 2026-10-29 (list price): dev's Gemini API cost was 1,230 JPY in August 2026, 0 in September and 1,070 in October, and dev's cost for all services was 3,452, 2,028 and 1,857 JPY. In `mart_gemini_cost_daily`, a dev charge was split across the prod processes of that day, or showed as `(unattributed)` on a day with no prod generation (2026-10-28, 7.75 JPY). Task 5.1's September check passed only because dev used no Gemini that month.

The dev charges since the dev environment stopped come from local sessions calling Gemini with the dev key from Pulumi ESC `liverty-music/dev` (a searcher integration test on 2026-10-24, and document reviews on 2026-10-28 and 10-29), not from a workload or a leaked key: each call in the dev project's `serviceruntime` request counts matches a command in those sessions.

So `stg_billing_daily` and `stg_billing_resource_daily` carry `project_id`. The Gemini, per-concert and per-fan marts read `liverty-music-prod` only, because they divide cost by prod's generations, concerts and fans. `mart_infra_cost_daily` keeps `project_id` as a dimension, so dev cost stays visible (task 3.4).

### Splitting the Gemini bill by process

The billing export has no process dimension. `mart_gemini_cost_daily` splits each JST day's Gemini token cost by each process's share of `$ai_generation` tokens that day, and each day's search-query cost by its share of web search queries. The total always equals the bill.

### The marts

| view | answers | sources |
|---|---|---|
| `mart_gemini_cost_daily` | Gemini cost by process, list price and billed | billing, `$ai_generation` |
| `mart_cost_per_concert_monthly` | cost per new concert (concert search) and per new sale (ticket-sale search) | above, `concert.ingest.completed`, `ticket_sale.search.completed` |
| `mart_unit_economics_monthly` | total cost per retained fan (active in 2 of the month's 4 weeks) | billing, PostHog events |
| `mart_infra_cost_daily` | cost by service and GKE namespace | detailed billing export |
| `mart_campaign_value` | sign-ups, retained fans and paid orders by first `utm_source` / `utm_campaign` | PostHog persons and events |
| `mart_pipeline_health_daily` | job runs, failures, notification delivery and failure reasons, review queue in and out | `logs_analytics` |

The North Star (fans who opened a new-concert notification in the week) is a PostHog insight, not a mart. It is a `posthog.Insight` in cloud-provisioning (`ProductAnalytics`), a Trends query of weekly unique persons with `notification.opened` and `type = new_concerts`. The management key needs `insight:write` for it. `type` reaches `notification.opened` only with frontend#837 and backend#685 (`expand-product-analytics`), both merged on 2026-10-24; earlier weeks show 0. Created on 2026-10-24 by the prod `pulumi up` (update 283, `+1-0~0`) as insight `SBk3xMle`, linked from `docs/runbooks/analytics-dashboards.md` (cloud-provisioning#698).

### PostHog export settings

Events and persons, hourly, impersonating the service account `posthog-export@liverty-music-prod`, with `ip` empty and the `perf.*` events excluded.

They are managed in Pulumi (`cloud-provisioning/src/posthog/components/warehouse-export.ts`) and recorded in `docs/runbooks/posthog-bigquery-export.md`. The PostHog Terraform provider (1.0.26, the latest) has no batch export or integration resource, and no issue asks for one. So two dynamic resources call the PostHog REST API, as the Zitadel dynamic resources already do:

- a BigQuery batch export resource, one per model
- a lookup that finds the project's `google-cloud-service-account` integration by its service account email; each export references it through `integration_id`

They authenticate with the existing management key, which needs two more scopes: `integration:read` and `batch_export:write`.

The integration itself is made once in PostHog's UI (checked on 2026-10-24). No API key can hold `integration:write`:

- Personal API keys: the key editor withholds it (`frontend/src/lib/scopes.tsx`, `integration` has `disabledActions: ['write']`).
- Project secret API keys: they accept only the allowlist `PROJECT_SECRET_API_KEY_ALLOWED_API_SCOPE_ACTION` (`posthog/scopes.py`), which does not include it.
- OAuth tokens can carry the scope, but they are short-lived and need a browser.
- Impersonation also works only through an integration: `BigQueryClient.from_service_account_integration` is the only path that impersonates.

Applied on 2026-10-24 (update 281, `+2-0~0`). PostHog lists `BigQuery events` and `BigQuery persons`: hourly, not paused, integration 92474, `use_json_type: true`, and the events export has `exclude_events` set to the four `perf.*` names.

Checked after the first hourly run, at 03:15 UTC on 2026-10-24 (task 4.2):

- `posthog_raw.events` was created, partitioned by day on `timestamp`. It holds 4 rows of 3 events, from 02:15 to 02:16 UTC. 0 rows have an `ip`, and 0 are `perf.*`.
- `posthog_raw.persons` holds 1 row.
- The exports start at their creation. Events and persons from before 2026-10-24 02:00 UTC are not exported until a backfill runs.

The lookup was chosen over storing the integration id in ESC. The id is not copied by hand, and a recreated integration is picked up on the next `pulumi up`. The cost is `integration:read` on a key the prod preview already uses, and one API call per preview. The impersonated integration has no secret in its readable `config`.

- Alternative: create the exports by hand in PostHog's UI. It was rejected because the configuration would then live outside review.

Checked on 2026-10-24 (task 2.2):

- PostHog's BigQuery docs list no event filter; "Events to exclude" is documented only for S3 and Redshift (`posthog.com/docs/data-pipelines/batch-exports/bigquery`, `.../s3`). The docs are out of date: the BigQuery export form shows **Include events** and **Exclude events** (seen on 2026-10-24).
- The API applies the filter to BigQuery. Every destination's inputs include `exclude_events` (PostHog `products/batch_exports/backend/service.py`, `BaseBatchExportInputs`). `sync_batch_export` copies each key of `destination.config` that names an input field. The events query filters with `event NOT IN {exclude_events}` (`temporal/sql/events.py`).
- The match is exact, so the four `perf.*` names seen in the last 90 days are listed: `perf.long_animation_frame`, `perf.slow_interaction`, `perf.rpc_call_telemetry` and `perf.discovery_reveal`. A new `perf.*` event must be added to the list. Until then, the staging view drops any `perf.*` row that gets through.
- No column can be left out either, `ip` included. Project 190464 has `anonymize_ips: true` (read with the PostHog MCP `project-get`), so PostHog discards the client IP at ingestion and the exported `ip` is empty. Task 4.2 still checks the rows.
- Impersonation needs three things. The service account's description must contain `posthog:019e7b58-75ff-0000-79de-62f6f9ec2075` (the PostHog organization id). PostHog's account `posthog-batch-exports@posthog-external.iam.gserviceaccount.com` needs `roles/iam.serviceAccountTokenCreator` on it. It also needs a role with `iam.serviceAccounts.get` on it; `roles/iam.serviceAccountViewer` grants that.
- Volume. In the 30 days to 2026-10-24, the project recorded 17,420 events, and 16,226 of them (93%) were `perf.*`. Those rows are excluded, so at 1,000 monthly fans the export stays at about 80k rows a month. That is well inside the free 1M. Task 4.3 measures it.

Measured on 2026-10-29 (task 4.3), from `posthog_raw.events` by the JST day each row was ingested:

- On 2026-10-24, 2,660 rows arrived. They include the backfill, so events are now in the table from 2026-08-03 on. `posthog_raw.persons` holds 64 persons.
- From 10-25 to 10-28, 62, 127, 134 and 101 rows arrived each day: about 3,500 rows a month, 0.4% of the free 1M.
- 0 rows are `perf.*`, and 0 rows have an `ip`.

The count is measured with no fans beyond the owner and one tester. The estimate of about 80k rows a month at 1,000 monthly fans stays the bound to watch.

### Data Studio

Reports are made by hand on the mart views with the owner's credentials and listed in `docs/runbooks/analytics-dashboards.md` (name, URL, views used). They are the one manual part (openspec/config.yaml `rules.tasks`): Data Studio has no API to create or edit a report, and its Linking API only opens a copy of an existing one. Everything a report reads, the views, is in Pulumi. Built on 2026-10-24: Gemini cost, Unit economics, Campaign value, Infrastructure cost and Pipeline health, listed with their URLs in the runbook (cloud-provisioning#699). Task 5.1's check passed for September 2026: `mart_gemini_cost_daily` sums to 6,424.88 JPY, the same as the raw billing export by JST day and for `invoice.month = 202609`. Conversational Analytics is used on the same views; it bills BigQuery compute only.

## Risks / Trade-offs

- [The analytics bucket cannot be created in asia-northeast1, or its link cannot join with `billing_export`] → checked on the real bucket right after it is created (task 3.2), before the views are built on it; fallback is the direct BigQuery sink.
- [The labels are not promoted on GKE] → checked first (task 1.1); fallback is the payload keys.
- [PostHog export rows exceed the free 1M a month] → `perf.*` (93% of today's events) is excluded by name, and the rest is about 80k a month at 1,000 fans. Task 4.3 checks the exported row count. A `perf.*` name missing from the list is the likely cause of a jump.
- [The `exclude_events` key for BigQuery is not in PostHog's typed API schema, only in its runtime inputs] → task 4.2 checks that no `perf.*` row arrives. If PostHog drops the key, the staging view filters `perf.*` instead.
- [Views get slow as data grows] → move the slow mart to a scheduled query or Dataform then; nothing in Data Studio changes, because the view name stays.

## Migration Plan

1. backend: the helper and the marked lines (task 1.1 needs one marked line in prod).
2. cloud-provisioning, first PR: datasets, service account and its IAM, bucket, sink, link, and the PostHog export runbook (tasks 3.1, 3.2). The user runs the prod `pulumi up` from Pulumi Cloud.
3. PostHog export (task 4.1), which creates `posthog_raw.events` and `posthog_raw.persons` on its first run.
4. cloud-provisioning, second PR: the staging and mart views (task 3.3). This is the one exception to the rule of one PR per repository (cloud-provisioning `AGENTS.md`, "Every PR must cite its change"). BigQuery refuses to create a view over a table that does not exist yet, and the PostHog tables appear only after step 3. The alternative was to pre-create those tables in Pulumi with PostHog's schema; it was rejected because it copies a schema PostHog owns and may add fields to.
5. Data Studio reports.
Rollback: delete the sink to stop routing; the datasets can stay.
