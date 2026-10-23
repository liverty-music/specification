## 1. Checks before building (prod, read-only or one log line)

- [ ] 1.1 Add `logging.AnalyticsLabels(topic)` in the backend, use it on the concert discovery job summary (`cmd/job/concert-discovery/main.go:111`), release, and after the next run confirm with `gcloud --configuration=liverty-music logging read 'labels.sink="analytics"'` that the entry has the labels `sink` and `topic`; if not, switch the helper to payload keys and record it in design.md
- [ ] 1.2 Create a test log bucket with analytics enabled in asia-northeast1 and a linked dataset by hand, run one query that joins it with `billing_export`, then delete both; record the result in design.md and switch to the fallback sink if either step fails

## 2. Backend marked lines (backend, components/infrastructure/backend/process/structured-logging)

- [ ] 2.1 Mark the job summaries of every job (`cmd/job/*/main.go`), notification delivery (`notification_delivery.go:111`, `ticket_sale_reminder_delivery_uc.go:91`, `notification_new_concerts.go`), catalog review (`concert_candidate_uc.go`), catalog sync (`official_site_refresh_uc.go`, `artist_image_sync_uc.go`) and payments (`order_refund_uc.go:190`, `settlement_uc.go:217`, `lottery_entry_uc.go:480`), with no fan email, name, phone or address on a marked line; tests annotated `// @spec components/infrastructure/backend/process/structured-logging "<scenario>"` for "Job summary", "New topic" and "Line with personal data", checking the written JSON
- [ ] 2.2 Check in PostHog's export settings whether the BigQuery export can exclude events, and record the answer in design.md

## 3. Warehouse resources (cloud-provisioning)

- [ ] 3.1 Add the prod-only `AnalyticsWarehouseComponent`: datasets `posthog_raw`, `analytics_staging`, `analytics_marts` in asia-northeast1; the service account `posthog-export` with `roles/bigquery.jobUser` on the project and `roles/bigquery.dataEditor` on `posthog_raw` only, and the impersonation grant for PostHog's service account; verify `pulumi preview -s prod` lists only these additions
- [ ] 3.2 Add the analytics log bucket (400 days, analytics on), the sink with the filter from task 1.1, and the linked dataset `logs_analytics`; verify the preview, and after the user's `pulumi up`, that a marked line appears in `logs_analytics._AllLogs`
- [ ] 3.3 Add the staging views and the six mart views from design.md as `bigquery.Table` views with SQL files under `src/gcp/analytics/sql/`; verify each view with `bq query --dry_run` in the preview workflow and, after the export runs, one real query per mart

## 4. PostHog export (PostHog project 190464, by hand)

- [ ] 4.1 Create the BigQuery batch export for events and persons, hourly, by impersonation, without `ip` (and without `perf.*` if task 2.2 allows); write `docs/runbooks/posthog-bigquery-export.md`
- [ ] 4.2 Confirm the first hourly run wrote rows into `posthog_raw.events` and that no row has an `ip` value
- [ ] 4.3 After one week, confirm the exported row count is on track to stay under 1M a month

## 5. Dashboards (Data Studio, by hand)

- [ ] 5.1 Build the reports on the mart views (unit economics, Gemini cost, infrastructure cost, campaign value, pipeline health) and list them in `docs/runbooks/analytics-dashboards.md`; confirm `mart_gemini_cost_daily` totals equal the billing export for one month
- [ ] 5.2 Build the North Star insight in PostHog (fans who opened a new_concerts notification per week) and link it from the same runbook
