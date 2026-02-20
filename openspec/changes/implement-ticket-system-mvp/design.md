## Context

The current Liverty Music platform handles concert discovery and notifications. This design introduces a Ticket System MVP to tackle scalping and fraud in the Japanese live music market. The MVP takes a **Hybrid Architecture** approach: a Go backend handles auth, on-chain interactions, and proof verification, while the Aurelia 2 PWA frontend handles the user experience including client-side ZKP generation.

The MVP targets **Base Sepolia** (testnet) and deploys the backend on **GKE Autopilot (Osaka)**. It connects to existing infrastructure via the `cloud-provisioning` repo.

## Goals / Non-Goals

**Goals:**
- Implement Soulbound Ticket (ERC-5192) minting and ownership verification
- Implement Passkey (WebAuthn/FIDO2) based user authentication with Smart Account mapping
- Implement client-side ZKP (Groth16) generation in the PWA for privacy-preserving entry
- Implement off-chain ZKP verification in the Go backend for low-latency, zero-gas check-in
- Deliver a PWA with offline capability (A2HS-compatible, Service Worker caching of ZK circuits)

**Non-Goals:**
- On-chain ZKP verification (gas cost prohibitive for MVP)
- Ticket secondary market / controlled resale mechanisms (post-MVP)
- Production mainnet deployment
- Native mobile apps (iOS/Android)
- Full Account Abstraction (ERC-4337) paymaster integration in MVP (future work)

## Decisions

### Decision 1: Hybrid Architecture (Go Backend + PWA Frontend)

**Choice**: Go backend service (Connect RPC on GKE) + Aurelia 2 PWA

**Rationale**: A browser-only approach was rejected because:
- FIDO2 server-side challenge management requires stateful backend
- Private key / contract interaction (minting) must not occur in the browser
- ZKP verification is performance-sensitive and should be centralized for consistency

**Alternatives considered**:
- *Browser-only*: Rejected due to inability to securely manage minting authorization and WebAuthn challenge state
- *Native apps*: Rejected due to development cost and distribution friction for MVP

---

### Decision 2: Connect RPC (not REST/gRPC) for Backend API

**Choice**: Connect RPC with Protocol Buffers (proto3) over HTTP

**Rationale**: Consistent with the existing Liverty architecture. Connect is compatible with gRPC and JSON clients, supports both browser and server. Protovalidate provides declarative field validation in the same proto files as the schema.

**Alternatives considered**:
- *REST + OpenAPI*: Rejected; less type-safe end-to-end, duplicates schema definition
- *gRPC*: Rejected for browser clients; requires gRPC-web proxy

---

### Decision 3: Off-Chain ZKP Verification

**Choice**: Go backend verifies Groth16 proofs using `gnark` (v0.14.0) with the `vocdoni/circom2gnark` adapter; proofs arrive via Connect RPC.

**Rationale**: On-chain verification (Solidity verifier) costs gas per entry and introduces latency. The event operator controls the backend, so off-chain verification is trusted for the MVP. Nullifier hashes are stored in the backend database (not on-chain) to prevent double-entry.

**Implementation detail**: The frontend generates proofs with `snarkjs` (circom ecosystem). `gnark` does not natively parse snarkjs JSON proof format, so `vocdoni/circom2gnark` is required to convert the proof and verification key. The verification key is loaded once at startup and cached in memory. The adapter handles BN254 curve parameter translation between the two ecosystems.

**Trade-off**: Verification is centralized in the backend, which is a trust assumption. This is acceptable for MVP but should be migrated to on-chain verification for production. The circom2gnark adapter adds a thin dependency; its correctness must be validated in integration tests.

**Alternatives considered**:
- *On-chain verifier contract*: Rejected for MVP due to gas cost and latency
- *Trusted third-party verifier*: Rejected due to dependency and integration complexity
- *`go-rapidsnark/verifier`*: Supports snarkjs JSON natively, but license is unclear and the library is less actively maintained than gnark. Rejected in favor of gnark + circom2gnark.
- *`go-circom-prover-verifier`*: Abandoned since 2020. Rejected.

---

### Decision 4: Passkey → Safe (ERC-4337) Smart Account Mapping

**Choice**: On registration, the backend derives a **predicted Safe address** deterministically from the Passkey credential ID (or public key). This address is stored in the `users` table and used as the SBT recipient.

**Rationale**: Safe's `predictSafeAddress` API allows deterministic address computation without deploying the contract. The actual deployment is deferred (lazy deployment / counterfactual wallet). This avoids gas costs at registration while enabling on-chain identity.

**Implementation detail**: No maintained Go SDK exists for ERC-4337 Account Abstraction (stackup-go archived Oct 2024, thirdweb Go SDK archived May 2024, no official Safe Go SDK). The backend constructs `UserOperation` structs manually using `go-ethereum` ABI encoding, then submits them to a Bundler (Pimlico or Alchemy) via standard `eth_sendUserOperation` JSON-RPC calls over `net/http`. Safe address prediction uses the `SafeProxyFactory` `CREATE2` formula computed on the backend without an external SDK.

**Alternatives considered**:
- *EOA Wallet*: Rejected; requires private key management by the user, breaks the Passkey UX promise
- *Deploy on registration*: Rejected due to gas cost and latency at signup
- *stackup-go / thirdweb Go SDK*: Both archived and unmaintained as of 2024. Rejected.
- *TypeScript AA SDK via sidecar*: Rejected; adds operational complexity and a cross-language RPC boundary

---

### Decision 5: Client-Side ZKP with WASM Circuits via Service Worker

**Choice**: `snarkjs` (latest stable) runs the `TicketCheck` Groth16 circuit WASM in the browser. The circuit WASM and ZKey files are cached by the Service Worker using a **runtime cache strategy** (Cache-First with versioned URLs), managed via `vite-plugin-pwa` (v1.2.0) in `injectManifest` mode with Workbox 7.4.0.

**Rationale**: Proof generation exposes the user's **Identity Trapdoor** (private input). Sending this to the backend would break the privacy guarantee of ZKP. Client-side generation keeps the private input local. Caching the circuit enables offline proof generation — critical for venue entry where connectivity may be unreliable.

**Implementation detail**: The `.zkey` file for the `TicketCheck` circuit is expected to be 5–30 MB. This exceeds Workbox's default `maximumFileSizeToCacheInBytes` limit (2 MB for precache). The circuit artifacts are therefore served from a CDN with versioned paths (e.g., `/circuits/ticketcheck-v1.zkey`) and cached via a Workbox `registerRoute` runtime handler using `CacheFirst` strategy. Cache invalidation is triggered by deploying a new versioned URL on circuit upgrade. The `injectManifest` mode is required (over `generateSW`) because the custom routing logic cannot be expressed in the declarative `generateSW` config.

**WebAuthn client library**: `@simplewebauthn/browser` (v13.2.2). The previously-considered `@github/webauthn-json` was archived in August 2025 (browsers now implement native JSON parsing for WebAuthn); it is not used.

**Alternatives considered**:
- *Backend proof generation*: Rejected; requires sending private input to server, defeating ZKP privacy
- *Native WASM outside browser*: Out of scope for PWA-first strategy
- *Noir / UltraHonk circuits*: Rejected; proof system is incompatible with the gnark Groth16 verifier on the backend
- *Precache for .zkey files*: Rejected; file size exceeds Workbox precache limits and would block Service Worker installation

---

### Decision 6: PWA over Native App

**Choice**: Aurelia 2 PWA with `manifest.json`, Service Worker, and A2HS prompts.

**Rationale**: PWA eliminates app store distribution overhead for MVP. iOS 16.4+ and modern Android support reliable service workers. A single codebase serves both mobile and desktop, reducing development cost.

**Alternatives considered**:
- *React Native / Flutter*: Rejected for MVP due to cost and timeline
- *Progressive Enhancement only (no SW)*: Rejected; offline ZK circuit caching is a hard requirement

---

### Decision 7: Database Schema (PostgreSQL via Cloud SQL)

New tables required:

| Table | Purpose |
|---|---|
| `users` | Passkey credentials, Smart Account address |
| `events` | Concert/event metadata |
| `tickets` | SBT ownership records (token ID, owner) |
| `merkle_tree` | Merkle tree nodes for ZKP identity set |
| `nullifiers` | Used nullifier hashes (double-entry prevention) |

**Rationale**: Nullifiers are stored off-chain in PostgreSQL for fast lookup and atomic writes. Merkle tree nodes must be consistent between proof generation (client) and verification (backend), so the backend maintains the canonical tree.

---

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| ZKP client-side performance (WASM is slow on low-end devices) | Runtime-cache circuits; show progress indicator; test on low-end Android (target: <30s for depth-20 Merkle proof) |
| Service Worker runtime cache size (.zkey 5–30 MB per circuit version) | Version URLs; evict old cache entries on SW activation; monitor Cache Storage quota |
| gnark / circom2gnark proof format incompatibility (BN254 field encoding) | Write integration test that round-trips a known circom proof through circom2gnark → gnark Verify before any production deploy |
| Off-chain nullifier DB as single point of failure for entry | Replicated Cloud SQL with failover; entry degraded to manual check if DB is down |
| Passkey compatibility on older iOS/Android | Minimum iOS 16.4 / Android 9; document this; provide fallback instructions |
| GKE Autopilot cold start latency for Connect RPC handlers | Pre-warm pods; set minimum replicas > 0 |
| Base Sepolia testnet instability | Retry logic in minting handler; idempotent mint (check existing token before minting) |
| Smart Account address prediction diverges from deployed Safe | Use exact same `initializer` and `saltNonce` in prediction and future deployment |
| No maintained Go AA SDK — manual UserOperation construction is error-prone | Unit-test ABI encoding against known good vectors from the ERC-4337 spec; integration-test against a local Bundler (Rundler) in CI |

## Library Selection (as of 2026-02-20)

| Domain | Library | Version | Notes |
|---|---|---|---|
| Go ZKP verification | `consensys/gnark` | v0.14.0 | Groth16 on BN254; most actively maintained Go ZKP library |
| Go ZKP format adapter | `vocdoni/circom2gnark` | latest | Converts snarkjs JSON proof/vkey → gnark types; required bridge |
| Go WebAuthn server | `go-webauthn/webauthn` | v0.15.0 (Nov 2025) | Only actively maintained Go FIDO2 server library |
| Go blockchain | `go-ethereum/ethclient` | v1.15.x | EVM interaction; UserOperation ABI encoding |
| Go HTTP bundler client | `net/http` (stdlib) | — | Direct JSON-RPC to Pimlico/Alchemy bundler; no AA SDK used |
| Browser ZKP generation | `snarkjs` | latest stable | Only production-ready circom/Groth16 JS library |
| Browser WebAuthn | `@simplewebauthn/browser` | v13.2.2 | Actively maintained; `@github/webauthn-json` archived Aug 2025 |
| PWA / Service Worker | `vite-plugin-pwa` + Workbox | v1.2.0 / v7.4.0 | `injectManifest` mode for custom ZK circuit runtime caching |

---

## Migration Plan

1. **Infrastructure**: Provision GKE Autopilot cluster + Cloud SQL (PostgreSQL) in `cloud-provisioning` (separate PR).
2. **Smart Contracts**: Deploy `TicketSBT` to Base Sepolia; record contract address in backend config.
3. **Backend**: Deploy Go service to GKE; run DB migrations; configure Secret Manager for contract keys.
4. **Frontend**: Deploy PWA to CDN/Firebase Hosting; verify Service Worker registration and A2HS prompt.
5. **Circuit**: Compile `TicketCheck` Groth16 circuit; publish WASM + ZKey to CDN; update Service Worker cache manifest.
6. **Rollback**: Backend is stateless (state in DB + blockchain); rolling back the Deployment to previous image is sufficient. DB migrations must be backward-compatible.

## Open Questions

- **Circuit trusted setup**: Who performs the Powers of Tau ceremony for `TicketCheck`? Using a public setup (Hermez) vs. project-specific?
- **Merkle tree leaf format**: What inputs constitute an identity leaf (credential ID hash? public key hash?)? Must be finalized before circuit compilation. Use **Poseidon** (not MiMC) as the hash function — benchmarks show Poseidon2 reduces Groth16 proof generation time by ~60% vs MiMC for equivalent depth circuits. Keep tree depth ≤ 20 to stay under 30 s on low-end mobile.
- **Paymaster integration**: The proposal mentions sponsoring gas fees for minting. Is paymaster in-scope for this MVP or deferred?
- **Operator role**: Who has the `MINTER_ROLE` on `TicketSBT`? The Go backend service account key, or a multisig? Needs security review.
- **Event creation flow**: How are `events` and `merkle_tree` entries populated — admin UI, API, or manual seeding for MVP?
