# GCP Cost Guardrails

## Purpose

Defines cost-protection mechanisms for GCP projects in scope (`liverty-music-dev`, `liverty-music-prod`). Billing budget alerts apply per-env via ESC materialization; quota overrides for high-cost APIs (Places API, Vertex AI) are dev-only guardrails that prevent runaway spend in the development environment while allowing normal workloads to operate unimpeded.

## Requirements

### Requirement: Places API Daily Quota Limit (Dev)
The `liverty-music-dev` GCP project SHALL have a consumer quota override limiting Places API (New) Text Search requests to **20 requests per day**. This limit SHALL be managed as a Pulumi resource and SHALL only apply to the dev environment.

#### Scenario: Quota limit blocks excess requests
- **WHEN** Places API (New) Text Search has been called 20 times within a calendar day on the dev project
- **THEN** subsequent calls return HTTP 429 (RESOURCE_EXHAUSTED), which the backend maps to `codes.ResourceExhausted` and treats as a non-retryable error for venue resolution, skipping that venue

#### Scenario: Quota is IaC-managed and dev-only
- **WHEN** the cloud-provisioning Pulumi stack is deployed for the dev environment
- **THEN** a `ConsumerQuotaOverride` resource exists for `places.googleapis.com` and no equivalent override exists in the prod stack

### Requirement: Vertex AI Per-Minute Quota Limit (Dev)
The `liverty-music-dev` GCP project SHALL have a consumer quota override limiting Vertex AI Gemini `GenerateContent` requests to **5 requests per minute** (throttling runaway loops that call Gemini far beyond the expected weekly CronJob frequency). This limit SHALL be managed as a Pulumi resource and SHALL only apply to the dev environment.

#### Scenario: Quota throttles runaway loop
- **WHEN** a bug causes the concert-discovery CronJob to call Vertex AI in a tight loop exceeding 5 req/min
- **THEN** requests beyond the quota return HTTP 429, which `gemini/errors.go` maps to `codes.ResourceExhausted` and `isRetryable` returns `true`, triggering exponential backoff (max 3 retries), after which the artist's search gracefully returns nil

#### Scenario: Normal CronJob is throttled gracefully
- **WHEN** the concert-discovery CronJob runs its normal weekly batch (one Gemini call per followed artist, no sleep between artists)
- **THEN** after the 5th request in a minute the job encounters 429s, backs off, and completes the batch over a longer duration — artists are not permanently skipped, only delayed

#### Scenario: Quota is IaC-managed and dev-only
- **WHEN** the cloud-provisioning Pulumi stack is deployed for the dev environment
- **THEN** a `ConsumerQuotaOverride` resource exists for `aiplatform.googleapis.com` and no equivalent override exists in the prod stack

### Requirement: Project Billing Budget Alert

Each GCP project in scope (`liverty-music-dev`, `liverty-music-prod`) SHALL have a Cloud Billing Budget configured with a monthly threshold sourced from ESC (`gcpConfig.budgetAmountJpy`, default `¥3,000` ≈ `$20 USD` when unset). The system SHALL send email notifications to the project billing contact (sourced from ESC `gcpConfig.billingAlertEmail`) when accumulated spend reaches 50%, 90%, and 100% of the monthly budget. The Pulumi code path is env-agnostic and materializes the budget resource in any env whose ESC seeds `billingAlertEmail`; the dev env retains its ¥3,000 default unless explicitly overridden.

#### Scenario: Dev budget threshold reached

- **WHEN** the dev project's monthly spend reaches 50%, 90%, or 100% of the configured budget
- **THEN** an email alert SHALL be sent to the configured billing contact address

#### Scenario: Prod budget threshold reached

- **WHEN** the prod project's monthly spend reaches 50%, 90%, or 100% of `gcpConfig.budgetAmountJpy`
- **THEN** an email alert SHALL be sent to `gcpConfig.billingAlertEmail` for the prod ESC environment

#### Scenario: Budget is IaC-managed in any seeded env

- **WHEN** the cloud-provisioning Pulumi stack is deployed for an env whose ESC includes `gcpConfig.billingAlertEmail`
- **THEN** a `gcp.billing.Budget` resource named `cost-budget` SHALL exist
- **AND** a `gcp.monitoring.NotificationChannel` named `billing-alert-email` SHALL exist pointing at the seeded email address
- **AND** both SHALL be visible in GCP Console under Billing → Budgets & Alerts

#### Scenario: Unseeded env has no budget

- **WHEN** the cloud-provisioning Pulumi stack is deployed for an env whose ESC does NOT include `gcpConfig.billingAlertEmail`
- **THEN** neither the `cost-budget` nor `billing-alert-email` resource SHALL exist in that stack's state
- **AND** spend SHALL NOT be alerted on (operator's explicit choice to defer)

#### Scenario: Prod budget amount can diverge from dev default

- **WHEN** prod ESC seeds `gcpConfig.budgetAmountJpy` to a value different from `3000`
- **THEN** the prod budget's `specifiedAmount.units` SHALL equal that seeded value
- **AND** the dev budget SHALL retain its existing amount (no cross-env leakage)

