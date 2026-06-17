# OTel Collector Deployment

## Purpose

Defines the OpenTelemetry Collector deployment on GKE for receiving OTLP traces from backend services and exporting them to Google Cloud Trace.

## Requirements

### Requirement: OTel Collector Kubernetes Deployment
The system SHALL deploy an OpenTelemetry Collector as a Kubernetes Deployment in a dedicated `otel-collector` namespace, configured to receive both traces and metrics via OTLP and export them to Google Cloud Trace (traces) and Google Cloud Monitoring (metrics). The metrics pipeline SHALL include a `filter` processor that drops low-value, high-volume metric series to keep Cloud Monitoring metric ingest within the GCP free tier (150 MiB / billing account / month) under normal traffic.

#### Scenario: Collector receives OTLP traces over HTTP
- **WHEN** a backend service sends traces to the Collector's OTLP/HTTP endpoint
- **THEN** the Collector SHALL accept the traces on port 4318
- **AND** the Collector SHALL process them through the `batch` processor
- **AND** the Collector SHALL export the traces to Google Cloud Trace via the `googlecloud` exporter

#### Scenario: Collector receives OTLP traces over gRPC
- **WHEN** a backend service sends traces to the Collector's OTLP/gRPC endpoint
- **THEN** the Collector SHALL accept the traces on port 4317

#### Scenario: Collector is reachable via in-cluster service
- **WHEN** a backend pod needs to send traces
- **THEN** a Kubernetes Service `otel-collector` in namespace `otel-collector` SHALL be available
- **AND** the service SHALL expose ports 4317 (gRPC) and 4318 (HTTP)

#### Scenario: Metrics pipeline drops noisy auto-generated metrics
- **WHEN** the Collector receives OTLP metrics whose name matches `rpc.server.*` or `http.client.*`
- **THEN** the `filter` processor SHALL drop those metrics before the `batch` processor
- **AND** the metrics SHALL NOT be exported to Cloud Monitoring

#### Scenario: Business-relevant metrics pass through
- **WHEN** the Collector receives OTLP metrics named `concert.search.count`, `db.pool.active_connections`, or `db.pool.idle_connections`
- **THEN** the `filter` processor SHALL NOT drop them
- **AND** the metrics SHALL be exported to Cloud Monitoring via the `googlecloud` exporter under the `workload.googleapis.com/` domain

#### Scenario: Filter ordering minimizes batch overhead
- **WHEN** metrics flow through the pipeline
- **THEN** the `filter` processor SHALL be configured before `batch` in the processor chain
- **AND** dropped metrics SHALL NOT contribute to batch payload size

---

### Requirement: Workload Identity for Cloud Trace Authentication
The system SHALL use GKE Workload Identity to authenticate the OTel Collector to Cloud Trace without service account keys.

#### Scenario: Collector authenticates via Workload Identity
- **WHEN** the Collector pod starts
- **THEN** the pod SHALL use the Kubernetes service account `otel-collector`
- **AND** the K8s SA SHALL be annotated with the GCP service account email
- **AND** the GCP SA SHALL have `roles/cloudtrace.agent` bound
- **AND** the GCP SA SHALL have Workload Identity binding for the `otel-collector` namespace

---

### Requirement: Backend Trace Export Configuration
The system SHALL configure backend deployments to send traces to the in-cluster OTel Collector.

#### Scenario: Backend server sends traces to OTel Collector
- **WHEN** the backend server deployment starts in a cluster with the OTel Collector deployed
- **THEN** the `TELEMETRY_OTLP_ENDPOINT` environment variable SHALL be set to `otel-collector.otel-collector.svc.cluster.local:4318`
- **AND** the backend SHALL export traces via OTLP/HTTP to this endpoint

#### Scenario: Backend consumer sends traces to OTel Collector
- **WHEN** the backend consumer deployment starts in a cluster with the OTel Collector deployed
- **THEN** the `TELEMETRY_OTLP_ENDPOINT` environment variable SHALL be set to the same Collector endpoint as the server

#### Scenario: Backend concert-discovery CronJob sends traces to OTel Collector
- **WHEN** the concert-discovery CronJob runs in a cluster with the OTel Collector deployed
- **THEN** the `TELEMETRY_OTLP_ENDPOINT` environment variable SHALL be set to the same Collector endpoint as the server

---

### Requirement: Cost-Optimized Resource Configuration
The Collector deployment SHALL follow the dev cost optimization policy for GKE Autopilot.

#### Scenario: Collector uses Spot VMs and minimal resources
- **WHEN** the Collector is deployed in the dev environment
- **THEN** the pod SHALL have `nodeSelector: cloud.google.com/compute-class: autopilot-spot`
- **AND** the container SHALL have explicit CPU and memory resource requests and limits

---

### Requirement: ArgoCD GitOps Management
The Collector deployment SHALL be managed by ArgoCD following the App of Apps pattern.

#### Scenario: ArgoCD Application for OTel Collector
- **WHEN** the cloud-provisioning repository contains the OTel Collector manifests
- **THEN** an ArgoCD Application `otel-collector` SHALL exist in namespace `argocd`
- **AND** the Application SHALL point to `k8s/namespaces/otel-collector/overlays/dev`
- **AND** the Application SHALL have automated sync with prune and self-heal enabled

---

### Requirement: Filter rule scope is documented in the ConfigMap
The Collector ConfigMap SHALL contain a comment explaining the filter rule's intent so future operators can extend, relax, or revert the policy with full context.

#### Scenario: ConfigMap comment explains drop rules
- **WHEN** an operator reads `k8s/namespaces/otel-collector/base/configmap.yaml`
- **THEN** there SHALL be a comment block above the `filter` processor explaining why `rpc.server.*` and `http.client.*` are dropped
- **AND** the comment SHALL reference the billing account 150 MiB free tier constraint
- **AND** the comment SHALL list the metrics that are explicitly retained

---

### Requirement: Metric ingest volume is observable
The system SHALL allow operators to verify the effectiveness of the filter via the `monitoring.googleapis.com/billing/bytes_ingested` metric in Cloud Monitoring.

#### Scenario: Operator can compare ingest volume before and after filter
- **WHEN** an operator queries `monitoring.googleapis.com/billing/bytes_ingested` for the prod project
- **THEN** the time series SHALL show a step decrease at the moment the filter is deployed
- **AND** the post-filter daily ingest SHALL be less than 1 MiB/day under normal traffic
