## Context

The backend and frontend both integrate the OpenTelemetry SDK and generate trace data. However, no collector or trace viewer is configured, so traces are created and immediately discarded. The backend uses `otlptracehttp` to export spans when `TELEMETRY_OTLP_ENDPOINT` is set (currently empty). The frontend initializes a `WebTracerProvider` with `OTLPTraceExporter` when `VITE_OTEL_EXPORTER_URL` is set (currently empty).

The GCP project already has `cloudtrace.googleapis.com` enabled, and the `backend-app` GCP service account already has `roles/cloudtrace.agent` bound. The infrastructure uses GKE Autopilot with ArgoCD (App of Apps pattern), Kustomize base/overlays, and Workload Identity for GCP authentication.

## Goals / Non-Goals

**Goals:**
- Deploy an OTel Collector to GKE that receives OTLP traces from the backend and exports them to Cloud Trace.
- Make backend traces visible in the GCP Console (Cloud Trace).
- Simplify the frontend by removing OTLP export while retaining `traceparent` propagation for distributed trace correlation.

**Non-Goals:**
- Metrics or logs collection via the OTel Collector (traces only for now).
- Tail-based sampling (use head-based `AlwaysSample` at the current traffic scale).
- Frontend span export to Cloud Trace.
- Self-hosted trace viewer (Jaeger, Tempo, etc.) — Cloud Trace is the viewer.

## Decisions

### 1. Viewer: Cloud Trace

**Decision**: Use Google Cloud Trace as the trace viewer.

**Rationale**: The GCP API is already enabled, the backend SA already has `cloudtrace.agent` role, and Cloud Trace provides 2.5M spans/month free tier. No additional infrastructure to host or maintain. Integrates with existing Cloud Logging and Cloud Monitoring alert policies.

**Alternatives considered**:
- **Jaeger**: Requires hosting in GKE (additional resource cost and maintenance). Better UI for dependency graphs, but overkill for current needs.
- **Grafana Tempo + Grafana**: Powerful TraceQL and unified observability, but requires deploying both Tempo and Grafana. Premature — no Prometheus/Grafana stack exists yet.
- **SigNoz Cloud**: SaaS cost ($199/mo+) not justified at this stage.

### 2. Collector Deployment Mode: Deployment (not DaemonSet)

**Decision**: Deploy the OTel Collector as a single-replica Kubernetes `Deployment` in a dedicated `otel-collector` namespace.

**Rationale**: GKE Autopilot has restrictions on DaemonSets (requires specific resource class annotations, cannot use `hostNetwork`). A Deployment is simpler and sufficient for the current traffic volume. The Collector processes traces in-memory with a `batch` processor — no persistent state required.

**Scaling**: If throughput grows, add HPA based on CPU/memory. If per-node collection is needed later (e.g., for host metrics), switch to DaemonSet.

### 3. Collector Distribution: `otel/opentelemetry-collector-contrib`

**Decision**: Use the `contrib` distribution of the OTel Collector.

**Rationale**: The `googlecloud` exporter is only available in the `contrib` distribution, not in the core distribution.

### 4. Frontend: Remove OTLP Export, Keep traceparent

**Decision**: Remove `OTLPTraceExporter`, `BatchSpanProcessor`, and the `@opentelemetry/exporter-trace-otlp-http` dependency from the frontend. Keep `WebTracerProvider` (without exporter) and `FetchInstrumentation` for `traceparent` header generation.

**Rationale**: The frontend only needs to generate trace context headers for backend request correlation. Exporting browser spans adds complexity (CORS, Collector public exposure) with minimal value — backend spans are sufficient for debugging API flows.

**What is retained**:
- `WebTracerProvider` (registered without span processors that export)
- `FetchInstrumentation` (injects `traceparent` into API requests)
- `OtelLogSink` (local span creation for error diagnostics — no export needed)
- Connect-RPC tracing interceptor

### 5. Workload Identity: Dedicated GCP SA for OTel Collector

**Decision**: Create a dedicated GCP service account `otel-collector` with `roles/cloudtrace.agent`, bound to the K8s SA `otel-collector` in namespace `otel-collector` via Workload Identity.

**Rationale**: Follows the existing pattern (e.g., `backend-app` SA, `k8s-external-secrets` SA). Principle of least privilege — the Collector only needs trace write access, not the broader permissions of `backend-app`.

### 6. OTel Collector Pipeline Configuration

**Decision**: Minimal pipeline — `otlp` receiver → `batch` processor → `googlecloud` exporter.

```yaml
receivers:
  otlp:
    protocols:
      http:
        endpoint: 0.0.0.0:4318
      grpc:
        endpoint: 0.0.0.0:4317

processors:
  batch:
    timeout: 5s
    send_batch_size: 512

exporters:
  googlecloud: {}

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [googlecloud]
```

**Rationale**: Simplest working configuration. The `batch` processor improves throughput by buffering spans before export. No sampling processor needed — `AlwaysSample` at the SDK level is fine at current scale.

## Risks / Trade-offs

- **Single point of failure**: One Collector replica means trace loss during restarts or OOM. → Acceptable for dev/staging. For prod, add a second replica or HPA.
- **Backend-only traces in Cloud Trace**: Without frontend span export, Cloud Trace shows only backend spans. Frontend-to-backend latency is not directly measurable. → Acceptable trade-off — backend spans include the full RPC processing time, which is the primary debugging need.
- **GKE Autopilot resource costs**: The Collector pod adds resource cost. → Mitigate with tight resource requests/limits and Spot VM nodeSelector (consistent with dev cost optimization policy).
