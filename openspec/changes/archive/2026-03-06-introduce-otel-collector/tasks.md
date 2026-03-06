## 1. GCP IAM (Pulumi)

- [x] 1.1 Create GCP service account `otel-collector` with `roles/cloudtrace.agent` in the KubernetesComponent
- [x] 1.2 Bind Workload Identity for K8s SA `otel-collector` in namespace `otel-collector` to the GCP SA

## 2. OTel Collector K8s Manifests

- [x] 2.1 Create `k8s/namespaces/otel-collector/base/` with Kustomization, ServiceAccount (annotated with GCP SA email placeholder), ConfigMap (collector config), Deployment, and Service
- [x] 2.2 Create `k8s/namespaces/otel-collector/overlays/dev/` with Kustomization, GCP SA email patch, resource requests/limits patch, and Spot VM nodeSelector patch
- [x] 2.3 Create ArgoCD Application `otel-collector` at `k8s/argocd-apps/dev/otel-collector.yaml`
- [x] 2.4 Add `otel-collector` namespace to `k8s/init/namespaces.yaml`
- [x] 2.5 Validate manifests with `kubectl kustomize k8s/namespaces/otel-collector/overlays/dev`

## 3. Backend Configuration

- [x] 3.1 Add `TELEMETRY_OTLP_ENDPOINT` env var to backend server Deployment overlay (dev) pointing to `otel-collector.otel-collector.svc.cluster.local:4318`
- [x] 3.2 Add `TELEMETRY_OTLP_ENDPOINT` env var to backend consumer Deployment overlay (dev) pointing to the same endpoint
- [x] 3.3 Add `TELEMETRY_OTLP_ENDPOINT` env var to backend concert-discovery CronJob overlay (dev) pointing to the same endpoint

## 4. Frontend Simplification

- [x] 4.1 Remove `OTLPTraceExporter` and `BatchSpanProcessor` from `otel-init.ts` — initialize `WebTracerProvider` without span processors
- [x] 4.2 Remove `@opentelemetry/exporter-trace-otlp-http` from `package.json` and run `npm install`
- [x] 4.3 Remove `VITE_OTEL_EXPORTER_URL` references from code and environment configs
- [x] 4.4 Run `make check` in frontend to verify lint and tests pass

## 5. Verification

- [x] 5.1 Run `make check` in cloud-provisioning (lint-ts, lint-k8s)
- [x] 5.2 Run `make check` in backend
