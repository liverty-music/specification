## Context

The current Liverty Music platform handles concert discovery and notifications. This design introduces a Ticket System MVP to tackle scalping and fraud in the Japanese live music market. The MVP takes a **Hybrid Architecture** approach: a Go backend handles auth, on-chain interactions, and proof verification, while the Aurelia 2 PWA frontend handles the user experience including client-side ZKP generation.

The MVP targets **Base Sepolia** (testnet) and extends the existing backend on **GKE Autopilot (Osaka)** (`cluster-osaka`) with **Cloud SQL PostgreSQL 18** (`postgres-osaka`, PSC connection). Authentication uses the existing **Zitadel** IdP with Passkey support enabled. The Proto schema is managed via **BSR** (`liverty-music/schema`) with generated code imported by both backend (Go) and frontend (TypeScript).

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

### Decision 4: Authentication via Zitadel (Passkey RP) + Safe Address from users.id

**Choice**: Passkey authentication is handled by **Zitadel as the WebAuthn Relying Party**. The existing OIDC flow (`oidc-client-ts` → Zitadel → JWT) remains unchanged. For MVP, Zitadel's hosted login UI is used. The backend derives a **predicted Safe address** deterministically from the internal `users.id` (UUIDv7), not from the Passkey credential public key.

**Rationale**: Zitadel already manages authentication for the platform (users, OIDC, JWT). Adding a separate WebAuthn RP (go-webauthn) would create two parallel auth systems. Zitadel supports Passkey registration via its v2 API (`POST /v2/users/{user_id}/passkeys`) and returns `PublicKeyCredentialCreationOptions` that can be passed directly to `navigator.credentials.create()`.

**Safe address derivation**: `CREATE2(salt = keccak256(users.id))`. Using the internal UUID rather than `external_id` (Zitadel sub) or credential public key ensures the derivation is **auth-provider-agnostic**. If the auth system changes in the future, existing Safe addresses remain valid.

**Design principle — auth-agnostic identification**: All internal references (tickets, nullifiers, merkle_tree) use `users.id` as the foreign key, never `external_id` or credential-specific values. This allows the auth mechanism to evolve without affecting the ticket system's data model.

**Implementation detail**: No maintained Go SDK exists for ERC-4337 Account Abstraction (stackup-go archived Oct 2024, thirdweb Go SDK archived May 2024, no official Safe Go SDK). The backend constructs `UserOperation` structs manually using `go-ethereum` ABI encoding, then submits them to a Bundler (Pimlico or Alchemy) via standard `eth_sendUserOperation` JSON-RPC calls over `net/http`. Safe address prediction uses the `SafeProxyFactory` `CREATE2` formula computed on the backend without an external SDK.

**Known Zitadel Passkey limitations** (see [research/zitadel-passkey-rp.md](research/zitadel-passkey-rp.md)):
- Credential public key is NOT exported via API (ListPasskeys returns id/state/name only)
- Custom Login UI on a different domain is blocked by Issue #8282 (RPOrigins bug, Open)
- Conditional UI (Passkey autofill) is not supported (Discussion #8867)
- Domain change invalidates all registered Passkeys

**Migration path**: If Zitadel's Passkey limitations become blocking (e.g., Issue #8282 remains unresolved when custom UI is needed), the system can evolve to Option C: Zitadel for existing users + self-hosted go-webauthn RP for ticket-specific Passkey auth. The auth-agnostic `users.id` derivation ensures Safe addresses are unaffected. See [auth-evolution-plan.md](auth-evolution-plan.md) for the detailed migration plan.

**Alternatives considered**:
- *Self-hosted go-webauthn RP (Option B)*: Rejected for MVP; replaces Zitadel entirely, wastes existing auth infrastructure (oidc-client-ts, authn middleware, users.external_id)
- *EOA Wallet*: Rejected; requires private key management by the user, breaks the Passkey UX promise
- *Deploy on registration*: Rejected due to gas cost and latency at signup
- *stackup-go / thirdweb Go SDK*: Both archived and unmaintained as of 2024. Rejected.
- *Safe address from credential public key*: Rejected; Zitadel does not export credential public key via API
- *Safe address from external_id (Zitadel sub)*: Rejected; couples on-chain identity to a specific IdP

---

### Decision 5: Client-Side ZKP with WASM Circuits via Service Worker

**Choice**: `snarkjs` (latest stable) runs the `TicketCheck` Groth16 circuit WASM in the browser. The circuit WASM and ZKey files are cached by the Service Worker using a **runtime cache strategy** (Cache-First with versioned URLs), managed via `vite-plugin-pwa` (v1.2.0) in `injectManifest` mode with Workbox 7.4.0.

**Rationale**: Proof generation exposes the user's **Identity Trapdoor** (private input). Sending this to the backend would break the privacy guarantee of ZKP. Client-side generation keeps the private input local. Caching the circuit enables offline proof generation — critical for venue entry where connectivity may be unreliable.

**Implementation detail**: The `.zkey` file for the `TicketCheck` circuit is expected to be 5–30 MB. This exceeds Workbox's default `maximumFileSizeToCacheInBytes` limit (2 MB for precache). The circuit artifacts are therefore served from a CDN with versioned paths (e.g., `/circuits/ticketcheck-v1.zkey`) and cached via a Workbox `registerRoute` runtime handler using `CacheFirst` strategy. Cache invalidation is triggered by deploying a new versioned URL on circuit upgrade. The `injectManifest` mode is required (over `generateSW`) because the custom routing logic cannot be expressed in the declarative `generateSW` config.

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

### Decision 7: Database Schema (PostgreSQL 18 via Cloud SQL)

The existing PostgreSQL 18 instance (`postgres-osaka`, Cloud SQL with PSC) already hosts `users`, `events`, `concerts`, `artists`, `venues`, and other tables. The ticket system extends this schema with ALTER statements and new tables.

**ALTER existing tables:**

| Table | Change | Purpose |
|---|---|---|
| `users` | ADD `safe_address TEXT` | Predicted Safe (ERC-4337) address derived from `users.id` |
| `events` | ADD `merkle_root BYTEA` (nullable) | ZKP identity set root; NULL for non-ticket events |

**New tables:**

| Table | Purpose |
|---|---|
| `tickets` | SBT ownership records (event_id FK → events, user_id FK → users, token_id, tx_hash) |
| `merkle_tree` | Merkle tree nodes for ZKP identity set (event_id, depth, index, hash) |
| `nullifiers` | Used nullifier hashes with unique index (event_id, nullifier_hash, used_at) |

**Design principle**: All new tables reference `users.id` (internal UUIDv7) as the user identifier, never `users.external_id` (Zitadel sub claim). This ensures the ticket data model is auth-provider-agnostic.

**Rationale**: Nullifiers are stored off-chain in PostgreSQL for fast lookup and atomic writes. Merkle tree nodes must be consistent between proof generation (client) and verification (backend), so the backend maintains the canonical tree. The existing `events` table is extended rather than duplicated because tickets are issued for events — the same entity that already tracks concerts.

---

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| ZKP client-side performance (WASM is slow on low-end devices) | Runtime-cache circuits; show progress indicator; test on low-end Android (target: <30s for depth-20 Merkle proof) |
| Service Worker runtime cache size (.zkey 5–30 MB per circuit version) | Version URLs; evict old cache entries on SW activation; monitor Cache Storage quota |
| gnark / circom2gnark proof format incompatibility (BN254 field encoding) | Write integration test that round-trips a known circom proof through circom2gnark → gnark Verify before any production deploy |
| Off-chain nullifier DB as single point of failure for entry | Replicated Cloud SQL with failover; entry degraded to manual check if DB is down |
| Passkey compatibility on older iOS/Android | Minimum iOS 16.4 / Android 9; document this; provide fallback instructions |
| Zitadel Passkey custom UI blocked (Issue #8282) | MVP uses hosted login UI (unaffected); monitor issue; Option C migration plan ready if unresolved |
| Zitadel does not export credential public key | Safe address derived from users.id (auth-agnostic); no dependency on credential material |
| Zitadel domain change invalidates Passkeys | Finalize custom domain before enabling Passkeys in production |
| GKE Autopilot cold start latency for Connect RPC handlers | Pre-warm pods; set minimum replicas > 0 |
| Base Sepolia testnet instability | Retry logic in minting handler; idempotent mint (check existing token before minting) |
| Smart Account address prediction diverges from deployed Safe | Use exact same `initializer` and `saltNonce` in prediction and future deployment |
| No maintained Go AA SDK — manual UserOperation construction is error-prone | Unit-test ABI encoding against known good vectors from the ERC-4337 spec; integration-test against a local Bundler (Rundler) in CI |

## Library Selection (as of 2026-02-20)

| Domain | Library | Version | Notes |
|---|---|---|---|
| Authentication (IdP) | Zitadel | self-hosted | Existing IdP; Passkey RP for MVP (hosted login UI) |
| Frontend auth client | `oidc-client-ts` | ^3.4.1 | Existing OIDC client; unchanged for MVP |
| Go JWT validation | `lestrrat-go/jwx/v2` | v2.1.6 | Existing JWT validator; issuer list must be configurable |
| Go ZKP verification | `consensys/gnark` | v0.14.0 | Groth16 on BN254; most actively maintained Go ZKP library |
| Go ZKP format adapter | `vocdoni/circom2gnark` | latest | Converts snarkjs JSON proof/vkey → gnark types; required bridge |
| Go blockchain | `go-ethereum/ethclient` | v1.15.x | EVM interaction; UserOperation ABI encoding |
| Go HTTP bundler client | `net/http` (stdlib) | — | Direct JSON-RPC to Pimlico/Alchemy bundler; no AA SDK used |
| Browser ZKP generation | `snarkjs` | latest stable | Only production-ready circom/Groth16 JS library |
| PWA / Service Worker | `vite-plugin-pwa` + Workbox | v1.2.0 / v7.4.0 | `injectManifest` mode for custom ZK circuit runtime caching |

**Removed from original design** (with rationale):
- `go-webauthn/webauthn`: Not needed for MVP; Zitadel is the WebAuthn RP. Reserved for Option C migration if needed.
- `@simplewebauthn/browser`: Not needed for MVP; Zitadel's hosted login UI handles `navigator.credentials`. Reserved for custom Login UI (Pattern 2) or Option C.

**Existing backend libraries** (already in go.mod, used by ticket system):
- `jackc/pgx/v5` v5.8.0 (PostgreSQL driver)
- `connectrpc.com/connect` v1.19.1 (Connect RPC)
- `connectrpc.com/validate` v0.6.0 (Protovalidate)
- `pannpers/go-apperr` v1.0.2 (Error handling)
- `pannpers/go-logging` v1.1.0 (Structured logging)

---

## Migration Plan

1. **Infrastructure**: GKE Autopilot (`cluster-osaka`) and Cloud SQL (`postgres-osaka`) already exist. Add Secret Manager entries for contract private key. Configure Zitadel Passkey settings.
2. **Proto / BSR**: Define new services (`TicketService`, `EntryService`) in `liverty-music/schema` BSR module. Push to BSR; generated Go/TS code auto-updates via dependency version bump.
3. **Database**: Run ALTER migrations (`users` + `events`) and CREATE migrations (`tickets`, `merkle_tree`, `nullifiers`). All migrations must be backward-compatible.
4. **Smart Contracts**: Deploy `TicketSBT` to Base Sepolia; record contract address in Secret Manager.
5. **Backend**: Add ticket/entry handlers to existing Go service. Deploy to GKE via existing CD pipeline.
6. **Circuit**: Compile `TicketCheck` Groth16 circuit; publish WASM + ZKey to CDN with versioned paths.
7. **Frontend**: Add PWA features (`vite-plugin-pwa`, Service Worker) and ticket UI to existing Aurelia 2 app. Deploy via existing CD pipeline.
8. **Rollback**: Backend is stateless (state in DB + blockchain); rolling back the Deployment to previous image is sufficient. DB migrations must be backward-compatible.

## Open Questions

- **Circuit trusted setup**: Who performs the Powers of Tau ceremony for `TicketCheck`? Using a public setup (Hermez) vs. project-specific?
- **Merkle tree leaf format**: What inputs constitute an identity leaf (credential ID hash? public key hash?)? Must be finalized before circuit compilation. Use **Poseidon** (not MiMC) as the hash function — benchmarks show Poseidon2 reduces Groth16 proof generation time by ~60% vs MiMC for equivalent depth circuits. Keep tree depth ≤ 20 to stay under 30 s on low-end mobile.
- **Paymaster integration**: The proposal mentions sponsoring gas fees for minting. Is paymaster in-scope for this MVP or deferred?
- **Operator role**: Who has the `MINTER_ROLE` on `TicketSBT`? The Go backend service account key, or a multisig? Needs security review.
- **Event creation flow**: How are `events` and `merkle_tree` entries populated — admin UI, API, or manual seeding for MVP?
