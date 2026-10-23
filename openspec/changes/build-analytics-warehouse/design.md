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

- Alternative: a sink straight to BigQuery with partitioned tables. Kept as the fallback if task 1.2 finds that an analytics bucket cannot be made in asia-northeast1 or cannot be joined with `billing_export`.

### The mark is a log entry label

The backend adds `slog.Group("logging.googleapis.com/labels", slog.String("sink", "analytics"), slog.String("topic", topic))` through one helper, `logging.AnalyticsLabels(topic)`. The GKE logging agent turns the `logging.googleapis.com/labels` object into LogEntry labels, which is what Cloud Logging's structured-logging special fields describe; GKE's own docs do not state it, so task 1.1 checks it with one line in prod before anything is built on it. If it fails, the helper writes `sink` and `topic` as plain payload keys and the filter becomes `jsonPayload.sink="analytics"`.

### Views in Pulumi instead of Dataform

Staging and mart views are `bigquery.Table` resources with `view.query` read from `.sql` files under `cloud-provisioning/src/gcp/analytics/sql/`, so they are reviewed in pull requests with the rest of the infrastructure. Dataform would need its own repository (its config must sit at a repository root) and a Git connection for about 6 views. Views cost nothing to keep; at 1,000 monthly fans a mart query scans well under 1 GiB. When a mart needs materialization or tests, Dataform in its own repository is the next step.

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

The North Star (fans who opened a new-concert notification in the week) is a PostHog insight, not a mart.

### PostHog export settings

Events and persons, hourly, impersonating the service account `posthog-export@liverty-music-prod`, with `ip` left out and `perf.*` excluded if the BigQuery export offers the filter (task 2.2 checks); otherwise the staging view drops them. Set by hand in PostHog (the MCP connection lacks `batch_export:write`) and recorded in `docs/runbooks/posthog-bigquery-export.md`.

### Data Studio

Reports are made by hand on the mart views with the owner's credentials and listed in `docs/runbooks/analytics-dashboards.md` (name, URL, views used). Conversational Analytics is used on the same views; it bills BigQuery compute only.

## Risks / Trade-offs

- [The analytics bucket cannot be created in asia-northeast1, or its link cannot join with `billing_export`] → checked first (task 1.2); fallback is the direct BigQuery sink.
- [The labels are not promoted on GKE] → checked first (task 1.1); fallback is the payload keys.
- [PostHog export rows exceed the free 1M a month] → at 1,000 fans the non-performance events are about 80k a month; the exported row count is checked in task 4.3.
- [Views get slow as data grows] → move the slow mart to a scheduled query or Dataform then; nothing in Data Studio changes, because the view name stays.

## Migration Plan

1. backend: the helper and the marked lines (task 1.1 needs one marked line in prod).
2. cloud-provisioning: datasets, service account, bucket, sink, link, views; prod `pulumi up` is run by the user from Pulumi Cloud.
3. PostHog export, then Data Studio reports.
Rollback: delete the sink to stop routing; the datasets can stay.
