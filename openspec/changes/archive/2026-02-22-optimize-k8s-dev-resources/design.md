## Context

The dev GKE Autopilot cluster (v1.33, Bursting supported) runs 15 pods across 6 namespaces. Billing data shows Kubernetes Engine at ¥4,910/month with all workloads over-provisioned by 5-50x on CPU and 2-17x on memory. The cluster uses `cloud.google.com/compute-class: autopilot-spot` for cost savings, but coverage is incomplete.

Current resource allocation strategy uses uniform defaults (50m CPU / 256Mi memory request) regardless of actual workload characteristics. GKE Autopilot with Bursting (1.29+) allows requests as low as 50m CPU / 52MiB memory per container, with actual usage allowed to burst beyond requests.

## Goals / Non-Goals

**Goals:**
- Reduce Kubernetes Engine costs by 50-70% through resource right-sizing
- Ensure 100% Spot VM coverage for all dev workloads
- Remove unused ArgoCD components to reduce pod count
- Establish per-workload resource policies based on observed usage

**Non-Goals:**
- Optimizing non-K8s costs (Gemini API, Cloud Monitoring, Cloud SQL, Networking)
- Changing production or staging resource configurations
- Implementing VPA (Vertical Pod Autoscaler) — manual right-sizing is sufficient for dev
- Modifying application code or behavior

## Decisions

### D1: Resource request strategy — Autopilot minimum (50m CPU) for all idle workloads

All workloads with actual CPU usage <10m will use 50m CPU request (Autopilot Bursting minimum). Memory requests will be set to ~1.5-2x of observed peak usage, with a floor of 52MiB (Autopilot minimum).

**Why not set requests even lower?** 50m is the Autopilot Bursting minimum — requests below this are automatically rounded up, so there is no benefit.

**Why not use actual usage (e.g., 5m)?** Same reason — Autopilot enforces 50m minimum regardless of what the manifest says.

### D2: ArgoCD component control via Helm values

Disable dex and notifications via `values.yaml` in the ArgoCD base, since these components are not used in any environment.

```yaml
dex:
  enabled: false
notifications:
  enabled: false
```

**Alternative considered:** Disable only in dev overlay. Rejected because these components are not used in any environment — no reason to keep them enabled in base.

### D3: Backend replica reduction via dev overlay patch

Reduce backend server replicas from 2 to 1 in the dev overlay only, using a Kustomize strategic merge patch.

**Why not change base?** Base defines the production-ready default (2 replicas for availability). Dev overrides this for cost savings.

### D4: CronJob Spot VM coverage via additional patch target

Extend the backend dev overlay's spot-vm patch to target both `Deployment` and `CronJob` kinds. This requires adding a second patch entry in the kustomization.yaml since Kustomize patches target a single kind per entry.

### D5: Memory values — conservative approach for ArgoCD application-controller

The application-controller shows ~200MiB actual usage (highest among ArgoCD components) due to in-memory caching of cluster state. Its memory request will be set to 128MiB with a 384MiB limit to accommodate GC spikes, while other ArgoCD components use 64MiB or less.

## Risks / Trade-offs

- **[Pod eviction on burst]** With requests at minimum (50m CPU), heavy burst usage could cause scheduling pressure → Mitigated by Autopilot's automatic node scaling and the fact that actual usage is well below current requests
- **[ArgoCD dex re-enablement]** If SSO is needed later, dex must be re-enabled in values.yaml → Low risk, simple config change
- **[CronJob on Spot VM preemption]** Spot VMs can be preempted mid-job → Mitigated by CronJob's built-in retry mechanism and the job's non-critical nature (concert discovery)

## Migration Plan

1. Apply all manifest changes in a single PR to `cloud-provisioning` repository
2. ArgoCD auto-syncs changes to the dev cluster
3. Verify all pods are running and healthy after sync
4. Monitor resource usage for 1 week to validate right-sizing

**Rollback:** Revert the PR. ArgoCD auto-syncs back to previous state.

## Open Questions

- Should we investigate Gemini API costs (¥6,496/month, 37% of total) as a follow-up change?
- Is Cloud Monitoring Prometheus collection intentionally enabled, or can it be disabled for dev?
