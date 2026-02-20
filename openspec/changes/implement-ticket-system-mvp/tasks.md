## 1. Infrastructure Provisioning

- [ ] 1.1 Add GKE Autopilot cluster resource to `cloud-provisioning` (Osaka region)
- [ ] 1.2 Add Cloud SQL (PostgreSQL 16) instance resource to `cloud-provisioning`
- [ ] 1.3 Add Secret Manager secrets for contract private key and JWT signing key
- [ ] 1.4 Configure GKE Workload Identity binding for the backend service account
- [ ] 1.5 Run `pulumi preview` and get approval; apply infrastructure stack to dev

## 2. Database Schema

- [ ] 2.1 Write initial migration: `users` table (passkey credential ID, public key CBOR, safe address, created_at)
- [ ] 2.2 Write migration: `events` table (id, name, merkle_root, starts_at)
- [ ] 2.3 Write migration: `tickets` table (id, event_id, owner_safe_address, token_id, minted_at)
- [ ] 2.4 Write migration: `merkle_tree` table (event_id, depth, index, hash, leaf_data)
- [ ] 2.5 Write migration: `nullifiers` table (event_id, nullifier_hash, used_at) with unique index
- [ ] 2.6 Write migration: `webauthn_sessions` table (challenge, expires_at) for transient ceremony state
- [ ] 2.7 Verify all migrations run cleanly on local PostgreSQL; write rollback migrations

## 3. ZK Circuit

- [ ] 3.1 Author `TicketCheck` circom circuit using Poseidon hash (not MiMC); depth ≤ 20
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
- [ ] 4.6 Deploy `TicketSBT` to Base Sepolia; record contract address in backend Secret Manager config
- [ ] 4.7 Grant `MINTER_ROLE` to backend service account EOA address

## 5. Protobuf / Connect RPC API

- [ ] 5.1 Define `ticket/v1/ticket.proto`: `TicketService` with `MintTicket`, `GetTicket`, `ListTicketsForUser` RPCs
- [ ] 5.2 Define `auth/v1/auth.proto`: `AuthService` with `BeginRegistration`, `FinishRegistration`, `BeginAuthentication`, `FinishAuthentication` RPCs
- [ ] 5.3 Define `entry/v1/entry.proto`: `EntryService` with `VerifyEntry` RPC (accepts proof JSON + event ID)
- [ ] 5.4 Add Protovalidate constraints to all request messages
- [ ] 5.5 Run `buf lint` and `buf breaking` against baseline; push to BSR

## 6. Go Backend — User Auth (WebAuthn)

- [ ] 6.1 Add `go-webauthn/webauthn` v0.15.0 dependency; configure `RelyingParty` with origin and RPID
- [ ] 6.2 Implement `BeginRegistration` handler: generate challenge, persist `SessionData` to `webauthn_sessions`
- [ ] 6.3 Implement `FinishRegistration` handler: verify credential, insert `users` row, compute Safe address
- [ ] 6.4 Implement Safe address prediction using `SafeProxyFactory` CREATE2 formula (go-ethereum/crypto)
- [ ] 6.5 Implement `BeginAuthentication` handler: look up credential by username/user handle, generate challenge
- [ ] 6.6 Implement `FinishAuthentication` handler: verify assertion, return signed JWT
- [ ] 6.7 Write unit tests for challenge round-trip and Safe address determinism

## 7. Go Backend — Ticket Minting (ERC-4337 + ERC-5192)

- [ ] 7.1 Generate Go bindings for `TicketSBT` ABI using `abigen`
- [ ] 7.2 Generate Go bindings for `SafeProxyFactory` and `Safe4337Module` ABIs using `abigen`
- [ ] 7.3 Implement `MintTicket` handler: sign and send mint transaction from backend service EOA via `go-ethereum/ethclient`
- [ ] 7.4 Make mint idempotent: check `tickets` table and on-chain `ownerOf` before submitting transaction
- [ ] 7.5 Add retry logic with exponential backoff for Base Sepolia RPC calls
- [ ] 7.6 Store minted token ID and tx hash in `tickets` table on success

## 8. Go Backend — ZKP Verification

- [ ] 8.1 Add `consensys/gnark` v0.14.0 and `vocdoni/circom2gnark` dependencies
- [ ] 8.2 Load `verification_key.json` at server startup; convert to gnark types via circom2gnark; cache in memory
- [ ] 8.3 Implement `VerifyEntry` handler: parse proof JSON from request, convert via circom2gnark, call `groth16.Verify`
- [ ] 8.4 On successful verification: atomically insert `nullifiers` row (unique constraint = double-entry guard)
- [ ] 8.5 Return structured error on duplicate nullifier (event-specific "already checked in" response)
- [ ] 8.6 Write integration test: round-trip a known circom-generated proof through circom2gnark → gnark Verify
- [ ] 8.7 Write integration test: duplicate nullifier returns correct error

## 9. Frontend — Aurelia 2 PWA Foundation

- [ ] 9.1 Add `manifest.json` with correct icons (192px, 512px), `display: standalone`, `start_url`
- [ ] 9.2 Configure `vite-plugin-pwa` v1.2.0 in `injectManifest` mode; set `maximumFileSizeToCacheInBytes: 60MB`
- [ ] 9.3 Author `sw.ts`: precache app shell via `self.__WB_MANIFEST`; add `registerRoute` for `.wasm` and `.zkey` (CacheFirst, 30-day expiry, cache name `zk-circuits-v1`)
- [ ] 9.4 Verify Service Worker registers and caches circuit files on first load (Chrome DevTools → Application)
- [ ] 9.5 Verify A2HS install prompt appears on Android Chrome and iOS Safari (Add to Home Screen)
- [ ] 9.6 Verify offline load after first visit (disconnect network, reload)

## 10. Frontend — Passkey Auth UI

- [ ] 10.1 Add `@simplewebauthn/browser` v13.2.2 dependency
- [ ] 10.2 Implement registration flow: call `BeginRegistration` RPC → `startRegistration()` → `FinishRegistration` RPC
- [ ] 10.3 Implement authentication flow: call `BeginAuthentication` RPC → `startAuthentication({ useBrowserAutofill: true })` → `FinishAuthentication` RPC
- [ ] 10.4 Store returned JWT in secure storage (HttpOnly cookie preferred; fallback sessionStorage)
- [ ] 10.5 Show authenticator type hint (`preferredAuthenticatorType: 'localDevice'`) on registration
- [ ] 10.6 Handle errors: credential already exists, user cancelled, timeout

## 11. Frontend — ZKP Entry Code Generation

- [ ] 11.1 Add `snarkjs` dependency; confirm it loads correctly as ES module in Aurelia 2 / Vite
- [ ] 11.2 Move proof generation into a Web Worker (`proof.worker.ts`) to avoid blocking main thread
- [ ] 11.3 Implement `generateProof(trapdoor, nullifierSecret, merkleRoot, pathElements, pathIndices)` in worker
- [ ] 11.4 Fetch Merkle path from backend `VerifyEntry` preparation endpoint (or dedicated `GetMerklePath` RPC) before generating proof
- [ ] 11.5 Display proof result as QR code (encode proof JSON + event ID as base64 payload)
- [ ] 11.6 Show progress indicator during proof generation (expected 3–30s depending on device)

## 12. Frontend — Ticket Display

- [ ] 12.1 Implement `ListTicketsForUser` call on authenticated home screen
- [ ] 12.2 Display ticket details: event name, date, token ID, SBT status
- [ ] 12.3 Show "Generate Entry Code" button for each ticket; navigate to proof generation flow

## 13. CI / CD

- [ ] 13.1 Add GitHub Actions workflow: `buf lint` + `buf breaking` on proto changes
- [ ] 13.2 Add GitHub Actions workflow: Go backend `go test ./...` + `golangci-lint`
- [ ] 13.3 Add GitHub Actions workflow: frontend `npm run build` + PWA manifest validation
- [ ] 13.4 Add GitHub Actions workflow: deploy backend to GKE dev on merge to main
- [ ] 13.5 Add GitHub Actions workflow: deploy frontend to CDN on merge to main
- [ ] 13.6 Add integration test job: spin up local Bundler (Rundler) + Anvil fork of Base Sepolia; run UserOperation ABI encoding tests
