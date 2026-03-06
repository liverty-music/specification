# OTel Collector Deployment

## Purpose

Defines the OpenTelemetry Collector deployment on GKE for receiving OTLP traces from backend services and exporting them to Google Cloud Trace.

## ADDED Requirements

### Requirement: OTel Collector Kubernetes Deployment
The system SHALL deploy an OpenTelemetry Collector as a Kubernetes Deployment in a dedicated `otel-collector` namespace, configured to receive traces via OTLP and export them to Cloud Trace.

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
