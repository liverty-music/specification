## Why

The current prod GKE cluster (`standard-cluster-osaka`) is a Standard regional cluster which pays the full `$0.10/hr × 720 = $72/month` cluster management fee because regional Standard clusters are not eligible for the GKE free tier (only zonal Standard *or* Autopilot clusters are). Once the dev cluster is retired post-launch (per the team's plan), prod will be the only Pulumi-managed cluster in the billing account — at which point switching prod to **Autopilot regional** lets the entire `$74.40/month` free-tier credit cover the management fee, dropping it from `$72` to `$0`.

Even after factoring in Autopilot's mandatory Google Managed Service for Prometheus (GMP) cost — which cannot be disabled on Autopilot per [official docs](https://docs.cloud.google.com/stackdriver/docs/managed-prometheus/setup-managed) ("*You can't turn off managed collection in GKE Autopilot clusters running GKE version 1.25 or greater*") and which empirically cost the dev Autopilot cluster a few thousand yen per month — the net monthly saving is `$50-70`, equivalent to `$600-900/year`. The change is cleanly migratable now because prod has zero application workloads (only the cluster control plane runs), making the cluster-rebuild risk minimal.

## What Changes

- **BREAKING (irreversible cluster recreation)**: Replace `standard-cluster-osaka` with a new Autopilot regional cluster. The cluster mode (Standard vs Autopilot) is set at creation and cannot be flipped in-place per GKE docs ("*Neither direction supports in-place conversion*"), so this is a destroy-and-recreate operation, executed safely by virtue of prod being workload-free.
- Reuse the existing prod KMS key (`gke-cluster/gke-etcd-encryption`) for etcd CMEK on the new Autopilot cluster — the KMS resource itself does not need to be recreated.
- Continue requiring **Dataplane V2** (`datapathProvider: ADVANCED_DATAPATH`) — Autopilot uses Dataplane V2 by default, so this becomes implicit rather than explicit.
- Continue using the same secondary IP CIDR plan (`subnetCidr: 10.10.0.0/20`, `podsCidr: 10.20.0.0/16`, `servicesCidr: 10.30.0.0/20`, `masterCidr: 172.16.0.0/28`).
- Remove the explicit Spot `e2-medium` node pool definition — Autopilot manages node provisioning, so the per-workload `cloud.google.com/gke-spot: "true"` label (already present on dev manifests) becomes the only knob, scheduling Pods onto Spot-class compute via Autopilot's Spot Pod pricing.
- **GMP cost-control settings baked in at cluster creation**: configure ClusterPodMonitoring `metricRelabeling` to drop all non-essential metrics, extend scrape interval to 60s (down from default 15s for a `4×` ingestion reduction), and disable automatic application monitoring so workload metrics are opt-in via per-namespace PodMonitoring CRDs. This keeps the empirical GMP cost in the `$5-15/month` band.
- **BREAKING**: Existing prod DNS records (`api.liverty-music.app`, `auth.liverty-music.app`) and the static IP (`api-gateway-static-ip`) point at the *old* cluster's Gateway. The migration plan cuts over by re-targeting the same static IP at the new cluster's Gateway, so DNS records remain unchanged (no Cloudflare/Cloud DNS rewrite required), but there is a brief Gateway-up window where the static IP is unbound.

## Capabilities

### New Capabilities

(none — this change does not introduce a new capability.)

### Modified Capabilities

- `prod-environment-bootstrap`: cluster-mode requirement changes from "Standard regional" to "Autopilot regional" (still regional, still using etcd CMEK + Dataplane V2 + same CIDR plan, but with Autopilot's node-management model). The Spot-pool-specific requirements are removed; instead, Pods continue using the `cloud.google.com/gke-spot: "true"` label to request Spot Pod scheduling. A new requirement records the GMP cost-control baseline (metric relabel + 60s scrape interval) that the new Autopilot cluster must satisfy. The "Initial prod Pulumi deploy SHALL be manual-triggered" requirement is preserved — this change's cutover is itself a manual Pulumi Cloud deployment.

## Impact

- **Pulumi code** (`cloud-provisioning/src/gcp/components/kubernetes.ts`):
  - Replace the prod `gcp.container.Cluster` block (regional Standard) with an Autopilot variant (`enableAutopilot: true`, no separate `NodePool` resource). Pulumi resource URN must change (mode flip cannot be in-place); plan: declare new resource alongside the old, perform cutover, destroy old. Or, more practically, rebuild the entire prod stack since it has no live data.
  - Remove the prod-specific `spot-pool-osaka` `gcp.container.NodePool` block.
  - KMS resource (`KmsComponent` at `src/gcp/components/kms.ts`) stays — the new Autopilot cluster reuses the same `gke-etcd-encryption` key.
  - Network resources (Cloud DNS, Certificate Manager, static IP) stay — same hostnames, same IP, just retargeted.
- **Kubernetes manifests / config**: a ClusterPodMonitoring resource for GMP cost control needs to be authored (delivered alongside the cluster cutover, since it cannot exist before the cluster exists). The k8s manifests change (formerly slated for a separate `prod-k8s-manifests` follow-up) gets a new mandatory item: GMP cost-control config.
- **Existing prod resources to destroy**: Cluster + node pool (with `deletionProtection` flipped off by Pulumi). All other prod resources (KMS, Cloud SQL, DNS zones, certs, Secret Manager) remain intact.
- **Cost impact**:
  - Pre-migration: $72/month management + $5.76/month Compute = $77.76/month
  - Post-migration: $0/month management (free tier covers) + $5-15/month GMP + $0-6.50/month Compute (Pod-level Spot) = $5-22/month
  - Net saving: **$55-72/month = $660-864/year** (workload size and GMP optimization aggressiveness dependent)
- **Risk**: The migration includes a brief Gateway unbind window during static-IP retargeting. Acceptable because there are no live users on prod yet. This is the last safe moment to flip the cluster mode without a real downtime cost.
- **Out of scope**: ArgoCD Applications + per-namespace overlays remain deferred to the separate `prod-k8s-manifests` change. This migration only changes the cluster itself + GMP config; workload bootstrap is independent.
