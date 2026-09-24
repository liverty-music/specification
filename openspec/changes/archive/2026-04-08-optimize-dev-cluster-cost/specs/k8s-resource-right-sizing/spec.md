## REMOVED Requirements

### Requirement: Resource limits provide burst headroom

The `Resource limits provide burst headroom` requirement and its `Limits do not exceed original allocation` scenario (CPU limit SHALL NOT exceed 500m; memory limit SHALL NOT exceed 512MiB) have been removed. The new strategy relies on the 10m CPU request floor and zero-scale-on-idle via KEDA (`maxReplicaCount: 1`) rather than hard resource ceilings.
