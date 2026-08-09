# Security Audit Report: implement-ticket-system-mvp

> Audited: 2026-02-23
> Scope: Backend (Go), Frontend (Aurelia 2 PWA), Smart Contracts (Solidity), ZK Circuit (circom), Proto definitions, DB schema

## Summary

Comprehensive security audit of the ticket system MVP implementation across all layers. The audit focused on on-chain interaction safety, ZKP correctness, concurrency, input validation, and cryptographic implementation.

**Overall Assessment**: The architecture is well-designed with strong foundations (idempotent minting, atomic nullifier insertion, parameterized SQL). Critical issues are concentrated in the on-chain transaction management layer.

---

## CRITICAL Findings

### C-1: Transaction Receipt Not Confirmed

**Location**: `backend/internal/infrastructure/blockchain/ticketsbt/client.go` — `Mint()`

`contract.Mint()` returns the tx hash immediately after submission, without waiting for the transaction to be mined. The DB records the ticket as successfully minted based solely on the tx hash, but:

- The tx could revert after being mined (gas, contract logic)
- The tx could remain stuck in the mempool (nonce collision, low gas price)
- A chain reorg could drop the tx entirely

**Impact**: Users see "ticket minted" but the token may not exist on-chain.

**Fix**: Call `bind.WaitMined()` after `contract.Mint()` and check `receipt.Status == types.ReceiptStatusSuccessful` before persisting to DB.

---

### C-2: No Nonce Management

**Location**: `backend/internal/infrastructure/blockchain/ticketsbt/client.go`

The client relies on `bind.TransactOpts` auto-nonce. If the backend crashes during a mint or concurrent mint requests arrive:

- Stale nonce state can cause all future mints to fail with "nonce too low"
- Concurrent mints may submit duplicate nonces, causing one to fail

**Fix**: Add a `sync.Mutex` to serialize mint calls. Explicitly fetch `PendingNonceAt()` before each submission.

---

### C-3: Retry Logic Does Not Distinguish Error Types

**Location**: `backend/internal/infrastructure/blockchain/ticketsbt/client.go` — `Mint()` retry loop

All errors trigger a retry, including permanent failures:

- `execution reverted` (e.g., unauthorized minter) — will never succeed
- `insufficient funds` — will never succeed
- `nonce too low` — stale state, needs correction not retry

**Fix**: Add `isTransientError()` classifier. Only retry network/timeout errors. Return immediately on revert/permanent errors.

---

## HIGH Findings

### H-1: SafeProxyFactory and initCodeHash Hardcoded

**Location**: `backend/internal/infrastructure/blockchain/safe/address.go`

Constants `SafeProxyFactory = 0x4e1DCf7AD4e460CfD30791CCC4F9c8a4f820ec67` and `safeProxyInitCodeHash` are hardcoded for Safe v1.4.1. If Safe upgrades, all new Safe address predictions break silently.

Additionally, the research document (`evm-aa-go-libraries.md`) lists a different SafeProxyFactory address (`0x914d7Fec6...`), creating documentation-code inconsistency.

**Fix**: Make configurable via `BlockchainConfig` with current values as defaults.

---

### H-2: Merkle Tree Depth Mismatch (Backend=10, Circuit=20)

**Location**: `backend/internal/usecase/entry_uc.go` line 21 vs `frontend/circuits/ticketcheck-v1/ticketcheck.circom`

- Backend: `DefaultTreeDepth = 10` (max 1,024 leaves)
- Circuit: `depth = 20` (max ~1M leaves)

The circuit expects 20 path elements and indices, but backend only returns 10. Proof generation would fail at the circuit level due to input size mismatch.

**Fix**: Set `DefaultTreeDepth = 20` in the backend.

---

### H-3: QR Code Payload is Plaintext Base64

**Location**: `frontend/src/routes/tickets/tickets-page.ts` line 91

The QR code contains `btoa(JSON.stringify({eventId, proof, publicSignals}))`. Base64 is trivially reversible. An attacker who photographs the QR can decode the proof and submit it to `VerifyEntry` before the legitimate user, consuming their nullifier.

**Fix**: Add an expiration timestamp to the payload (`exp: Date.now() + 5 * 60 * 1000`). The backend nullifier check already prevents reuse, but the expiry limits the replay window.

---

### H-4: Trapdoor Derived from Backend-Known Value

**Location**: Frontend `proof-service.ts` line 58: `trapdoor: leaf`

The "trapdoor" (ZKP private input) is the Merkle leaf value `Poseidon(userID)`, which the backend computes and returns via `GetMerklePath`. This means the backend operator can generate proofs for any user.

**Current Acceptability**: MVP design explicitly accepts backend as a trusted party (off-chain verification). This is documented in `design.md` Decision 3.

**Future Risk**: If migrating to on-chain verification, this design breaks the privacy guarantee of ZKP. The trapdoor should be a user-controlled secret (e.g., derived from Passkey credential).

---

## MEDIUM Findings

### M-1: Token Existence Detection via String Matching

**Location**: `backend/internal/infrastructure/blockchain/ticketsbt/client.go` lines 168-169

```go
if strings.Contains(err.Error(), erc721NonexistentTokenSelector) ||
    strings.Contains(err.Error(), "ERC721NonexistentToken") {
```

Fragile — error message format may change across ethclient versions.

**Fix**: Extract 4-byte selector from error data bytes instead of string matching.

---

### M-2: Proto user_id Fields Ignored by Handlers

**Location**: `ticket_service.proto`, `entry_service.proto`

`MintTicketRequest.user_id`, `ListTicketsRequest.user_id`, and `GetMerklePathRequest.user_id` are required in the proto definition but completely ignored by backend handlers (user is derived from JWT claims). This creates a misleading API contract.

**Fix**: Remove these fields from request messages; add `reserved` directives.

---

### M-3: Circuit File Integrity Not Verified

**Location**: `frontend/src/sw.ts`, `frontend/src/services/proof-service.ts`

`.wasm` and `.zkey` files are cached by Service Worker (CacheFirst, 30-day TTL) without integrity verification (no SRI, no hash check). Cache poisoning would persist for 30 days.

**Fix**: Compute SHA-256 hash after fetching and compare against known-good constants.

---

### M-4: No CSP Headers

**Location**: `frontend/index.html`

No Content-Security-Policy meta tag. Combined with OIDC tokens in localStorage (M-5), this makes XSS attacks high-impact.

---

### M-5: OIDC Tokens in localStorage

**Location**: `frontend/src/services/auth-service.ts`

```typescript
userStore: new WebStorageStateStore({ store: window.localStorage })
```

Access tokens in localStorage are vulnerable to XSS. Noted as intentional for Playwright compatibility.

---

### M-6: VerifyEntryResponse.message Unbounded

**Location**: `entry_service.proto`

The `message` string field has no size constraint. Should add `max_len = 256`.

---

## LOW Findings

### L-1: Poseidon Parameter Compatibility Not Documented

No comment explicitly confirms that `iden3/go-iden3-crypto/poseidon` uses the same parameters as `circomlib/poseidon`. Both use BN254, but the parameter set (number of rounds, MDS matrix) must match exactly.

### L-2: Zero Hash Padding Implicit

`merkle/tree.go` uses `make([]byte, 32)` (all zeros) for empty leaf positions. The circuit must use the same zero value.

### L-3: Missing DB CHECK Constraints

- No CHECK on `merkle_tree.depth >= 0`, `node_index >= 0`
- No CHECK on hash field sizes (`octet_length = 32`)
- No CHECK on `users.safe_address` Ethereum address format

### L-4: Push Notification URL No Origin Validation

`sw.ts` `notificationclick` handler passes `data.url` to `openWindow()` without verifying it starts with `self.location.origin`.

### L-5: Incomplete Vite Environment Types

`vite-env.d.ts` missing `VITE_CIRCUIT_BASE_URL`, `VITE_VAPID_PUBLIC_KEY`, `VITE_ZITADEL_ORG_ID`.

---

## Smart Contract Assessment: No Critical Issues

The `TicketSBT` contract (ERC-721 + ERC-5192) is well-implemented:

- Transfer lock complete (both `transferFrom` and `safeTransferFrom` revert)
- Access control via OpenZeppelin `AccessControl` with `MINTER_ROLE`
- `Locked` event emitted on mint per ERC-5192
- ERC-165 interface detection correct
- No reentrancy vectors
- All 7 Foundry tests pass

**Minor Note**: No pause/freeze mechanism. If the MINTER_ROLE key is compromised, there is no on-chain way to stop minting. Acceptable for testnet MVP.

---

## ZK Circuit Assessment: Correct

The `TicketCheck` circom circuit is mathematically sound:

- Nullifier = `Poseidon(trapdoor, eventId)` — correctly prevents double-entry and cross-event replay
- Binary path index constraints enforced
- Correct conditional left/right sibling ordering via multiplication trick
- Final root constraint matches public input

---

## Sources

- `backend/internal/infrastructure/blockchain/ticketsbt/client.go`
- `backend/internal/infrastructure/blockchain/safe/address.go`
- `backend/internal/usecase/entry_uc.go`
- `backend/internal/usecase/ticket_uc.go`
- `backend/internal/infrastructure/zkp/verifier.go`
- `backend/internal/infrastructure/merkle/tree.go`
- `backend/internal/infrastructure/merkle/poseidon.go`
- `backend/internal/infrastructure/database/rdb/nullifier_repo.go`
- `backend/contracts/src/TicketSBT.sol`
- `frontend/circuits/ticketcheck-v1/ticketcheck.circom`
- `frontend/src/services/proof-service.ts`
- `frontend/src/sw.ts`
- `frontend/src/routes/tickets/tickets-page.ts`
- `specification/proto/liverty_music/rpc/ticket/v1/ticket_service.proto`
- `specification/proto/liverty_music/rpc/entry/v1/entry_service.proto`
