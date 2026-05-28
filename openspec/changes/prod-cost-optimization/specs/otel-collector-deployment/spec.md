## MODIFIED Requirements

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

## ADDED Requirements

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
