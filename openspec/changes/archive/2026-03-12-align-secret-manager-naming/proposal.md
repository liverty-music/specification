## Why

Blockchain-related secret names are inconsistent across six layers (Go envconfig, ExternalSecret, Pulumi SM names, ESC paths, Pulumi TypeScript interface, GCP Secret Manager). The naming chaos — mixing `TICKET_SBT_*`, `blockchain-*`, `BASE_SEPOLIA_*`, `smartContract.*`, and `gcp.*` — caused ExternalSecret to reference non-existent Secret Manager keys. The backend ArgoCD Application has been Degraded since 2026-02-21 and the ticket minting feature has never worked in dev.

## What Changes

- Unify all layers under `BLOCKCHAIN_*` / `blockchain.*` / `blockchain-*` naming convention
- Rename Go `envconfig` struct tags (feature is currently non-functional, safe to change)
- Extract `BlockchainConfig` from `GcpConfig` in Pulumi TypeScript
- Migrate ESC secrets from `smartContract.*` to `blockchain.*`
- Update ExternalSecret manifest to match new naming
- Create secrets in GCP Secret Manager via `pulumi up`
- Update `TICKET_SYSTEM_SETUP.md` documentation

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none — infrastructure configuration fix across all layers)

## Impact

- **backend**: `pkg/config/config.go` envconfig tags renamed
- **cloud-provisioning**: `src/gcp/components/project.ts` new `BlockchainConfig` interface
- **cloud-provisioning**: `src/gcp/index.ts` config reading and SM names
- **cloud-provisioning**: `k8s/namespaces/backend/base/server/external-secret.yaml` key names
- **cloud-provisioning**: `docs/TICKET_SYSTEM_SETUP.md` documentation
- **Pulumi ESC**: `liverty-music/dev` environment secret paths migrated
- **GCP Secret Manager**: 3 new secrets created
- **Kubernetes**: ExternalSecret syncs successfully, ArgoCD Degraded resolves
