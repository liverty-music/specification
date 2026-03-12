## Context

Blockchain-related secrets are named inconsistently across all layers. The feature has never worked in dev because Secret Manager entries were never created — ExternalSecret has been in `SecretSyncedError` since 2026-02-21, causing ArgoCD to report the backend Application as Degraded.

Current naming chaos:

| Layer | Deployer Key | RPC URL | Bundler |
|-------|-------------|---------|---------|
| Go `envconfig` tag | `TICKET_SBT_DEPLOYER_KEY` | `BASE_SEPOLIA_RPC_URL` | `BUNDLER_API_KEY` |
| ExternalSecret `remoteRef.key` | `ticket-sbt-deployer-key` | `base-sepolia-rpc-url` | `bundler-api-key` |
| Pulumi SM name | `blockchain-deployer-private-key` | `blockchain-rpc-url` | `bundler-api-key` |
| ESC path | `smartContract.deployerEoa.privateKey` | (missing) | `smartContract.bundlerApiKey` |
| Pulumi interface | `gcp.ticketSbtDeployerKey` | `gcp.baseSepoliaRpcUrl` | `gcp.bundlerApiKey` |
| Secret Manager (actual) | does not exist | does not exist | does not exist |

Six layers, five different naming conventions.

## Goals / Non-Goals

**Goals:**
- Unify all layers under a single `blockchain`-prefixed naming convention
- Rename Go envconfig tags (feature is not running, safe to change)
- Extract blockchain config from `GcpConfig` into a dedicated `BlockchainConfig` interface in Pulumi
- Move ESC secrets from `smartContract.*` to `blockchain.*`
- Create the secrets in GCP Secret Manager (dev environment)
- Resolve ExternalSecret `SecretSyncedError` and ArgoCD `Degraded` status
- Update documentation (`TICKET_SYSTEM_SETUP.md`)

**Non-Goals:**
- Deploying the TicketSBT contract (requires separate setup)
- Enabling ticket minting in production (dev only)
- Multi-chain support (YAGNI — single-chain design is sufficient)

## Decisions

### 1. `blockchain` is the naming domain across all layers

The Go struct is `BlockchainConfig`. All layers derive names from this domain:

| Layer | Deployer Key | RPC URL | Bundler |
|-------|-------------|---------|---------|
| Go envconfig | `BLOCKCHAIN_DEPLOYER_PRIVATE_KEY` | `BLOCKCHAIN_RPC_URL` | `BLOCKCHAIN_BUNDLER_API_KEY` |
| ESC path | `blockchain.deployerPrivateKey` | `blockchain.rpcUrl` | `blockchain.bundlerApiKey` |
| Pulumi interface | `BlockchainConfig.deployerPrivateKey` | `BlockchainConfig.rpcUrl` | `BlockchainConfig.bundlerApiKey` |
| SM name | `blockchain-deployer-private-key` | `blockchain-rpc-url` | `blockchain-bundler-api-key` |
| ExternalSecret secretKey | `BLOCKCHAIN_DEPLOYER_PRIVATE_KEY` | `BLOCKCHAIN_RPC_URL` | `BLOCKCHAIN_BUNDLER_API_KEY` |
| ExternalSecret remoteRef.key | `blockchain-deployer-private-key` | `blockchain-rpc-url` | `blockchain-bundler-api-key` |

**Rationale**: Chain-specific names (`BASE_SEPOLIA_*`) break on mainnet migration. Contract-specific names (`TICKET_SBT_*`) break when the same deployer EOA is reused for other contracts. `BLOCKCHAIN_*` is the right abstraction level — stable across chain and contract changes.

### 2. Extract `BlockchainConfig` from `GcpConfig` in Pulumi

Blockchain secrets are not GCP-specific. Create a separate `BlockchainConfig` interface and move the fields out of `GcpConfig`:

```typescript
export interface BlockchainConfig {
  deployerPrivateKey?: string
  rpcUrl?: string
  bundlerApiKey?: string
}
```

Read from Pulumi config under the `blockchain` namespace instead of `gcp`.

### 3. Migrate ESC from `smartContract.*` to `blockchain.*`

Move existing values:
- `smartContract.deployerEoa.privateKey` → `blockchain.deployerPrivateKey`
- `smartContract.bundlerApiKey` → `blockchain.bundlerApiKey`
- Add missing: `blockchain.rpcUrl`
- Remove old `smartContract.*` keys after migration

### 4. RPC URL derivation

The Alchemy API key from `smartContract.bundlerApiKey` (`qTGHFFio_i56ngeXDUMMO`) is likely the same key used for the RPC URL: `https://base-sepolia.g.alchemy.com/v2/<API_KEY>`. Confirm with user before setting.

## Risks / Trade-offs

- **[Risk] Go envconfig rename breaks local `.env` files** → Acceptable. Feature never worked; no one has working `.env` entries for these fields.
- **[Risk] ESC migration leaves orphaned `smartContract.*` keys** → Clean up in the same change. Remove after verifying new keys work.
- **[Risk] `TICKET_SBT_ADDRESS` still missing** → Even with all three secrets, ticket minting requires the deployed contract address. Out of scope — the DI code gracefully logs a warning when absent.
