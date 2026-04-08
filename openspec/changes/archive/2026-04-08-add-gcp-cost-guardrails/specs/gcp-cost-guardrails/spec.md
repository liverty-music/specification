## ADDED Requirements

### Requirement: Dev Project Billing Budget Alert
The `liverty-music-dev` GCP project SHALL have a Cloud Billing Budget configured with a monthly threshold of ¥3,000 (approx. $20 USD). The system SHALL send email notifications to the project billing contact when accumulated spend reaches 50%, 90%, and 100% of the monthly budget.

#### Scenario: Budget threshold reached
- **WHEN** the dev project's monthly spend reaches 50%, 90%, or 100% of the configured budget
- **THEN** an email alert is sent to the billing contact address

#### Scenario: Budget is IaC-managed
- **WHEN** the cloud-provisioning Pulumi stack is deployed
- **THEN** the billing budget exists as a Pulumi-managed resource and is visible in GCP Console under Billing → Budgets & Alerts

### Requirement: Places API Daily Quota Limit (Dev)
The `liverty-music-dev` GCP project SHALL have a consumer quota override limiting Places API (New) Text Search requests to **20 requests per day**. This limit SHALL be managed as a Pulumi resource and SHALL only apply to the dev environment.

#### Scenario: Quota limit blocks excess requests
- **WHEN** Places API (New) Text Search has been called 20 times within a calendar day on the dev project
- **THEN** subsequent calls return HTTP 429 (RESOURCE_EXHAUSTED), which the backend maps to `codes.ResourceExhausted` and treats as a non-retryable error for venue resolution, skipping that venue

#### Scenario: Quota is IaC-managed and dev-only
- **WHEN** the cloud-provisioning Pulumi stack is deployed for the dev environment
- **THEN** a `ConsumerQuotaOverride` resource exists for `places.googleapis.com` and no equivalent override exists in the prod stack

### Requirement: Vertex AI Daily Quota Limit (Dev)
The `liverty-music-dev` GCP project SHALL have a consumer quota override limiting Vertex AI Gemini `GenerateContent` requests to **5 requests per minute** (effectively throttling runaway loops while allowing normal weekly CronJob execution). This limit SHALL be managed as a Pulumi resource and SHALL only apply to the dev environment.

#### Scenario: Quota throttles runaway loop
- **WHEN** a bug causes the concert-discovery CronJob to call Vertex AI in a tight loop exceeding 5 req/min
- **THEN** requests beyond the quota return HTTP 429, which `gemini/errors.go` maps to `codes.ResourceExhausted` and `isRetryable` returns `true`, triggering exponential backoff (max 3 retries), after which the artist's search gracefully returns nil

#### Scenario: Normal CronJob completes within quota
- **WHEN** the concert-discovery CronJob runs normally (1 Gemini call per artist with ~1s throttle between calls)
- **THEN** all artists are processed successfully, as the 1 req/s rate is well within the 5 req/min quota

#### Scenario: Quota is IaC-managed and dev-only
- **WHEN** the cloud-provisioning Pulumi stack is deployed for the dev environment
- **THEN** a `ConsumerQuotaOverride` resource exists for `aiplatform.googleapis.com` and no equivalent override exists in the prod stack
