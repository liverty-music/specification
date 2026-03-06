## Why

Both frontend and backend integrate the OpenTelemetry SDK and generate trace data, but no collector or viewer is deployed. Traces are created and discarded because `TELEMETRY_OTLP_ENDPOINT` (backend) and `VITE_OTEL_EXPORTER_URL` (frontend) are unset. Without trace visibility, debugging distributed request flows across the frontend-backend boundary is done entirely through log inspection.

## What Changes

- Deploy an OpenTelemetry Collector as a Kubernetes Deployment in GKE, configured to receive OTLP traces and export them to Google Cloud Trace via the `googlecloud` exporter.
- Configure the backend to send traces to the in-cluster OTel Collector via `TELEMETRY_OTLP_ENDPOINT`.
- **Simplify frontend observability**: Remove the OTLP/HTTP span exporter (`OTLPTraceExporter`, `BatchSpanProcessor`) and related dependencies. The frontend only needs to generate `traceparent` headers for backend request correlation — it does not need to export its own spans.
- Retain the Connect-RPC tracing interceptor and `OtelLogSink` (they operate on the local tracer provider and remain useful for in-browser diagnostics).
- Set up Workload Identity for the OTel Collector so it can authenticate to Cloud Trace without service account keys.

## Capabilities

### New Capabilities

- `otel-collector-deployment`: Defines the OTel Collector Kubernetes deployment, configuration, service account, and Workload Identity binding for exporting traces to Cloud Trace.

### Modified Capabilities

- `frontend-observability`: Remove the OTLP/HTTP export requirement. The frontend SHALL generate trace context (`traceparent`) for backend request correlation but SHALL NOT export spans to an external collector.

## Impact

- **cloud-provisioning**: New K8s namespace `otel-collector` with Kustomize base/overlay, ArgoCD Application, Workload Identity IAM binding via Pulumi.
- **backend**: Set `TELEMETRY_OTLP_ENDPOINT` environment variable in the backend Deployment manifests pointing to the in-cluster Collector service.
- **frontend**: Remove `@opentelemetry/exporter-trace-otlp-http` dependency and `BatchSpanProcessor` initialization. `VITE_OTEL_EXPORTER_URL` is no longer needed.
- **GCP**: Cloud Trace API is already enabled. Workload Identity binding for the Collector service account is required.
