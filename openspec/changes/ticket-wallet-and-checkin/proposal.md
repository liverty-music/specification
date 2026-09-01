## Why

Phase 3 step ⑥ — the last ticketing MVP capability. ⑤ issues **account-bound
Tickets**, but a fan cannot yet *use* one: there is no wallet to show it, no
tamper-resistant entry credential, and no way for staff to admit attendees. This
change adds the **wallet + entry** layer: view your tickets, enter the gate with
a **server-signed rotating QR** (+ Passkey re-auth), companion **same-time group
entry**, and a **reception PWA** that scans via the web camera — honoring the
product's **Web-First, No Native App** constraint.

Roadmap:
[`ticketing-platform-roadmap.md`](../../../docs/ticketing-platform-roadmap.md).

## What Changes

- **Ticket wallet UI** — a fan views their issued (⑤) tickets and event details.
- **Server-signed rotating QR** — the entry credential is a short-lived,
  server-signed token that **rotates** (a screenshot is useless once it rotates),
  bound to the ticket + holder. Validation is server-side.
- **Passkey re-auth to reveal/open the QR** — showing the entry QR requires a
  fresh **Passkey** check (the identity floor), so a shared screen cannot enter.
- **Same-time group entry (companion)** — a multi-ticket win is used by the
  **lead holding all N tickets on their own device**; companions enter **together**
  with the lead. **No distribution URL** (deliberately rejected — a scalping
  loophole; roadmap Guiding Decisions).
- **Reception (check-in) PWA** — staff scan the rotating QR with the **web camera
  (`getUserMedia`)**; the server validates (signature + not-yet-used + holder
  match) and marks entry. No native scanner app.
- **Real-time entry status** — a ticket flips to **entered** on a successful
  scan; a re-scan of the same ticket is rejected (no double-entry).

Scope guardrails (MVP): electronic tickets only; entry is the rotating-QR +
Passkey floor (the optional face-match identity tier `face-auth-entry` is a
separate later change); no offline-scanner mode (PWA needs connectivity to
validate) — accepted for MVP, revisit for large venues.

## Capabilities

### New Capabilities
- `ticket-wallet-and-checkin`: the fan **wallet** (view issued tickets), the
  **server-signed rotating QR + Passkey re-auth** entry credential, **same-time
  companion group entry** (lead-device, no distribution), the **reception PWA**
  (web-camera scan → server validation → entry), and **real-time entry status**
  with double-entry prevention.

### Modified Capabilities
<!-- None as a delta. This capability operates on the `Ticket` entity defined by
     ⑤ ticket-purchase-and-issuance (account-bound, 本人確認-bound); it adds entry
     state + the QR/check-in behavior. ⑤ is not yet specced, so the Ticket
     reference is a forward contract (see design.md). -->

## Impact

- **Depends on:** ⑤ `ticket-purchase-and-issuance` (the issued **Ticket**
  entity + its 本人確認 binding) and existing **Passkey / identity-management**
  (the re-auth floor). Hard dependency on ⑤.
- **Enables:** ⑦ `official-resale` void semantics (a resold seat's original QR is
  invalidated — the rotating-QR/void mechanism lives here).
- **New:** rotating-QR signing/validation service, `entry`/`entered` state on the
  Ticket, the reception PWA app surface, real-time entry status.
- **Product constraints honored:** **Web-First / No Native App** (PWA
  `getUserMedia` scanner); **no companion distribution URL** (anti-scalp).
- **Anti-scalp:** rotating QR + Passkey + covered-ticket status make a sold
  screenshot / off-platform purchase useless at the gate.
