## Why

Phase 3 step ⑥ — the last ticketing MVP capability. ⑤ issues **account-bound
Tickets**, but a fan cannot yet *use* one: there is no wallet to show it, no
forge-resistant entry credential, and no way for staff to admit attendees. This
change adds the **wallet + entry** layer: view your ticket (incl. its
covered-ticket face), enter with an **in-app dynamic QR backed by a server-signed
short-TTL token**, companion **same-time group entry**, and a **reception PWA**
that scans via the web camera and validates each scan with **signature + freshness
then an online atomic duplicate-check**.

Anti-scalp is **not** enforced by a gate-time re-authentication (explored and
rejected — see design.md); it rests on the platform's tiered model (account
passkey + JPKI eKYC lane + signed-credential/dedup + official resale + future
per-event 顔認証). **OS Wallet passes are a deferred convenience tier**, not the
MVP baseline (see design Non-Goals). Roadmap:
[`ticketing-platform-roadmap.md`](../../../docs/ticketing-platform-roadmap.md).

## What Changes

- **Ticket wallet UI** — a fan views their issued (⑤) ticket: event details, entry
  status, and the **covered-ticket (特定興行入場券) face** (⑤ owns the content;
  ⑥ renders it on the presented credential, so 不正転売禁止法 §2③ "stated on its
  face" holds where the holder presents it).
- **Entry credential = in-app dynamic QR from a server-signed short-TTL token** —
  signed over {ticket_id, event_id, holder_ref, epoch}, ~30s TTL, secret
  server-side; rendered live in the authenticated wallet; cross-platform; **not an
  OS-shareable pass**. A screenshot is stale after the TTL; a leaked ticket-id
  can't be forged without the signing secret.
- **No gate-time re-auth** to display the credential (rejected — it can't close
  the device hand-off it targeted and is costly; design.md).
- **Validation = signature + freshness, THEN online atomic duplicate-check** — the
  reception sends the token; the server verifies it, then does an atomic
  check-and-set (allow/deny before admit); two concurrent scans → exactly one
  admit; server-unreachable **fails closed**.
- **Same-time group entry** — the lead's authenticated session presents the
  group's credentials; subset M-of-N admits only those scanned. **No first-party
  distribution URL**; in-app (not OS-shareable) → no off-platform vector.
- **Reception (check-in) PWA** — staff scan with the **web camera (`getUserMedia`)**,
  no native app, **no NFC reader hardware**.
- **Entry status + no double-entry**; **void → invalidate at server validation**.

Scope guardrails (MVP): electronic tickets only; **online-first, fail-closed**
(reception network isolated from attendee traffic — transport is a deployment
choice). **OS Wallet passes, NFC tap, offline scanning, and per-event 顔認証/ID are
out of scope** (future — see design Non-Goals + roadmap). MVP anti-scalp =
account passkey + signed-credential/dedup + the ⑤-captured 本人確認 identity;
bulk-scalp resistance arrives with `identity-ekyc-jpki`.

## Capabilities

### New Capabilities
- `ticket-wallet-and-checkin`: the fan **wallet** (renders the ticket + its
  covered-ticket face), the **in-app dynamic QR / signed short-TTL token** entry
  credential, **signature+freshness then online atomic duplicate-check** at admit,
  **same-time companion group entry** (no first-party distribution), the
  **reception PWA** (web-camera scan, no NFC), and entry status with double-entry
  prevention.

### Modified Capabilities
<!-- None as a delta. This capability operates on the `Ticket` entity defined by
     ⑤ ticket-purchase-and-issuance (account-bound, 本人確認-bound, covered-ticket
     face CONTENT); ⑥ adds entry state + credential/check-in behavior and RENDERS
     ⑤'s covered-ticket face. ⑤ is not yet specced (forward contract). NOTE: an
     earlier draft added a WebAuthn step-up primitive to identity-management — that
     is WITHDRAWN (no gate-time step-up; see design). -->

## Impact

- **Depends on:** ⑤ `ticket-purchase-and-issuance` (the issued **Ticket** entity +
  its 本人確認 + covered-ticket face **content**). Hard dependency on ⑤.
- **Enables:** ⑦ `official-resale` void semantics (a resold seat's credential is
  invalidated at validation — the void→invalidate mechanism lives here).
- **New:** signed short-TTL token signer + server-side secret store, in-app dynamic
  QR rendering (+ covered-ticket face), validate (signature+TTL) + **atomic
  check-and-set** dedup, `entered` state on the Ticket, the reception PWA surface.
- **Product constraints honored:** **Web-First / No Native App** (PWA
  `getUserMedia`, no NFC hardware); **no first-party distribution URL**.
- **Anti-scalp (tiered, NOT a gate re-auth):** signed short-TTL credential +
  online atomic dedup defeat forgery/screenshot/multi-sale; bulk scalping is
  blocked upstream by JPKI eKYC (backlog); the 1:1 device-transfer residual is
  closed for top-demand shows by a **future per-event 顔認証/ID mode**
  (`face-auth-entry`), not by this layer.
- **Deferred (future):** OS Wallet convenience passes (caveats: OS-shareable, iOS
  static, 個情法 §28 越境移転 to Apple/Google, must render the covered-ticket face);
  NFC tap; offline scanning; per-event 顔認証.
- **Withdrawn:** the previously-proposed identity-management **step-up primitive**.
