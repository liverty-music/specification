## ADDED Requirements

### Requirement: Prod backend ConfigMaps SHALL reference the mainnet ticket SBT contract

The `TICKET_SBT_ADDRESS` environment variable in every prod backend ConfigMap (under `cloud-provisioning/k8s/namespaces/backend/overlays/prod/*/configmap.env`) SHALL reference the deployed mainnet Soul-Bound Token contract address. The zero address (`0x0000000000000000000000000000000000000000`) SHALL NOT be present in any prod configmap, because it is a placeholder that the backend treats as "no contract configured" and silently disables ticket-minting RPCs.

#### Scenario: No zero-address SBT in prod configmaps

- **WHEN** searching `cloud-provisioning/k8s/namespaces/backend/overlays/prod/*/configmap.env` for `TICKET_SBT_ADDRESS=`
- **THEN** every match SHALL have a value that is NOT `0x0000000000000000000000000000000000000000`
- **AND** the value SHALL pass EIP-55 checksum validation

#### Scenario: Mainnet contract is reachable

- **WHEN** querying the configured `TICKET_SBT_ADDRESS` on Polygon mainnet via the prod RPC URL (`blockchain.rpcUrl`)
- **THEN** the address SHALL be deployed (non-empty contract bytecode)
- **AND** the contract SHALL respond to the expected SBT ABI (e.g., `name()`, `symbol()`, `totalSupply()`)

### Requirement: Prod VAPID public key SHALL match the GSM-stored private key

The `VAPID_PUBLIC_KEY` value baked into prod's backend ConfigMaps (`server`, `consumer`, `cronjob/concert-discovery`) AND into the prod frontend bundle (via the build-time env contract) SHALL be the public half of the same VAPID keypair whose private half is stored in the `vapid-private-key` GSM Secret in the `liverty-music-prod` project. If the configmap-baked public key was carried over from dev as a placeholder, prod-specific keys SHALL be regenerated and both halves updated as part of one coordinated apply window. Strict cluster-side atomicity is not achievable because ArgoCD (configmap reconciliation) and ESO (GSM-backed Secret reconciliation) operate as independent control loops; the operational requirement is therefore a sub-minute mismatch window during the rotation, gated on the absence of live push subscriptions (prod is pre-launch when this rotation runs). The byte-equal invariant in the scenarios below describes the steady state after the apply window closes, not every transient mid-rotation moment.

This invariant prevents the silent-failure mode where Web Push subscriptions signed by the SPA cannot be validated by the backend (the SPA's `applicationServerKey` and the backend's signing key are mismatched halves of different keypairs).

#### Scenario: Configmap public key matches GSM private key

- **WHEN** an operator extracts the prod `VAPID_PUBLIC_KEY` value from any backend prod configmap
- **AND** derives the public key from the GSM `vapid-private-key` (Base64URL-encoded uncompressed P-256 point)
- **THEN** the two values SHALL be byte-equal

#### Scenario: Frontend bundle public key matches GSM private key

- **WHEN** an operator extracts `VITE_VAPID_PUBLIC_KEY` from the prod-built `web-app` static assets
- **AND** derives the public key from GSM `vapid-private-key`
- **THEN** the two values SHALL be byte-equal

#### Scenario: Push notifications round-trip in prod

- **WHEN** an operator subscribes to push notifications via the prod SPA
- **AND** triggers a backend notification path
- **THEN** the backend SHALL successfully sign the push payload using the GSM-stored private key
- **AND** the browser SHALL accept the push (no `BadJwtToken` or signature-mismatch failure)

### Requirement: Prod blockchain ESC values SHALL reference mainnet

The `blockchain.deployerPrivateKey`, `blockchain.rpcUrl`, and `blockchain.bundlerApiKey` keys in the `liverty-music/prod` ESC environment SHALL reference Polygon mainnet (or whichever EVM mainnet hosts the prod ticket SBT contract), not Polygon Amoy / Sepolia or any other testnet. The dev ESC environment uses testnet values; prod's must diverge appropriately.

#### Scenario: Prod RPC URL targets mainnet

- **WHEN** an operator decrypts `blockchain.rpcUrl` from `esc env get liverty-music/prod`
- **THEN** the URL host SHALL match a known Polygon mainnet provider (e.g., `polygon-rpc.com`, `polygon-mainnet.alchemyapi.io`, `polygon-mainnet.g.alchemy.com`, or an Infura/QuickNode mainnet endpoint)
- **AND** SHALL NOT contain the substring `amoy`, `mumbai`, `sepolia`, or `testnet`

#### Scenario: Prod deployer private key controls the mainnet ticket SBT owner

- **WHEN** an operator decrypts `blockchain.deployerPrivateKey` from prod ESC
- **AND** derives the corresponding Ethereum address
- **THEN** the address SHALL be the owner of the mainnet `TICKET_SBT_ADDRESS` contract (as reported by `owner()` on the contract)

#### Scenario: Prod bundler API key targets mainnet

- **WHEN** an operator decrypts `blockchain.bundlerApiKey` from prod ESC
- **AND** uses it to query the ERC-4337 bundler's `chainId`
- **THEN** the chainId SHALL equal `137` (Polygon mainnet) or the mainnet chainId of whichever EVM network the prod contract is deployed on

### Requirement: Prod admin Google sub SHALL be issued by the prod OAuth client

The `zitadel.adminGoogleSubs.pannpers` value in the `liverty-music/prod` ESC environment SHALL be the Google `sub` identifier issued by the *prod* Google OAuth Web Application client (`108947861615-…apps.googleusercontent.com`, owned by the `liverty-music-prod` GCP project) for the `pannpers@pannpers.dev` Google identity. Google's `sub` is per-OAuth-client, so the dev and prod values are intentionally different even though the underlying human identity is the same; a copy-paste of the dev sub into prod ESC would break IdP linking on first prod sign-in.

#### Scenario: Prod sub differs from dev sub

- **WHEN** an operator decrypts `zitadel.adminGoogleSubs.pannpers` from both `liverty-music/dev` and `liverty-music/prod` ESC environments
- **THEN** the two values SHALL be different

#### Scenario: Prod sub authenticates against prod admin org

- **WHEN** the pannpers identity signs in via Google IdP at `https://auth.liverty-music.app/ui/console`
- **THEN** Zitadel SHALL resolve the user to the pre-linked admin HumanUser in the prod `admin` org via the configured `sub`
- **AND** SHALL NOT prompt for a separate Zitadel account or create a new user
