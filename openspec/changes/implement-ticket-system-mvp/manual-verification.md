# Manual Verification Runbook

This document provides step-by-step instructions for verifying the features introduced in the `implement-ticket-system-mvp` change. It covers:

- **Sections 10.x**: PWA (Service Worker, A2HS, Offline)
- **Sections 11.x**: Passkey Authentication
- **Sections 12.x**: Ticket System (UC1–UC7)

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [12.0 — Environment Setup for Ticket System](#120--environment-setup-for-ticket-system)
- [12.1 — UC1: Mint a Ticket (MintTicket RPC)](#121--uc1-mint-a-ticket-mintticket-rpc)
- [12.2 — UC2: Get Ticket Details (GetTicket RPC)](#122--uc2-get-ticket-details-getticket-rpc)
- [12.3 — UC3: List My Tickets (ListTickets RPC)](#123--uc3-list-my-tickets-listtickets-rpc)
- [12.4 — UC4: Get Merkle Path (GetMerklePath RPC)](#124--uc4-get-merkle-path-getmerklepath-rpc)
- [12.5 — UC5: Generate Entry QR Code (Frontend)](#125--uc5-generate-entry-qr-code-frontend)
- [12.6 — UC6: Verify Entry (VerifyEntry RPC)](#126--uc6-verify-entry-verifyentry-rpc)
- [12.7 — UC7: Build Merkle Tree (Backend Internal)](#127--uc7-build-merkle-tree-backend-internal)
- [12.8 — End-to-End Flow](#128--end-to-end-flow)
- [10.4 — Service Worker Caches Circuit Files](#104--service-worker-caches-circuit-files)
- [10.5 — A2HS (Add to Home Screen) Install Prompt](#105--a2hs-add-to-home-screen-install-prompt)
- [10.6 — Offline Load After First Visit](#106--offline-load-after-first-visit)
- [11.1 — OIDC Flow Supports Passkey via Zitadel](#111--oidc-flow-supports-passkey-via-zitadel)
- [11.2 — Passkey Registration](#112--passkey-registration)
- [11.3 — Passkey Authentication](#113--passkey-authentication)
- [11.4 — Supported Browsers and OS Versions for Passkey](#114--supported-browsers-and-os-versions-for-passkey)

---

## Prerequisites

- Frontend running locally (`npm run dev`) or deployed to `https://dev.liverty-music.app`
- Backend running locally or deployed to `https://api.dev.liverty-music.app`
- Zitadel dev instance accessible: `https://dev-svijfm.us1.zitadel.cloud`
- Devices for testing:
  - Desktop: Chrome 120+ (Windows/macOS/Linux)
  - Android: Chrome 120+ on Android 9+
  - iOS: Safari 17+ on iOS 16.4+
- Tools installed:
  - `curl` (for API calls)
  - `jq` (for JSON formatting — optional but recommended)
  - `psql` (for database verification)
  - `kubectl` (for cluster access, if verifying deployed environment)

---

## 12.0 — Environment Setup for Ticket System

Before verifying ticket system use cases, several backend prerequisites must be met.

### 12.0.1 — Required Environment Variables

The ticket system requires specific environment variables to be set on the backend. Without these, the services will not register and API calls will return `404 Not Found`.

#### For TicketService (MintTicket, GetTicket, ListTickets)

| Variable | Description | Example |
|----------|-------------|---------|
| `BASE_SEPOLIA_RPC_URL` | EVM JSON-RPC endpoint (Base Sepolia) | `https://base-sepolia.g.alchemy.com/v2/YOUR_KEY` |
| `CHAIN_ID` | EIP-155 chain ID | `84532` (Base Sepolia) |
| `TICKET_SBT_DEPLOYER_KEY` | Hex private key with MINTER_ROLE on TicketSBT | `0xabc123...` |
| `TICKET_SBT_ADDRESS` | Deployed TicketSBT contract address | `0x1234...abcd` |
| `SAFE_PROXY_FACTORY` | Safe ProxyFactory address (default provided) | `0x4e1DCf7AD4e460CfD30791CCC4F9c8a4f820ec67` |
| `SAFE_INIT_CODE_HASH` | keccak256 of Safe proxy creation bytecode (default provided) | `0x52bede28...` |

#### For EntryService (VerifyEntry, GetMerklePath)

| Variable | Description | Example |
|----------|-------------|---------|
| `ZKP_VERIFICATION_KEY_PATH` | Path to snarkjs `verification_key.json` | `/app/circuits/verification_key.json` |

**How to check if services are registered:**

```bash
# If TicketService is NOT registered, you'll get a 404:
curl -s -o /dev/null -w "%{http_code}" \
  -X POST https://api.dev.liverty-music.app/liverty_music.rpc.ticket.v1.TicketService/ListTickets \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{}'

# 200 or 401 = service registered
# 404 = service NOT registered (env vars missing)
```

### 12.0.2 — Obtain a JWT Access Token

All ticket/entry RPCs (except `VerifyEntry`) require a valid JWT. You can obtain one by:

**Option A: Browser DevTools (recommended for beginners)**

1. Open `https://dev.liverty-music.app` in Chrome.
2. Sign in with Passkey (see Section 11).
3. Open DevTools (`F12`) → **Application** tab → **Local Storage** → select the app URL.
4. Find the key containing `access_token` (from the OIDC session).
5. Copy the token value.

**Option B: oidc-client-ts callback inspection**

1. Open DevTools → **Network** tab.
2. Sign in.
3. Look for the token endpoint response in the network log.
4. Copy the `access_token` from the response body.

**Store the token for use in subsequent commands:**

```bash
export TOKEN="eyJhbGciOiJSUzI1NiIs..."
```

### 12.0.3 — Seed Test Data (Events and Venues)

The ticket system requires existing events in the database. No seed data is created automatically — you must insert it manually.

**Connect to the dev database:**

```bash
# Via kubectl port-forward (if using GKE):
kubectl port-forward -n backend svc/postgres 5432:5432

# Then connect:
psql -h localhost -U postgres -d liverty_music
```

**Insert a test venue and event:**

```sql
-- Create a test venue (if none exists)
INSERT INTO venues (id, name, address, capacity)
VALUES (
  'a0000000-0000-0000-0000-000000000001',
  'Test Venue Tokyo',
  '1-1-1 Shibuya, Tokyo',
  500
)
ON CONFLICT (id) DO NOTHING;

-- Create a test event (if none exists)
INSERT INTO events (id, venue_id, title, starts_at, ends_at)
VALUES (
  'e0000000-0000-0000-0000-000000000001',
  'a0000000-0000-0000-0000-000000000001',
  'Test Concert 2026',
  '2026-03-15 18:00:00+09',
  '2026-03-15 22:00:00+09'
)
ON CONFLICT (id) DO NOTHING;
```

**Verify:**

```sql
SELECT id, title, starts_at FROM events WHERE id = 'e0000000-0000-0000-0000-000000000001';
```

> **Note**: The exact column names may vary depending on the current schema. Use `\d events` and `\d venues` to check the actual table structure if the above INSERT fails.

### 12.0.4 — Verify User Exists in Database

When you sign in via Passkey, the backend syncs the Zitadel user to the `users` table. Confirm your user exists:

```sql
SELECT id, external_id, safe_address FROM users WHERE external_id = 'YOUR_ZITADEL_USER_ID';
```

The `external_id` matches the JWT `sub` claim. The `safe_address` will be `NULL` until the first ticket mint.

---

## 12.1 — UC1: Mint a Ticket (MintTicket RPC)

**Goal**: Verify that an authenticated user can mint a soulbound ticket (ERC-5192) for an event.

### What Happens Behind the Scenes

1. Backend extracts `user_id` from JWT `sub` claim (resolved via `users.external_id`).
2. If the user has no `safe_address`, a deterministic Safe (ERC-4337) address is computed via CREATE2 and persisted.
3. An ERC-5192 soulbound token is minted on-chain to the user's Safe address.
4. The ticket record is stored in the `tickets` table.
5. The user's identity commitment is added to the event's Merkle tree (for ZKP entry).

### Steps

**1. Call MintTicket via curl:**

```bash
curl -s -X POST \
  https://api.dev.liverty-music.app/liverty_music.rpc.ticket.v1.TicketService/MintTicket \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{
    "event_id": "e0000000-0000-0000-0000-000000000001"
  }' | jq .
```

**2. Expected successful response:**

```json
{
  "ticket": {
    "id": "01968abc-...",
    "eventId": "e0000000-0000-0000-0000-000000000001",
    "userId": "your-internal-user-uuid",
    "tokenId": "1",
    "txHash": "0xabc123...64-hex-chars",
    "mintTime": "2026-02-23T12:00:00Z"
  }
}
```

**3. Save the ticket ID for later steps:**

```bash
export TICKET_ID="01968abc-..."
```

### Verification Checklist

| Check | How to Verify | Expected |
|-------|---------------|----------|
| HTTP status | Check curl response code | `200` |
| Ticket ID | `ticket.id` in response | Non-empty UUIDv7 |
| Token ID | `ticket.tokenId` in response | Positive integer |
| TX Hash | `ticket.txHash` in response | `0x` + 64 hex chars |
| DB record | `SELECT * FROM tickets WHERE id = '...'` | Row exists |
| Safe address | `SELECT safe_address FROM users WHERE id = '...'` | Non-null `0x...` address |
| Merkle tree | `SELECT COUNT(*) FROM merkle_tree WHERE event_id = 'e0...'` | At least 1 node |

### Error Cases

| Error | HTTP Status | Connect Code | Cause |
|-------|-------------|--------------|-------|
| Missing/invalid JWT | 401 | `unauthenticated` | No `Authorization` header or expired token |
| User not found | 404 | `not_found` | JWT `sub` not matching any `users.external_id` |
| Event not found | 404 | `not_found` | Invalid `event_id` |
| Duplicate ticket | 409 | `already_exists` | User already has a ticket for this event |
| Service not registered | 404 | N/A | Blockchain env vars not configured |

**Test duplicate prevention:**

```bash
# Run the same MintTicket call a second time — it should fail:
curl -s -X POST \
  https://api.dev.liverty-music.app/liverty_music.rpc.ticket.v1.TicketService/MintTicket \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{"event_id": "e0000000-0000-0000-0000-000000000001"}' | jq .

# Expected: error with code "already_exists"
```

---

## 12.2 — UC2: Get Ticket Details (GetTicket RPC)

**Goal**: Retrieve full details of a specific ticket by its ID.

### Steps

```bash
curl -s -X POST \
  https://api.dev.liverty-music.app/liverty_music.rpc.ticket.v1.TicketService/GetTicket \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d "{
    \"ticket_id\": \"${TICKET_ID}\"
  }" | jq .
```

### Expected Response

```json
{
  "ticket": {
    "id": "01968abc-...",
    "eventId": "e0000000-0000-0000-0000-000000000001",
    "userId": "your-internal-user-uuid",
    "tokenId": "1",
    "txHash": "0xabc123...",
    "mintTime": "2026-02-23T12:00:00Z"
  }
}
```

### Verification Checklist

| Check | Expected |
|-------|----------|
| HTTP status | `200` |
| `ticket.id` matches requested ID | Yes |
| All fields populated | `eventId`, `userId`, `tokenId`, `txHash`, `mintTime` present |

### Error Cases

| Error | Connect Code | Cause |
|-------|--------------|-------|
| Invalid ticket ID | `invalid_argument` | Malformed UUID |
| Ticket not found | `not_found` | No ticket with that ID |
| Missing JWT | `unauthenticated` | No `Authorization` header |

---

## 12.3 — UC3: List My Tickets (ListTickets RPC)

**Goal**: List all tickets belonging to the authenticated user.

### Steps

```bash
curl -s -X POST \
  https://api.dev.liverty-music.app/liverty_music.rpc.ticket.v1.TicketService/ListTickets \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{}' | jq .
```

> **Note**: The request body is empty `{}`. The user is determined from the JWT `sub` claim.

### Expected Response

```json
{
  "tickets": [
    {
      "id": "01968abc-...",
      "eventId": "e0000000-0000-0000-0000-000000000001",
      "userId": "your-internal-user-uuid",
      "tokenId": "1",
      "txHash": "0xabc123...",
      "mintTime": "2026-02-23T12:00:00Z"
    }
  ]
}
```

### Verification Checklist

| Check | Expected |
|-------|----------|
| HTTP status | `200` |
| `tickets` array | Contains the ticket minted in UC1 |
| Only user's tickets | No tickets belonging to other users |

### Frontend Verification

1. Open `https://dev.liverty-music.app/tickets` in the browser (must be signed in).
2. Verify the tickets page renders the list of tickets.
3. Each ticket should show the event name and mint date.

---

## 12.4 — UC4: Get Merkle Path (GetMerklePath RPC)

**Goal**: Retrieve the Merkle path for the authenticated user's ticket in an event. This data is used client-side to generate a zero-knowledge proof.

### Prerequisites

- A ticket must have been minted for the user + event (UC1 completed).
- The Merkle tree must have been built for the event (happens automatically during minting).

### Steps

```bash
curl -s -X POST \
  https://api.dev.liverty-music.app/liverty_music.rpc.entry.v1.EntryService/GetMerklePath \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{
    "event_id": "e0000000-0000-0000-0000-000000000001"
  }' | jq .
```

### Expected Response

```json
{
  "merkleRoot": "base64-encoded-32-bytes",
  "pathElements": [
    "base64-encoded-32-bytes",
    "base64-encoded-32-bytes"
  ],
  "pathIndices": [0, 1],
  "leaf": "base64-encoded-32-bytes"
}
```

### Verification Checklist

| Check | Expected |
|-------|----------|
| HTTP status | `200` |
| `merkleRoot` | Non-empty, base64-encoded 32 bytes |
| `pathElements` | Array of base64-encoded 32-byte hashes (up to 20) |
| `pathIndices` | Array of 0s and 1s, same length as `pathElements` |
| `leaf` | Non-empty, base64-encoded 32 bytes |

### Error Cases

| Error | Connect Code | Cause |
|-------|--------------|-------|
| No ticket for event | `not_found` | User hasn't minted a ticket for this event |
| Missing JWT | `unauthenticated` | No `Authorization` header |
| Service not registered | 404 (HTTP) | `ZKP_VERIFICATION_KEY_PATH` env var not set |

---

## 12.5 — UC5: Generate Entry QR Code (Frontend)

**Goal**: Verify that the frontend can generate a QR code containing a zero-knowledge proof for event entry.

### Prerequisites

- User is signed in on the frontend.
- User has minted a ticket for the event (UC1).
- Circuit files are served at the configured `VITE_CIRCUIT_BASE_URL`.
- Service Worker has cached the circuit files (see Section 10.4).

### Steps

1. Open `https://dev.liverty-music.app/tickets` in Chrome.
2. Find the ticket for the test event in the list.
3. Click the **"Show QR"** (or equivalent) button on the ticket card.
4. A modal or inline section will appear showing:
   - A progress indicator while the ZKP proof is being generated.
   - The generated QR code image once proof generation is complete.

### What Happens Behind the Scenes

1. Frontend calls `GetMerklePath` RPC to fetch the Merkle path for the user's ticket.
2. snarkjs generates a Groth16 proof client-side using the circuit files (`.wasm` + `.zkey`).
3. A QR payload is created:
   ```json
   {
     "eventId": "e0000000-...",
     "proof": { /* snarkjs Groth16 proof object */ },
     "publicSignals": ["signal1", "signal2", ...],
     "exp": 1740000000000
   }
   ```
4. The payload is base64-encoded and rendered as a QR code (280x280 px).

### Verification Checklist

| Check | How to Verify | Expected |
|-------|---------------|----------|
| QR code appears | Visual | QR code image displayed |
| Proof generation time | Observe progress | Completes within ~10–30 seconds |
| QR expiry | Check DevTools console or source | `exp` is 5 minutes from now |
| Circuit files from cache | DevTools → Network | Size column shows `(ServiceWorker)` |

### Troubleshooting

| Problem | Possible Cause | Solution |
|---------|---------------|----------|
| "Proof generation failed" | Circuit files not available | Check SW cache (Section 10.4), verify `VITE_CIRCUIT_BASE_URL` |
| No QR appears | GetMerklePath failed | Check browser console for RPC errors |
| Very slow generation | First time, no cached circuits | Wait for download; subsequent attempts use cache |

---

## 12.6 — UC6: Verify Entry (VerifyEntry RPC)

**Goal**: Verify a zero-knowledge proof to grant event entry. This simulates what the event staff's QR scanner would do.

### Important Notes

- `VerifyEntry` does **NOT** require JWT authentication (the proof itself is the authentication).
- The nullifier in the proof prevents double entry — each proof can only be verified once per event.

### Steps (Using a QR Payload)

In practice, the scanning device would decode the QR code and call `VerifyEntry`. For manual testing, you can extract the proof from the frontend:

**1. Extract the proof from the QR payload (DevTools method):**

1. Open DevTools → **Console** tab.
2. After QR generation, the proof data is available in the component state.
3. Alternatively, intercept the base64 payload and decode it:
   ```javascript
   // In browser console, if you can access the QR data:
   atob("base64-encoded-qr-payload")
   ```

**2. Call VerifyEntry with the extracted proof:**

```bash
curl -s -X POST \
  https://api.dev.liverty-music.app/liverty_music.rpc.entry.v1.EntryService/VerifyEntry \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "e0000000-0000-0000-0000-000000000001",
    "proof_json": "{\"pi_a\":[...],\"pi_b\":[[...],[...]],\"pi_c\":[...],\"protocol\":\"groth16\"}",
    "public_signals_json": "[\"signal1\",\"signal2\"]"
  }' | jq .
```

> **Note**: No `Authorization` header needed. Replace the `proof_json` and `public_signals_json` with actual values from the QR payload.

### Expected Successful Response

```json
{
  "verified": true,
  "message": "Entry verified successfully"
}
```

### Verification Checklist

| Check | Expected |
|-------|----------|
| HTTP status | `200` |
| `verified` | `true` |
| `message` | Non-empty success message |
| Nullifier stored | `SELECT * FROM nullifiers WHERE event_id = 'e0...'` returns a row |

### Replay Prevention Test

**Run the same VerifyEntry call a second time with the same proof:**

```bash
# Same curl command as above — should fail:
# Expected: verified=false or error, because nullifier already used
```

| Check | Expected |
|-------|----------|
| `verified` | `false` |
| `message` | Indicates nullifier already used |
| Nullifier table | Still only 1 row (no duplicate) |

### Error Cases

| Error | Connect Code | Cause |
|-------|--------------|-------|
| Invalid proof format | `invalid_argument` | Malformed `proof_json` |
| Invalid public signals | `invalid_argument` | Malformed `public_signals_json` |
| Proof verification failed | `invalid_argument` | Invalid ZKP proof (tampered data) |
| Service not registered | 404 (HTTP) | `ZKP_VERIFICATION_KEY_PATH` not set |

---

## 12.7 — UC7: Build Merkle Tree (Backend Internal)

**Goal**: Verify that the Merkle tree is correctly built when tickets are minted.

> **Note**: This is an internal backend operation. There is no direct RPC to "build" the Merkle tree — it happens automatically during `MintTicket`. This section describes how to verify the tree was built correctly.

### Steps

**1. Check the Merkle tree table after minting a ticket:**

```sql
SELECT event_id, depth, node_index, encode(hash, 'hex') AS hash_hex
FROM merkle_tree
WHERE event_id = 'e0000000-0000-0000-0000-000000000001'
ORDER BY depth, node_index;
```

**2. Verify the tree structure:**

| depth | Meaning |
|-------|---------|
| 0 | Leaf nodes (one per ticket holder) |
| 1..N | Internal nodes (hashes of children) |
| max depth | Root node |

**3. Verify the Merkle root matches the events table:**

```sql
SELECT encode(merkle_root, 'hex') AS root_hex
FROM events
WHERE id = 'e0000000-0000-0000-0000-000000000001';
```

The root from `events.merkle_root` should match the highest-depth node in `merkle_tree`.

### Verification Checklist

| Check | Expected |
|-------|----------|
| Leaf count | Equal to number of tickets for the event |
| Hash sizes | All hashes are exactly 32 bytes (`octet_length(hash) = 32`) |
| Root consistency | `events.merkle_root` matches root node in `merkle_tree` |
| Tree integrity | Each parent is the Poseidon hash of its two children |

### Verify Hash Size Constraints

```sql
-- These should return 0 rows (no violations):
SELECT COUNT(*) FROM merkle_tree WHERE octet_length(hash) != 32;
SELECT COUNT(*) FROM nullifiers WHERE octet_length(nullifier_hash) != 32;
```

---

## 12.8 — End-to-End Flow

**Goal**: Verify the complete ticket lifecycle from minting to event entry.

### Flow Diagram

```
User signs in (Passkey)
    ↓
User mints ticket (UC1: MintTicket)
    ↓
User views tickets (UC3: ListTickets / Frontend /tickets page)
    ↓
User taps "Show QR" (UC5: Frontend proof generation)
    ↓                              ↓
    ├── Fetches Merkle path       (UC4: GetMerklePath)
    ├── Generates ZKP proof        (client-side snarkjs)
    └── Renders QR code            (base64-encoded payload)
    ↓
Staff scans QR code
    ↓
Staff device calls VerifyEntry (UC6: VerifyEntry)
    ↓
Entry granted (or denied if replayed)
```

### Step-by-Step End-to-End Verification

1. **Sign in** to `https://dev.liverty-music.app` with Passkey.
2. **Navigate** to the tickets page (`/tickets`).
3. **Mint a ticket** for the test event (via UI or curl — UC1).
4. **Verify** the ticket appears in the list (UC3).
5. **Tap "Show QR"** and wait for proof generation (UC5).
6. **Decode the QR** payload (using a QR scanner or DevTools).
7. **Call VerifyEntry** with the decoded proof (UC6).
8. **Confirm** entry is verified (`verified: true`).
9. **Re-scan the same QR** — confirm replay is blocked (`verified: false`).

### Completion Matrix

| Step | Use Case | Method | Status |
|------|----------|--------|--------|
| Sign in | Prerequisite | Passkey (Section 11) | |
| Mint ticket | UC1 | `MintTicket` RPC or UI | |
| View ticket details | UC2 | `GetTicket` RPC | |
| List tickets | UC3 | `ListTickets` RPC or `/tickets` page | |
| Get Merkle path | UC4 | `GetMerklePath` RPC | |
| Generate QR | UC5 | Frontend UI | |
| Verify entry | UC6 | `VerifyEntry` RPC | |
| Merkle tree built | UC7 | Database verification | |
| Replay blocked | Security | Second `VerifyEntry` call | |

---

## 10.4 — Service Worker Caches Circuit Files

**Goal**: Verify that the Service Worker registers on first load and caches ZK circuit artifacts (`.wasm`, `.zkey`).

### Steps

1. Open Chrome and navigate to the app URL.
2. Open DevTools (`F12`) → **Application** tab → **Service Workers**.
3. Confirm the Service Worker status shows **activated and is running**.
4. Navigate to **Application** → **Cache Storage**.
5. Locate the cache named `zk-circuits-v1`.
6. Verify it contains entries matching:
   - `ticketcheck.wasm`
   - `ticketcheck.zkey` (or versioned path like `/circuits/ticketcheck-v1/...`)

### Expected Result

- Service Worker is registered and active.
- `zk-circuits-v1` cache exists with `.wasm` and `.zkey` files cached using CacheFirst strategy.
- Subsequent loads serve circuit files from cache (verify via **Network** tab: `(ServiceWorker)` in the Size column).

### Troubleshooting

- If SW does not register: check console for errors, ensure HTTPS or `localhost`.
- If cache is empty: circuit files are cached on first fetch. Trigger proof generation once, then re-check.

---

## 10.5 — A2HS (Add to Home Screen) Install Prompt

**Goal**: Verify the PWA install prompt appears on supported platforms.

### Android Chrome

1. Open the app in Chrome on an Android device (9+).
2. Wait a few seconds after page load.
3. Look for the "Add to Home Screen" banner at the bottom or the install icon in the address bar.
4. Tap to install. Confirm the app appears on the home screen.
5. Launch from the home screen — verify it opens in standalone mode (no browser chrome).

### iOS Safari

1. Open the app in Safari on an iOS device (16.4+).
2. Tap the Share button (square with arrow).
3. Scroll down and tap "Add to Home Screen".
4. Confirm name shows "Liverty" (short_name from manifest).
5. Launch from the home screen — verify it opens in standalone mode.

### Expected Result

- Android: automatic install prompt or manual install via browser menu.
- iOS: manual install via Safari share sheet.
- Both: app launches in standalone mode (theme color `#1a1333`, no URL bar).

### Verification Checklist

| Item | Android | iOS |
|------|---------|-----|
| Install prompt / share sheet available | | |
| App name: "Liverty Music" / "Liverty" | | |
| App icon displayed correctly (512x512) | | |
| Standalone mode (no browser UI) | | |
| Start URL loads `/` | | |

---

## 10.6 — Offline Load After First Visit

**Goal**: Verify the app shell loads offline after the initial visit (precached by Workbox).

### Steps

1. Visit the app in Chrome and wait for the Service Worker to activate.
2. Open DevTools → **Application** → **Service Workers** — confirm SW is active.
3. Enable offline mode: DevTools → **Network** tab → check **Offline** checkbox.
4. Reload the page (`Ctrl+Shift+R` or `Cmd+Shift+R`).

### Expected Result

- The app shell renders (layout, navigation, basic UI) without network.
- API calls will fail (expected) but the page does not show Chrome's dinosaur / "No internet" page.
- Circuit files previously cached in `zk-circuits-v1` are available offline.

### Troubleshooting

- If offline load fails: check that SW precache manifest is populated (`self.__WB_MANIFEST` in sw.ts). Run a production build (`npm run build`) and test with `npm run preview`.
- Dev mode may not fully precache — test with a production build for reliable results.

---

## 11.1 — OIDC Flow Supports Passkey via Zitadel

**Goal**: Verify that the existing `oidc-client-ts` flow redirects to Zitadel's hosted login UI which supports Passkey authentication. No code change is expected — this confirms the integration works end-to-end.

### Steps

1. Open the app and click "Sign In".
2. Verify redirect to Zitadel hosted login UI (`dev-svijfm.us1.zitadel.cloud`).
3. On the Zitadel login page, confirm:
   - Username/password login is **disabled** (login policy: `userLogin: false`).
   - Passkey option is available (`passwordlessType: PASSWORDLESS_TYPE_ALLOWED`).
   - External IDP (Google, etc.) is **not shown** (`allowExternalIdp: false`).
4. Complete authentication (use existing Passkey or register one — see 11.2).
5. After redirect back, verify the user is authenticated (user info displayed, JWT token in localStorage).

### Expected Result

- Zitadel login page enforces Passkey-only authentication.
- After successful auth, `oidc-client-ts` receives tokens and stores user session.
- The org scope `urn:zitadel:iam:org:id:358672916038025519` ensures the org-level login policy applies.

---

## 11.2 — Passkey Registration

**Goal**: Test Passkey registration through Zitadel's hosted UI on desktop and mobile.

### Desktop (Chrome / Edge / Firefox)

1. Click "Sign Up" in the app (triggers `prompt: 'create'` flow).
2. On Zitadel registration page, enter the required user information.
3. When prompted to set up a Passkey, follow the browser's WebAuthn dialog:
   - Chrome: "Use your device's screen lock" or "Use a security key"
   - Select the appropriate method (Touch ID, Windows Hello, FIDO2 key, etc.)
4. Complete registration.

### Mobile (Android Chrome / iOS Safari)

1. Open the app (or PWA from home screen).
2. Tap "Sign Up".
3. On Zitadel registration page, enter user information.
4. When prompted for Passkey setup:
   - **Android**: Fingerprint / PIN / Pattern dialog.
   - **iOS**: Face ID / Touch ID dialog.
5. Complete registration.

### Verification Checklist

| Platform | Registration Prompt | Passkey Created | Auth Succeeds |
|----------|-------------------|----------------|---------------|
| Chrome (macOS) | | | |
| Chrome (Windows) | | | |
| Chrome (Android 9+) | | | |
| Safari (iOS 16.4+) | | | |

---

## 11.3 — Passkey Authentication

**Goal**: Test Passkey authentication (sign-in) on desktop and mobile.

### Steps

1. Open the app and click "Sign In".
2. On Zitadel login page, enter the username.
3. The browser prompts for Passkey verification:
   - Desktop: Touch ID / Windows Hello / FIDO2 key.
   - Mobile: Biometric (fingerprint / Face ID).
4. Verify successful redirect back to the app with authenticated session.

### Cross-Device Scenarios

| Scenario | Steps | Expected |
|----------|-------|----------|
| Same device | Sign in on the device where Passkey was registered | Biometric prompt → success |
| Cross-device (QR) | Sign in on desktop, scan QR with phone that has the Passkey | Phone biometric prompt → desktop authenticated |
| Multiple Passkeys | Register Passkeys on 2+ devices, sign in from either | Either device can authenticate |

### Verification Checklist

| Platform | Login Prompt | Biometric Works | Session Active |
|----------|-------------|-----------------|----------------|
| Chrome (macOS) | | | |
| Chrome (Windows) | | | |
| Chrome (Android 9+) | | | |
| Safari (iOS 16.4+) | | | |

---

## 11.4 — Supported Browsers and OS Versions for Passkey

### Minimum Requirements

| Platform | Browser | Min Version | Passkey Support |
|----------|---------|-------------|-----------------|
| macOS | Chrome | 109+ | Touch ID, iCloud Keychain |
| macOS | Safari | 16.0+ | Touch ID, iCloud Keychain |
| macOS | Firefox | 122+ | iCloud Keychain (macOS 14+) |
| macOS | Edge | 109+ | Touch ID |
| Windows | Chrome | 109+ | Windows Hello, Security Keys |
| Windows | Edge | 109+ | Windows Hello, Security Keys |
| Windows | Firefox | 122+ | Windows Hello |
| Android | Chrome | 109+ | Fingerprint, PIN, Pattern |
| Android | Samsung Internet | 23+ | Fingerprint, PIN |
| iOS | Safari | 16.0+ | Face ID, Touch ID |
| iOS | Chrome | 109+ | Face ID, Touch ID (via iOS Keychain) |

### OS Requirements

| OS | Min Version | Notes |
|----|-------------|-------|
| iOS | 16.4+ | Required for PWA standalone mode + Passkey. iOS 16.0 supports Passkey but 16.4 adds PWA push notification support. |
| Android | 9+ (API 28) | FIDO2 API via Google Play Services. Chrome 109+ required. |
| macOS | 13+ (Ventura) | iCloud Keychain passkey sync. Older versions support device-bound keys only. |
| Windows | 10 (1903+) | Windows Hello required for platform authenticator. |

### Known Limitations

- **iOS PWA**: Safari is the only engine for PWA on iOS. Third-party browsers (Chrome, Firefox) use Safari's WebKit and share the same Passkey store.
- **Firefox Desktop**: Passkey support was added in v122 (Jan 2024). Older versions require a security key (no platform authenticator).
- **Incognito/Private Mode**: Some browsers restrict Passkey access in private browsing mode.
- **Cross-Origin iframes**: Passkey prompts may be blocked in iframes without the `publickey-credentials-get` permissions policy.

### Recommendation

For the MVP, target:
- **Desktop**: Chrome 109+ (covers ~95% of desktop users)
- **Mobile**: iOS Safari 16.4+ and Android Chrome 109+
