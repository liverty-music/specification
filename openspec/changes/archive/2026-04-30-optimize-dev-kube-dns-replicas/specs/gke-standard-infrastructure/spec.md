## ADDED Requirements

### Requirement: Dev cluster `kube-dns-autoscaler` SHALL set `preventSinglePointFailure: false`
The dev GKE cluster SHALL override the GKE-managed `kube-dns-autoscaler` ConfigMap (in `kube-system`) so that the linear scaling policy declares `preventSinglePointFailure: false`. The remaining linear-policy fields (`coresPerReplica`, `nodesPerReplica`) SHALL retain GKE's defaults of 256 and 16 respectively. Rationale: with the cluster at 6 vCPU / 3 nodes, the cluster-proportional-autoscaler formula computes 1 desired replica; the single-point-of-failure guard is the only reason kube-dns runs at 2 replicas, consuming an additional 270m CPU that prevents the cluster autoscaler from compacting to 2 spot nodes. dev does not require kube-dns HA — `node-local-dns` caching plus client retries cover the rare reschedule gap.

#### Scenario: ConfigMap declares preventSinglePointFailure false
- **WHEN** running `kubectl get configmap kube-dns-autoscaler -n kube-system -o yaml` on the dev cluster
- **THEN** the `data.linear` JSON value SHALL contain `"preventSinglePointFailure":false`

#### Scenario: kube-dns scales to one replica
- **WHEN** running `kubectl get deployment kube-dns -n kube-system` on the dev cluster after the autoscaler has reconciled
- **THEN** the `READY` count SHALL be `1/1`

#### Scenario: Override is reconciled by ArgoCD
- **WHEN** the GKE control plane resets the ConfigMap to its managed default (e.g., during cluster upgrade)
- **THEN** ArgoCD's `core` Application SHALL re-apply the dev override within one sync interval, restoring `preventSinglePointFailure: false`

#### Scenario: Override is dev-only
- **WHEN** comparing rendered manifests for `prod` and `staging` overlays
- **THEN** neither overlay SHALL include a `kube-dns-autoscaler` ConfigMap override
- **AND** the GKE-default `preventSinglePointFailure: true` SHALL apply in those environments
