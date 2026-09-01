## 0. Dependency gate

- [ ] 0.1 Confirm ⑤ `ticket-purchase-and-issuance` is specced + shipped (the account-bound `Ticket` entity + 本人確認 binding this operates on)
- [ ] 0.2 **Add a WebAuthn step-up / fresh-assertion primitive to identity-management** (prerequisite delta) — the shipped surface only has Passkey login policy + 90-day refresh expiry; the QR-reveal gate needs a per-action step-up that does not exist yet

## 1. Proto / entity (specification → BSR)

- [ ] 1.1 Add entry state to `Ticket` (not_entered / entered, entered_at) + a void marker (references ⑤ Ticket)
- [ ] 1.2 Rotating-QR: signed-token issue RPC (server-side) + validate/admit RPC (reception)
- [ ] 1.3 Wallet RPCs: list my tickets + status; reception RPC: scan → validate → admit
- [ ] 1.4 protovalidate; buf lint/breaking; merge PR → Release → BSR gen

## 2. Backend — rotating QR + validation

- [ ] 2.1 Server-signed short-lived rotating token bound to ticket + holder; rotation interval + validation skew window
- [ ] 2.2 Server-side validate: signature + freshness + ticket binding + not-already-used
- [ ] 2.3 Void → invalidate QR hook (shared mechanism reused by ⑦ resale + admin)

## 3. Backend — entry state

- [ ] 3.1 Atomic entry transition (not_entered → entered) with double-entry rejection
- [ ] 3.2 Real-time entry status (wallet + reception views)
- [ ] 3.3 Same-time group entry: admit N companion tickets held on the lead's device together

## 4. Frontend — wallet (Aurelia PWA)

- [ ] 4.1 Wallet: list issued tickets + event details + entry status
- [ ] 4.2 Passkey re-auth gate before revealing the rotating QR
- [ ] 4.3 Entry QR view (auto-rotating); companion group shown on the lead's device (no distribution URL)

## 5. Reception check-in PWA

- [ ] 5.1 Web-camera scanner via getUserMedia (PWA, no native app)
- [ ] 5.2 Scan → server validate → admit/reject UX; already-used + void rejection surfaced
- [ ] 5.3 Same-time group admit flow for a multi-ticket lead

## 6. Anti-scalp / product constraints

- [ ] 6.1 No companion distribution URL / transferable per-companion code (verify none exists)
- [ ] 6.2 Screenshot-proof: confirm a captured code fails after rotation; shared-screen fails Passkey gate

## 7. Release & verification

- [ ] 7.1 Cross-repo release order: spec → BSR → backend → frontend + reception PWA
- [ ] 7.2 End-to-end verify: issue (⑤) → wallet → Passkey-gated QR → reception scan admit → entered; re-scan rejected; stale-code rejected; void → cannot enter; same-time group admit
- [ ] 7.3 Sync delta specs to main specs and archive the change
