## 0. Dependency gate

- [ ] 0.1 Confirm ⑤ `ticket-purchase-and-issuance` is specced + shipped (the account-bound `Ticket` entity + 本人確認 + covered-ticket face **content** this renders)
- [ ] 0.2 (No identity step-up prerequisite — gate-time passkey re-auth is NOT adopted; see design)
- [ ] 0.3 (No OS Wallet issuer setup in MVP — OS Wallet passes are a deferred convenience tier)

## 1. Proto / entity (specification → BSR)

- [ ] 1.1 Add entry state to `Ticket` (not_entered / entered, entered_at) + a void marker (references ⑤ Ticket)
- [ ] 1.2 Signed short-TTL entry token: issue RPC (claims set {ticket_id, event_id, holder_ref, epoch}) + validate/admit RPC (reception)
- [ ] 1.3 Wallet RPCs: list my tickets + status + covered-ticket face; reception RPC: scan → verify signature+TTL → atomic dedup → admit
- [ ] 1.4 protovalidate (type-safe IDs, enum entry state); buf lint/breaking; merge PR → Release → BSR gen

## 2. Backend — credential + validation

- [ ] 2.1 Signed short-TTL token signer + **server-side secret store** (claims set, ~30s TTL, rotating epoch, swappable signing primitive for a future SD-JWT-VC/mdoc path)
- [ ] 2.2 Validate at admit: **verify signature + freshness FIRST** (reject forged/stale), then hand to dedup; reject voided tickets
- [ ] 2.3 Void → invalidate hook (shared mechanism reused by ⑦ resale + admin), enforced at validation

## 3. Backend — admission dedup + entry state

- [ ] 3.1 **Atomic check-and-set** on entry state (conditional update / unique constraint / **per-ticket** row lock, not table-level); exactly-one-admit for concurrent same-ticket scans across gates; decision returned before admit
- [ ] 3.2 Entry status surfaced (wallet + reception views)
- [ ] 3.3 Same-time group entry: present the group in the lead's session; subset M-of-N admits only those scanned; unadmitted stay valid

## 4. Frontend — wallet (Aurelia PWA)

- [ ] 4.1 Wallet: list issued tickets + event details + entry status + **render the covered-ticket face** (⑤'s 3 conditions) on the presented credential
- [ ] 4.2 In-app **dynamic QR** rendered live in the authenticated session (auto-refresh per epoch; no gate-time re-auth to display; not an OS-shareable pass)
- [ ] 4.3 Companion group presented together (no first-party distribution URL)

## 5. Reception check-in PWA

- [ ] 5.1 Web-camera scanner via getUserMedia (PWA, no native app, no NFC reader)
- [ ] 5.2 Scan → server verify (signature+TTL) → **atomic dedup** → admit/reject UX; already-used, stale, forged, and void rejections surfaced; **fail closed** when server unreachable
- [ ] 5.3 Same-time group admit flow (subset M-of-N)
- [ ] 5.4 Deployment note: reception devices on a network isolated from attendee traffic with a reliable uplink (ops runbook, not code)

## 6. Anti-scalp / product constraints

- [ ] 6.1 No first-party distribution URL / transferable per-companion code (verify none exists)
- [ ] 6.2 Forgery/screenshot resistance: confirm a stale/forged token fails signature+TTL verification (not merely dedup), and that dedup admits at most once per ticket
- [ ] 6.3 Scope check: MVP anti-scalp = account passkey + signed-credential/dedup + ⑤-captured 本人確認 identity; do NOT claim bulk-scalp resistance (that is `identity-ekyc-jpki`)

## 7. Release & verification

- [ ] 7.1 Cross-repo release order: spec → BSR → backend → frontend + reception PWA
- [ ] 7.2 End-to-end verify: issue (⑤) → wallet renders covered-ticket face + dynamic QR → reception scan admit → entered; re-scan rejected; **stale/forged token rejected before dedup**; **concurrent same-ticket scans → exactly one admit**; server-unreachable fails closed; void → cannot enter; subset group admit
- [ ] 7.3 Sync delta specs to main specs and archive the change

## 8. Future (out of MVP scope — do not implement now)

- [ ] 8.1 **OS Wallet convenience passes** (Apple/Google) — caveats: OS-shareable (weaker anti-scalp), iOS static (no self-serve rotating barcode), 個情法 §28 越境移転 consent to Apple/Google (US), must render the covered-ticket face on the pass
- [ ] 8.2 Per-event **顔認証 / ID high-assurance mode** at entry (closes the 1:1 device-transfer hole; roadmap `face-auth-entry`; face templates = 特定生体情報 under 令和8年改正)
- [ ] 8.3 **NFC tap-to-enter** (Apple VAS / Google Smart Tap) — certified gate reader hardware + platform programs; not PWA
- [ ] 8.4 **Offline scanning** — reuse the signed short-TTL token: local signature+TTL verify + local used-list + reconcile (light allowlist model), if a venue outgrows online-first
