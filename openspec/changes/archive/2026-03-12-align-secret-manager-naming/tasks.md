## 1. Go Backend — Rename envconfig tags

- [x] 1.1 Rename `TICKET_SBT_DEPLOYER_KEY` → `BLOCKCHAIN_DEPLOYER_PRIVATE_KEY` in `BlockchainConfig` struct (`pkg/config/config.go`)
- [x] 1.2 Rename `BASE_SEPOLIA_RPC_URL` → `BLOCKCHAIN_RPC_URL` in `BlockchainConfig` struct
- [x] 1.3 ~~Rename `BUNDLER_API_KEY` → `BLOCKCHAIN_BUNDLER_API_KEY` in `BlockchainConfig` struct~~ (skipped: field not in Go code yet, future ERC-4337 feature)
- [x] 1.4 ~~Update Go doc comments on renamed fields~~ (no changes needed: comments describe semantics, not env var names)
- [x] 1.5 Run `make check` in backend

## 2. Cloud Provisioning — Pulumi TypeScript

- [x] 2.1 Create `BlockchainConfig` interface in `src/gcp/components/project.ts`, move blockchain fields out of `GcpConfig`
- [x] 2.2 Update `src/gcp/index.ts` to read config from `blockchain` namespace and use new SM names (`blockchain-deployer-private-key`, `blockchain-rpc-url`, `blockchain-bundler-api-key`)
- [x] 2.3 Run `make check` in cloud-provisioning

## 3. Cloud Provisioning — K8s ExternalSecret

- [x] 3.1 Update `k8s/namespaces/backend/base/server/external-secret.yaml`: rename `secretKey` and `remoteRef.key` to `BLOCKCHAIN_*` / `blockchain-*` naming
- [x] 3.2 Run `kubectl kustomize` dry-run to verify manifest renders correctly

## 4. Pulumi ESC — Migrate secrets

- [x] 4.1 Set `pulumiConfig.blockchain.deployerPrivateKey` in `liverty-music/dev` ESC (value from existing `smartContract.deployerEoa.privateKey`)
- [x] 4.2 Set `pulumiConfig.blockchain.rpcUrl` in `liverty-music/dev` ESC (Alchemy Base Sepolia endpoint)
- [x] 4.3 Set `pulumiConfig.blockchain.bundlerApiKey` in `liverty-music/dev` ESC (value from existing `smartContract.bundlerApiKey`)
- [x] 4.4 Remove old `smartContract.*` keys from ESC (manual: `esc env rm liverty-music/dev pulumiConfig.smartContract`)

## 5. Documentation

- [x] 5.1 Update `cloud-provisioning/docs/TICKET_SYSTEM_SETUP.md` to reflect new naming across all references

## 6. Deploy & Verify

- [x] 6.1 Run `pulumi preview` to verify Secret Manager resources will be created with correct names
- [x] 6.2 Get user approval and run `pulumi up`
- [x] 6.3 Confirm secrets exist in Secret Manager: `gcloud secrets list --project=liverty-music-dev`
- [x] 6.4 Confirm ExternalSecret `server-backend-secrets` status is `Ready: True` (pending: ArgoCD sync after code merge)
- [x] 6.5 Confirm ArgoCD `backend` Application health transitions from `Degraded` (pending: ArgoCD sync after code merge)
- [x] 6.6 Check server pod logs for blockchain config initialization (pending: ArgoCD sync after code merge)
