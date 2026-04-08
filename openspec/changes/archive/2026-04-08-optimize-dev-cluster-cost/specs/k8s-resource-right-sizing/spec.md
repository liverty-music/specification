## MODIFIED Requirements

### Requirement: Dev environment resource requests use Standard GKE minimums
All dev environment workloads SHALL set CPU request to 10m (Standard GKE minimum for idle workloads; no Autopilot Bursting floor applies). Memory requests SHALL be set to 1.5-2x of observed peak usage, with a floor of 20MiB.

#### Scenario: ArgoCD components resource requests
- **WHEN** rendering the ArgoCD dev overlay manifests
- **THEN** `argocd-application-controller` CPU request SHALL be 20m with memory request of 320MiB
- **AND** all other ArgoCD container CPU requests SHALL be 10m
- **AND** `repo-server`, `server`, `applicationset-controller` memory requests SHALL be 64MiB
- **AND** `redis`, `redisSecretInit` memory requests SHALL be 52MiB

#### Scenario: External Secrets components resource requests
- **WHEN** rendering the external-secrets dev overlay manifests
- **THEN** controller CPU request SHALL be 10m with memory request of 64MiB
- **AND** webhook and cert-controller CPU requests SHALL be 10m with memory requests of 52MiB

#### Scenario: Backend server resource requests
- **WHEN** rendering the backend dev overlay manifests
- **THEN** server-app CPU request SHALL be 10m with memory request of 60MiB
- **AND** consumer-app CPU request SHALL be 10m with memory request of 20MiB

#### Scenario: Frontend web-app resource requests
- **WHEN** rendering the frontend dev overlay manifests
- **THEN** web-app CPU request SHALL be 10m with memory request of 52MiB

#### Scenario: Reloader resource requests
- **WHEN** rendering the reloader dev overlay manifests
- **THEN** reloader CPU request SHALL be 10m with memory request of 64MiB

#### Scenario: KEDA components resource requests
- **WHEN** rendering the keda dev overlay manifests
- **THEN** operator, metricServer, and webhooks CPU requests SHALL each be 10m

#### Scenario: NATS resource requests
- **WHEN** rendering the nats dev overlay manifests
- **THEN** the NATS container merge CPU request SHALL be 10m

#### Scenario: OTel Collector resource requests
- **WHEN** rendering the otel-collector dev overlay manifests
- **THEN** the collector CPU request SHALL be 10m

#### Scenario: Atlas Operator resource requests
- **WHEN** rendering the atlas-operator dev overlay manifests
- **THEN** the atlas-operator CPU request SHALL be 10m

## ADDED Requirements

### Requirement: KEDA ScaledObjects in dev SHALL cap at maxReplicaCount 1
Consumer workload ScaledObjects in the dev environment SHALL set `maxReplicaCount: 1` to prevent horizontal scale-out in a low-traffic environment.

#### Scenario: consumer-app ScaledObject maxReplicaCount
- **WHEN** rendering the backend dev overlay manifests
- **THEN** the consumer-app ScaledObject `maxReplicaCount` SHALL be 1
- **AND** `minReplicaCount` SHALL remain 0 (zero-scale on idle is preserved)

## REMOVED Requirements

### Requirement: Resource limits provide burst headroom

The `Resource limits provide burst headroom` requirement and its `Limits do not exceed original allocation` scenario (CPU limit SHALL NOT exceed 500m; memory limit SHALL NOT exceed 512MiB) have been removed. The new strategy relies on the 10m CPU request floor and zero-scale-on-idle via KEDA (`maxReplicaCount: 1`) rather than hard resource ceilings.
