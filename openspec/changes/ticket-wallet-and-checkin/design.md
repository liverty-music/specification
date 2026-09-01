## Context

See [proposal.md](./proposal.md) for motivation. ⑥ is the wallet + entry layer on
top of the `Ticket` entity defined by ⑤ `ticket-purchase-and-issuance`. It honors
two product constraints: **Web-First / No Native App** (reception is a PWA using
`getUserMedia`) and the roadmap's rejection of any **companion distribution URL**.
⑤ is not yet specced, so the `Ticket` reference is a forward contract; the
Passkey re-auth reuses the existing identity-management floor.

## Goals / Non-Goals

**Goals:**
- A tamper-resistant, screenshot-proof entry credential (server-signed rotating
  QR + Passkey re-auth) validated server-side.
- Companion use without distribution (same-time group entry, lead-device).
- A browser-only reception scanner (no native app) with double-entry prevention.

**Non-Goals (design-level):**
- The optional **face-match identity tier** (`face-auth-entry`) — a separate later
  change on top of this floor.
- **Offline** reception validation — MVP requires connectivity (server validates
  each scan); revisit for large/poor-connectivity venues.
- Order/charge/issuance (⑤); resale matching/refunds (⑦, which only reuses the
  void→invalidate-QR mechanism defined here).

## Decisions

- **Server-signed rotating QR, server-side validation.** The code is a
  short-lived signed token bound to ticket + holder, rotating on an interval; the
  gate validates against the server, so a screenshot dies at the next rotation and
  the client cannot forge a code. Rejected: static QR / client-only validation
  (trivially screenshot-shared).
- **Passkey re-auth to reveal the QR.** Reuses the identity floor so a shared
  screen / handed-off device cannot enter — the anti-scalp identity anchor.
- **Same-time group entry, no distribution URL.** The lead holds all N on-device
  and the group enters together; there is deliberately **no** shareable per-
  companion code (a scalper could otherwise win, share the URL, and collect off-
  platform). The sanctioned hand-off for cannot-attend is ⑦ official resale.
  Residual risk (small-scale physical escort) accepted (roadmap).
- **Reception = PWA + `getUserMedia`** (Web-First/No-Native-App). Each scan is
  server-validated (signature + freshness + ticket binding + not-already-used).
- **Entry state on the Ticket + double-entry prevention.** A successful scan flips
  the ticket to `entered` atomically; a re-scan of an entered ticket is rejected.
- **Void → invalidate QR** is defined here as the shared mechanism ⑦ resale (and
  admin actions) call to kill a seat's credential at match/void time. Centralizing
  it here avoids ⑦ re-implementing entry invalidation.

- **Passkey step-up is a NEW identity-management prerequisite.** The shipped
  identity surface has only a Passkey *login* policy + the 90-day refresh expiry —
  no per-action step-up. ⑥ requires a **WebAuthn fresh-assertion primitive** to be
  added to identity-management first (tasks §0.2); it MUST NOT be downgraded to an
  ordinary session check.
- **Entity conventions (proto stage).** New entities/fields (entry state, QR
  validation) MUST follow CLAUDE.md: **wrapper-message type-safe IDs** and
  **enums** for entry state (not bare strings), with protovalidate constraints.

## Risks / Trade-offs

- **Authored ahead of ⑤ (not specced).** The `Ticket` entity + its 本人確認
  binding are a forward contract. *→* Reference, don't redefine; add only entry
  state + QR behavior. Reconcile when ⑤ specs land.
- **Connectivity required at the gate.** *→* MVP accepts online-only validation;
  note it explicitly; an offline signed-token grace mode is a future option.
- **Rotation interval vs scan latency.** Too short → valid codes rejected on slow
  cameras; too long → wider screenshot window. *→* Tunable; pick an interval with
  a small validation skew window. Implementation detail, not a spec change.
- **Same-time entry is operationally strict** (whole group must arrive together).
  *→* Accepted per roadmap; the cannot-attend path is ⑦ resale, not hand-off.
- **Passkey friction at a busy gate.** *→* The re-auth is to reveal the QR (can be
  done just before reaching the scanner); acceptable for the anti-scalp benefit.

## Migration Plan

New capability on ⑤'s Ticket. Sequence: proto (entry state, QR/validation RPCs,
reception service) → BSR → backend (rotating-QR signer + validator, entry
transition with double-entry guard, void→invalidate hook) → frontend (wallet +
Passkey-gated QR reveal) → reception PWA (getUserMedia scanner). Gated on ⑤ for
the Ticket entity; reuses existing Passkey/identity.

## Open Questions

- **QR rotation interval + validation skew window** — a tunable security/UX
  parameter; does not change the spec surface.
- **Future offline reception mode** (signed-token grace when the gate is offline)
  — deferred; would be an additive change, not part of MVP.
