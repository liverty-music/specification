## 1. Sampler (backend, components/infrastructure/backend/process/trace-propagation)

- [x] 1.1 Add `clientRootDrop` in `pkg/telemetry` and use it as the root sampler inside `ParentBased` in `setupTracerProvider` (design "Drop client roots in the sampler"); verify with unit tests on an in-memory span recorder, annotated `// @spec components/infrastructure/backend/process/trace-propagation "<scenario>"`, that a client span with no parent is not recorded and its context still carries a valid trace id ("Background check that finds nothing"), that an `otelhttp` client call with no parent records nothing ("Database credential refresh"), and that a client span under a server span is recorded as its child ("Same query inside a request"); also verify that a producer span and an internal span with no parent are still recorded, and that `make check` is clean

## 2. Production check (read-only, after the backend release is rolled out)

- [x] 2.1 List one hour of prod traces with the Cloud Trace API (`gcloud --configuration=liverty-music auth print-access-token`, `cloudtrace.googleapis.com/v1/projects/liverty-music-prod/traces?view=COMPLETE`) and confirm that no trace's root span is of kind client, and that RPC, job and consumer traces still arrive
- [x] 2.2 The day after the rollout, read the "Spans ingested" usage for that day from the billing export and record it next to the 2026-10-28 baseline (14,984) in this change's design.md
