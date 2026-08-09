## Why

A fair, forward-looking assessment (MVP **and** future extensibility) concluded that every blockchain-unique property in the ticket system — SBT non-transferability, on-chain minting, ERC-4337 Smart Accounts, ZKP membership entry — only becomes load-bearing when the platform crosses a trust boundary (an open multi-promoter secondary market, cross-platform composability). None of those are on Liverty's roadmap: the product is a **walled-garden**, single-operator concert platform (Scenario A). Within that boundary a Web2 architecture (account-bound tickets + signed rotating QR + Passkey) meets every functional and regulatory requirement at equal or higher quality, without the blockchain stack's cost and risk surface (heavy crypto dependencies, a `circom2gnark` bridge, a trusted-setup ceremony, testnet instability, a custodial contract private key, and 5–30 MB circuit downloads with 3–30 s mobile proof generation).

This change **removes the shipped-but-dormant blockchain ticket implementation** so the codebase stops carrying dead weight and attack surface. The Web2 replacement is deliberately scoped as a **separate follow-up change** — removal and rebuild are not mixed.

## What Changes

- **BREAKING** Remove the `TicketService` (`MintTicket`, `GetTicket`, `ListTickets`) and `EntryService` (`GetMerklePath`, `VerifyEntry`) from the proto schema and BSR. Requires the `buf skip breaking` label.
- Remove the backend blockchain stack: `contracts/` (Foundry + `TicketSBT.sol`), `configs/zkp/`, `internal/infrastructure/blockchain/`, `internal/infrastructure/zkp/`, `internal/infrastructure/merkle/`, and the entry/ticket-mint/merkle/nullifier entities, use cases, handlers, repositories, mocks, and DI wiring.
- Remove the backend crypto dependencies (`consensys/gnark`, `vocdoni/circom2gnark`, `ethereum/go-ethereum`, `gnark-crypto`, `icicle-gnark`) from `go.mod` and run `go mod tidy`.
- Remove the frontend ZKP stack: `circuits/`, `prover/`, `public/circuits/`, the `tickets` route, `proof.worker.ts`, `proof-service.ts`, `entry-client.ts`, `ticket-client.ts`, `ticket-store.ts`, and the PWA circuit-precache handling.
- Drop the blockchain schema via a forward migration: `DROP TABLE tickets, merkle_tree, nullifiers`; `ALTER users DROP COLUMN safe_address`; `ALTER events DROP COLUMN merkle_root`.
- Retire the `ENTRY` and `TICKET` JetStream streams and the `ticket.mint.completed` / `entry.zk_proof.verified` analytics events, taking care not to wedge the preserved `TICKET_JOURNEY` and `TICKET_EMAIL` consumers.
- Deprovision the Base Sepolia contract deployer key, RPC URL, and Bundler API key from Secret Manager (`cloud-provisioning`).
- Supersede the in-flight blockchain proposals: mark `implement-ticket-system-mvp` (72/79) and `sbt-formal-verification` (0/34) as withdrawn/obsolete under Scenario A.

**Preserved (NOT touched):** the Web2 ticket features `ticket-journey` (interest-tier funnel / status UI, in production) and `ticket-email-import` (email ingestion), plus general `user-auth`, `authentication`, and PWA capabilities. Passkey auth via Zitadel stays — it was never blockchain-specific.

## Capabilities

### New Capabilities

- _None._ This change is purely a removal. The Web2 ticket system is a separate follow-up change.

### Modified Capabilities

**Removed in full** (each spec is deleted via a REMOVED delta):
- `ticket-management`: the on-chain `TicketService` (SBT mint/get/list) capability.
- `ticket-minting-internals`: the `MintTicket` on-chain orchestrator sub-method structure.
- `zkp-entry`: the `EntryService` ZKP entry capability (`GetMerklePath`, `VerifyEntry`).
- `client-zk-proving`: the browser-side Groth16 proving runtime capability.
- `sbt-test-coverage`: the `TicketSBT` Solidity contract test requirements.
- `sbt-static-analysis`: the Slither / `forge snapshot` contract-CI requirements.

**Partially modified** (blockchain requirements stripped, the rest kept):
- `database`: remove the `tickets.minted_at` / `nullifiers.used_at` column-naming requirements.
- `product-analytics`: remove `ticket.mint.completed` and `entry.zk_proof.verified` from the event catalogue (keep the Web2 `ticket.email.parsed`).
- `entity-domain-logic`: remove the `ParseZKPPublicSignals` / `ZKPPublicSignals` requirement.
- `frontend-testing`: remove the `proof-service` pure-utility test requirement.
- `frontend-store-cache`: remove `Entry.getMerklePath` from the network-first resource set.
- `live-events`: remove `merkle root` from the optional event fields.

## Impact

- **Proto / BSR** (`specification`): breaking removal of two services + blockchain entity messages; new BSR release; downstream Go/TS dependency bumps.
- **Backend** (`backend`): large deletion across `entity`, `usecase`, `adapter/rpc`, `infrastructure`, `contracts`, `configs`; `go.mod` slimming; one forward DROP migration (backward-compatible — no reader depends on the dropped columns/tables); JetStream stream retirement.
- **Frontend** (`frontend`): removal of circuits, WASM prover, tickets route, and proof workers; PWA service-worker precache simplification; bundle-size reduction.
- **Cloud provisioning** (`cloud-provisioning`): Secret Manager entries removed via Pulumi; Base Sepolia deployment abandoned (testnet, no action needed beyond dropping the recorded address).
- **Risk**: dormant feature (frontend nav already hidden, backend handlers unreachable without dev secrets), so removal is low user-facing risk. Primary care points are JetStream durable/stream retirement ordering and the applied-migration DROP.
