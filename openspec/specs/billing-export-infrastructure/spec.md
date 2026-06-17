# Billing Export Infrastructure

## Purpose

Provisions a Pulumi-managed BigQuery dataset and the IAM bindings that allow GCP Billing Export (Standard, Detailed, and Pricing) to land in BigQuery for the `liverty-music-prod` project. This is the permanent foundation for per-SKU cost analysis, enabling operators to attribute spend to specific services and resources via SQL. The dataset and its permissions are managed as code so they survive drift and can be recreated on demand.

## Requirements

### Requirement: BigQuery dataset for GCP Billing Export
The system SHALL provision a BigQuery dataset named `billing_export` in the `liverty-music-prod` GCP project to receive GCP Billing Export data for cost analysis.

#### Scenario: Dataset exists and is queryable
- **WHEN** Pulumi applies the prod stack
- **THEN** a BigQuery dataset `billing_export` SHALL exist in project `liverty-music-prod`
- **AND** the dataset SHALL be located in `asia-northeast1`
- **AND** the dataset SHALL have a description indicating its purpose as billing export sink

#### Scenario: Dataset is managed by Pulumi
- **WHEN** an operator drifts the dataset (e.g., deletes via Console)
- **THEN** the next `pulumi preview` SHALL detect the drift
- **AND** `pulumi up` SHALL recreate the dataset

---

### Requirement: IAM binding for billing export service account
The system SHALL grant the GCP billing export service account write permissions on the `billing_export` dataset so that Standard, Detailed, and Pricing exports can land in BigQuery without manual permission grants.

#### Scenario: Billing export service account can write to dataset
- **WHEN** Pulumi applies the prod stack
- **THEN** the billing export service account SHALL have `roles/bigquery.dataEditor` on the `billing_export` dataset
- **AND** the service account principal SHALL match the form documented by GCP (e.g., `cloud-billing-export@system.gserviceaccount.com` or the project's billing service agent)

#### Scenario: Permission survives drift
- **WHEN** the IAM binding is removed manually
- **THEN** `pulumi preview` SHALL detect the missing binding
- **AND** `pulumi up` SHALL re-create it

---

### Requirement: Runbook documents the Console step to enable billing export
The system SHALL document the Console-side enablement of billing export to the provisioned dataset, since the export configuration itself is not Pulumi-managed.

#### Scenario: Runbook lists all required Console steps
- **WHEN** an operator follows the runbook for the first time
- **THEN** the runbook SHALL specify navigation to `Billing → Billing export → BigQuery export`
- **AND** the runbook SHALL instruct enabling Standard usage cost export to project `liverty-music-prod` dataset `billing_export`
- **AND** the runbook SHALL instruct enabling Detailed usage cost export to the same dataset
- **AND** the runbook SHALL document the verification step (`bq ls liverty-music-prod:billing_export` 24 hours later) confirming table creation

#### Scenario: Operator can recover from misconfiguration
- **WHEN** the runbook verification step fails (no tables after 24 hours)
- **THEN** the runbook SHALL provide troubleshooting steps for IAM permission verification
- **AND** the runbook SHALL link to GCP's official billing export documentation for current service account naming

---

### Requirement: Detailed usage cost export is preferred over Standard-only
The system SHALL enable Detailed usage cost export (resource-level granularity) in addition to Standard usage cost export.

#### Scenario: Detailed export provides per-resource breakdown
- **WHEN** a cost spike investigation requires per-pod or per-namespace attribution
- **THEN** the Detailed usage cost export tables SHALL be queryable with resource labels intact
- **AND** the operator SHALL be able to attribute costs to specific resources via SQL

---

### Requirement: Sample analysis SQL is provided
The system SHALL ship example SQL queries against the billing export tables for common cost analysis scenarios.

#### Scenario: Example daily SKU breakdown query exists
- **WHEN** an operator wants to investigate a daily cost spike
- **THEN** an example SQL query SHALL be available (in runbook or repository docs)
- **AND** the example SHALL show daily SUM(cost) grouped by service and SKU
