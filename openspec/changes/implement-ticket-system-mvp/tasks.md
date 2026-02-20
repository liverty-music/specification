## 1. Infrastructure — Secret Manager

> GKE Autopilot (`cluster-osaka`) and Cloud SQL PostgreSQL 18 (`postgres-osaka`) already exist. No new compute/database provisioning needed.

- [ ] 1.1 Add Secret Manager secret for TicketSBT contract deployer private key (`cloud-provisioning`)
- [ ] 1.2 Add Secret Manager secret for Base Sepolia RPC endpoint URL (`cloud-provisioning`)
- [ ] 1.3 Add Secret Manager secret for Bundler (Pimlico/Alchemy) API key (`cloud-provisioning`)
- [ ] 1.4 Configure Zitadel: enable Passkey authentication for the existing project
- [ ] 1.5 Run `pulumi preview` and get approval; apply Secret Manager changes to dev

## 2. Database Schema (ALTER + CREATE migrations)

> Existing tables: `users` (with `external_id`), `events` (with `venue_id`, `title`, `local_event_date`), `concerts`, `artists`, `venues`. Migrations must be backward-compatible.

- [ ] 2.1 Write ALTER migration: `users` ADD `safe_address TEXT` (predicted Safe address derived from `users.id`)
- [ ] 2.2 Write ALTER migration: `events` ADD `merkle_root BYTEA` (nullable; NULL for non-ticket events)
- [ ] 2.3 Write CREATE migration: `tickets` table (id UUID PK, event_id FK → events, user_id FK → users, token_id BIGINT, tx_hash TEXT, minted_at TIMESTAMPTZ)
- [ ] 2.4 Write CREATE migration: `merkle_tree` table (event_id FK → events, depth INT, index INT, hash BYTEA; composite PK on event_id + depth + index)
- [ ] 2.5 Write CREATE migration: `nullifiers` table (event_id FK → events, nullifier_hash BYTEA, used_at TIMESTAMPTZ; UNIQUE index on event_id + nullifier_hash)
- [ ] 2.6 Verify all migrations run cleanly on local PostgreSQL; write rollback (DOWN) migrations
- [ ] 2.7 Verify ALTER migrations are backward-compatible (existing queries on `users`/`events` unaffected)

## 3. ZK Circuit

- [ ] 3.1 Author `TicketCheck` circom circuit using Poseidon hash (not MiMC); depth <= 20
- [ ] 3.2 Define circuit inputs: private (`trapdoor`, `nullifierSecret`, `pathElements[]`, `pathIndices[]`); public (`merkleRoot`, `nullifierHash`)
- [ ] 3.3 Perform Phase 1 trusted setup using Hermez Powers of Tau ceremony (ptau file)
- [ ] 3.4 Run Phase 2 circuit-specific setup: generate `.zkey` file
- [ ] 3.5 Export verification key JSON (`verification_key.json`) for backend
- [ ] 3.6 Build circuit WASM (`ticketcheck.wasm`) for browser proof generation
- [ ] 3.7 Publish `.wasm` and `.zkey` to CDN with versioned paths (e.g., `/circuits/ticketcheck-v1/`)
- [ ] 3.8 Benchmark proof generation in Chrome (desktop) and low-end Android; confirm < 30s mobile

## 4. Smart Contract

- [ ] 4.1 Author `TicketSBT` contract implementing ERC-721 + ERC-5192 (non-transferable)
- [ ] 4.2 Implement `MINTER_ROLE` access control; `mint(address recipient, uint256 tokenId)` callable only by backend service key
- [ ] 4.3 Implement transfer lock: `transferFrom` and `safeTransferFrom` revert with "SBT: Ticket transfer is prohibited"
- [ ] 4.4 Emit `Locked(tokenId)` event on mint (ERC-5192 compliance)
- [ ] 4.5 Write Foundry tests: transfer revert, locked event emission, authorized mint, unauthorized mint revert
- [ ] 4.6 Deploy `TicketSBT` to Base Sepolia; record contract address in Secret Manager
- [ ] 4.7 Grant `MINTER_ROLE` to backend service account EOA address

## 5. Protobuf / BSR

> Proto files are managed in BSR (`liverty-music/schema`). Generated Go/TS code is imported via dependency, not generated locally. No proto files live in the backend repo.

- [ ] 5.1 Define `ticket/v1/ticket.proto` in BSR: `TicketService` with `MintTicket`, `GetTicket`, `ListTicketsForUser` RPCs
- [ ] 5.2 Define `entry/v1/entry.proto` in BSR: `EntryService` with `VerifyEntry` RPC (accepts proof JSON + event ID) and `GetMerklePath` RPC
- [ ] 5.3 Add Protovalidate constraints to all request messages
- [ ] 5.4 Run `buf lint` and `buf breaking` against baseline; push to BSR
- [ ] 5.5 Bump generated Go module version in backend `go.mod` (`buf.build/gen/go/liverty-music/schema`)
- [ ] 5.6 Bump generated TS module version in frontend `package.json` (`@buf/liverty-music_schema`)

## 6. Go Backend — Zitadel Passkey Configuration

> Authentication uses existing Zitadel OIDC flow. No self-hosted WebAuthn RP for MVP. Zitadel's hosted login UI handles Passkey registration/authentication.

- [ ] 6.1 Configure Zitadel Passkey settings via v2 API: enable Passkey authenticator for the application
- [ ] 6.2 Implement Safe address prediction: `CREATE2(salt = keccak256(users.id))` using `SafeProxyFactory` formula (`go-ethereum/crypto`)
- [ ] 6.3 Add Safe address computation on user creation (or lazy computation on first ticket mint)
- [ ] 6.4 Ensure JWT validation (`jwx`) has configurable `accepted_issuers` list (preparation for Option C migration)
- [ ] 6.5 Write unit tests for Safe address determinism (same `users.id` always produces same address)

## 7. Go Backend — Ticket Minting (ERC-5192)

- [ ] 7.1 Generate Go bindings for `TicketSBT` ABI using `abigen`
- [ ] 7.2 Implement `MintTicket` handler: sign and send mint transaction from backend service EOA via `go-ethereum/ethclient`
- [ ] 7.3 Make mint idempotent: check `tickets` table and on-chain `ownerOf` before submitting transaction
- [ ] 7.4 Add retry logic with exponential backoff for Base Sepolia RPC calls
- [ ] 7.5 Store minted token ID and tx hash in `tickets` table on success
- [ ] 7.6 Implement `GetTicket` and `ListTicketsForUser` handlers (query `tickets` table joined with `events`)

## 8. Go Backend — ZKP Verification

- [ ] 8.1 Add `consensys/gnark` v0.14.0 and `vocdoni/circom2gnark` dependencies
- [ ] 8.2 Load `verification_key.json` at server startup; convert to gnark types via circom2gnark; cache in memory
- [ ] 8.3 Implement `VerifyEntry` handler: parse proof JSON from request, convert via circom2gnark, call `groth16.Verify`
- [ ] 8.4 Implement `GetMerklePath` handler: return Merkle path for a given user + event from `merkle_tree` table
- [ ] 8.5 On successful verification: atomically insert `nullifiers` row (unique constraint = double-entry guard)
- [ ] 8.6 Return structured error on duplicate nullifier (event-specific "already checked in" response)
- [ ] 8.7 Write integration test: round-trip a known circom-generated proof through circom2gnark -> gnark Verify
- [ ] 8.8 Write integration test: duplicate nullifier returns correct error

## 9. Go Backend — Merkle Tree Management

- [ ] 9.1 Implement Merkle tree builder: given a list of user identity commitments for an event, compute the full tree and store nodes in `merkle_tree` table
- [ ] 9.2 Implement `merkle_root` update on `events` table when tree is (re)built
- [ ] 9.3 Implement identity commitment computation: `Poseidon(users.id)` or agreed leaf format (depends on Open Question resolution)
- [ ] 9.4 Write unit tests for Merkle tree construction and path extraction

## 10. Frontend — Aurelia 2 PWA Foundation

- [ ] 10.1 Add `manifest.json` with correct icons (192px, 512px), `display: standalone`, `start_url`
- [ ] 10.2 Configure `vite-plugin-pwa` v1.2.0 in `injectManifest` mode; set `maximumFileSizeToCacheInBytes: 60MB`
- [ ] 10.3 Author `sw.ts`: precache app shell via `self.__WB_MANIFEST`; add `registerRoute` for `.wasm` and `.zkey` (CacheFirst, 30-day expiry, cache name `zk-circuits-v1`)
- [ ] 10.4 Verify Service Worker registers and caches circuit files on first load (Chrome DevTools -> Application)
- [ ] 10.5 Verify A2HS install prompt appears on Android Chrome and iOS Safari (Add to Home Screen)
- [ ] 10.6 Verify offline load after first visit (disconnect network, reload)

## 11. Frontend — Auth (Zitadel Hosted Login UI)

> MVP uses Zitadel's hosted login UI with Passkey support. No `@simplewebauthn/browser` needed. Existing `oidc-client-ts` flow is unchanged.

- [ ] 11.1 Verify existing `oidc-client-ts` OIDC flow supports Passkey login via Zitadel hosted UI (no code change expected)
- [ ] 11.2 Test Passkey registration through Zitadel hosted UI on desktop and mobile browsers
- [ ] 11.3 Test Passkey authentication through Zitadel hosted UI on desktop and mobile browsers
- [ ] 11.4 Document supported browsers and minimum OS versions for Passkey (iOS 16.4+, Android 9+)

## 12. Frontend — ZKP Entry Code Generation

- [ ] 12.1 Add `snarkjs` dependency; confirm it loads correctly as ES module in Aurelia 2 / Vite
- [ ] 12.2 Move proof generation into a Web Worker (`proof.worker.ts`) to avoid blocking main thread
- [ ] 12.3 Implement `generateProof(trapdoor, nullifierSecret, merkleRoot, pathElements, pathIndices)` in worker
- [ ] 12.4 Fetch Merkle path from backend `GetMerklePath` RPC before generating proof
- [ ] 12.5 Display proof result as QR code (encode proof JSON + event ID as base64 payload)
- [ ] 12.6 Show progress indicator during proof generation (expected 3-30s depending on device)

## 13. Frontend — Ticket Display

- [ ] 13.1 Implement `ListTicketsForUser` call on authenticated home screen
- [ ] 13.2 Display ticket details: event name, date, token ID, SBT status
- [ ] 13.3 Show "Generate Entry Code" button for each ticket; navigate to proof generation flow

## 14. CI / CD

> Backend and frontend already have CD pipelines. Add CI checks for new components.

- [ ] 14.1 Add GitHub Actions workflow: `buf lint` + `buf breaking` on proto changes (BSR repo)
- [ ] 14.2 Verify existing Go backend CI (`go test ./...` + `golangci-lint`) covers new handlers
- [ ] 14.3 Verify existing frontend CI (`npm run build`) covers PWA manifest validation
- [ ] 14.4 Add integration test job: spin up local Bundler (Rundler) + Anvil fork of Base Sepolia; run UserOperation ABI encoding tests
