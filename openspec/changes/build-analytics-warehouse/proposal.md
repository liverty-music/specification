## Why

The team wants one place to answer questions that need more than one source: what a discovered concert costs (Gemini billing × search outcomes), what a retained fan costs (all billing × PostHog activity), which campaign brings fans who stay, and how the scheduled jobs and notification delivery perform over months. Today each answer is rebuilt by hand from a 30-day log bucket, the billing export and PostHog, as was done on 2026-10-22 to price a new concert (about 19 JPY at list price).

The billing export already lands in BigQuery (`billing_export`, asia-northeast1). PostHog and the backend logs do not: the prod `_Default` log bucket keeps 30 days, and no PostHog export is set up. This change brings both next to the billing export, shapes them into a few tables, and puts the dashboards in Data Studio (formerly Looker Studio). `expand-product-analytics` defines what PostHog receives; this change moves it.

## What Changes

- **Location**: every analytics dataset is in asia-northeast1 (Tokyo), next to `billing_export`, because BigQuery joins only within one location and the billing dataset cannot move. Osaka also lacks BigQuery Studio notebooks and remote models.
- **PostHog → BigQuery**: a PostHog batch export writes `events` and `persons` hourly into `posthog_raw`, through service-account impersonation (no key), without the `ip` column.
- **Backend logs → BigQuery**: a backend log line meant for analytics carries one mark (`sink=analytics`) and a topic. One Log Router sink with the filter on that mark routes the lines to a Tokyo log bucket with 400 days of retention, upgraded to Observability Analytics and linked to BigQuery as `logs_analytics`. A new topic needs no sink change. The first topics: job results, notification delivery, catalog review, catalog sync and payments. Gemini calls are not marked: they reach BigQuery through PostHog.
- **Shaping**: staging and mart views in `analytics_staging` and `analytics_marts`, defined in Pulumi as BigQuery views. Dataform was planned, but it needs its `workflow_settings.yaml` at a repository root, which would mean a new repository for 6 views.
- **Dashboards in Data Studio** (by hand, recorded in a runbook): unit economics (cost per new concert and per retained fan), Gemini cost by process, infrastructure cost by GKE namespace, value by campaign, pipeline and delivery health, and long-term fan activity. Conversational Analytics, available to every Data Studio user since 2026-04-16, answers ad-hoc questions on the marts.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/infrastructure/backend/process/structured-logging`: a log line meant for analytics carries the analytics mark and its topic.

## Impact

- **backend**: one helper that adds the mark, used on the log lines of the first topics (`cmd/job/*/main.go` job summaries; `usecase/notification_delivery.go:111`, `ticket_sale_reminder_delivery_uc.go:91`, `notification_new_concerts.go`; `concert_candidate_uc.go`; `official_site_refresh_uc.go`, `artist_image_sync_uc.go`; `order_refund_uc.go:190`, `settlement_uc.go:217`, `lottery_entry_uc.go:480`).
- **cloud-provisioning**: datasets, the PostHog export service account and its IAM, the log bucket, sink and link, the views, and runbooks for the PostHog export and the Data Studio reports. Prod only, like `billing_export`.
- **PostHog project 190464**: the batch export (by hand).
- **Cost**: about 0 JPY a month at 1,000 monthly fans (BigQuery storage under 10 GiB and queries under 1 TiB a month are free; the analytics log lines are about 25 MB a month inside Logging's 50 GiB).
