## 1. Checks before building (prod, read-only or one log line)

- [x] 1.1 Add `analyticslog.Attrs(topic, attrs...)` (`backend/pkg/analyticslog`) in the backend, use it on the concert discovery job summary (`cmd/job/concert-discovery/main.go:111`), release, and after the next run confirm with `gcloud --configuration=liverty-music logging read 'labels.sink="analytics"'` that the entry has the labels `sink` and `topic`; if not, switch the helper to payload keys and record it in design.md

## 2. Backend marked lines (backend, components/infrastructure/backend/process/structured-logging)

- [x] 2.1 Mark the job summaries of every job (`cmd/job/*/main.go`), notification delivery (`notification_delivery.go:111`, `ticket_sale_reminder_delivery_uc.go:91`, `notification_new_concerts.go`), catalog review (`concert_candidate_uc.go`), catalog sync (`official_site_refresh_uc.go`, `artist_image_sync_uc.go`) and payments (`order_refund_uc.go:190`, `settlement_uc.go:217`, `lottery_entry_uc.go:480`), with no fan email, name, phone or address on a marked line; tests annotated `// @spec components/infrastructure/backend/process/structured-logging "<scenario>"` for "Job summary", "New topic" and "Line with personal data", checking the written JSON
- [x] 2.2 Check in PostHog's export settings whether the BigQuery export can exclude events, and record the answer in design.md
- [x] 2.3 Report how far each run got in the job summaries of concert discovery, sales-phase discovery and artist image sync (`cmd/job/{concert-discovery,sales-phase-discovery,artist-image-sync}/main.go`): count the items processed, compute succeeded as processed minus failed, and add `circuit_broken` (official site refresh already has it); tests annotated `// @spec components/infrastructure/backend/process/structured-logging "<scenario>"` for "Run stops after consecutive failures" and "Run reaches every item"; after release, confirm in `mart_pipeline_health_daily` that a run that stops early shows `circuit_broken` 1

## 3. Warehouse resources (cloud-provisioning)

- [x] 3.1 Add the prod-only `AnalyticsWarehouseComponent`: datasets `posthog_raw`, `analytics_staging`, `analytics_marts` in asia-northeast1; the service account `posthog-export` with `roles/bigquery.jobUser` on the project and `roles/bigquery.dataEditor` on `posthog_raw` only, and the impersonation grant for PostHog's service account; verify `pulumi preview -s prod` lists only these additions
- [x] 3.2 Add the analytics log bucket (400 days, analytics on), the sink with the filter from task 1.1, and the linked dataset `logs_analytics`; verify the preview, and after the user's `pulumi up`, that a marked line appears in `logs_analytics._AllLogs`, and run one query that joins `logs_analytics._AllLogs` with `billing_export`; record the result in design.md, and if the bucket cannot be created in asia-northeast1 or the join fails, replace the bucket and link with the fallback sink
- [x] 3.3 Add the staging views and the six mart views from design.md as `bigquery.Table` views with SQL files under `src/gcp/analytics/sql/`; verify each view with `bq query --dry_run` in the preview workflow and, after the export runs, one real query per mart
- [x] 3.4 Add `project_id` to `stg_billing_daily` and `stg_billing_resource_daily`, keep only `liverty-music-prod` in `mart_gemini_cost_daily`, `mart_cost_per_concert_monthly` and `mart_unit_economics_monthly`, and keep `project_id` as a dimension in `mart_infra_cost_daily`; verify the prod preview and, after the user's `pulumi up`, that `mart_gemini_cost_daily` for August 2026 equals the billing export's Gemini API cost for `liverty-music-prod` alone by JST day (August has 1,230 JPY of dev Gemini cost, so a mart that still mixes projects fails the check)

## 4. PostHog export (cloud-provisioning, PostHog project 190464)

- [x] 4.1 Add the BigQuery batch exports for events and persons in Pulumi: hourly, by impersonation through the `google-cloud-service-account` integration the user makes once in PostHog's UI (looked up by service account email), `perf.*` excluded; write `docs/runbooks/posthog-bigquery-export.md`; after the user adds `integration:read` and `batch_export:write` to the management key, creates the integration and runs `pulumi up`, verify that both exports exist in PostHog
- [x] 4.2 Confirm the first hourly run wrote rows into `posthog_raw.events`, and that no row has an `ip` value or a `perf.*` event
- [x] 4.3 After one week, confirm the exported row count is on track to stay under 1M a month

## 5. Dashboards (Data Studio, by hand)

- [x] 5.1 Build the reports on the mart views (unit economics, Gemini cost, infrastructure cost, campaign value, pipeline health) and list them in `docs/runbooks/analytics-dashboards.md`; confirm `mart_gemini_cost_daily` totals equal the billing export for one month
- [x] 5.2 Add the North Star insight (fans who opened a new_concerts notification per week) as a `posthog.Insight` in cloud-provisioning, and link it from the same runbook; verify the prod preview and, after the user's `pulumi up`, that the insight exists in PostHog
