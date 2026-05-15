## MODIFIED Requirements

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
