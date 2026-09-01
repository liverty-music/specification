## Context

See [proposal.md](./proposal.md) for motivation. ⑥ is the wallet + entry layer on
top of the `Ticket` entity defined by ⑤ `ticket-purchase-and-issuance`. It honors
**Web-First / No Native App** (reception is a PWA using `getUserMedia`; no NFC
reader hardware). ⑤ is not yet specced, so the `Ticket` reference is a forward
contract.

**Design posture (app-first, corrected).** An earlier draft gated the QR reveal
behind a **gate-time passkey step-up** (rejected — see Decisions), then over-rotated
to an **OS-Wallet-first** entry model. Review corrected that: the entry credential
is an **in-app dynamic QR backed by a server-signed short-TTL token** (cross-platform,
fully app-controlled, not OS-shareable); **OS Wallet passes are a deferred
convenience tier**, not the MVP baseline.

**Anti-scalp posture (tiered platform model — not a gate re-auth):**

```
1. Account passkey login .................... phishing-resistant identity (always)
2. JPKI eKYC (マイナンバーカード) high-assurance lane  ...... kills BULK/industrial scalping
   (1 person = 1 verified account) — separate backlog change; JPKI certs only
   (never the 個人番号 → outside 番号法); the 基本4情報 + cert serial it returns are
   STILL 個情法 personal data → retain minimally. A lane, not mandatory.
3. Signed short-TTL credential + online atomic dedup ... forgery/screenshot + multi-sale
4. Official resale (⑦) ...................... sanctioned cannot-attend / demand valve
5. Per-event 顔認証 / ID check at entry (FUTURE) .. closes the 1:1 device-transfer hole
   for top-demand shows (roadmap `face-auth-entry`)
```

Honest MVP scope: MVP ships tiers 1 + 3 (+ the ⑤-captured 本人確認 rendered as the
covered-ticket identity). Bulk-scalp resistance arrives with `identity-ekyc-jpki`;
the device-transfer hole is closed for top shows by the future per-event 顔認証.
The spec's anti-scalp language is scoped to "convenience + double-entry prevention
+ covered-ticket identity", not a claim of full anti-scalp at MVP.

## Goals / Non-Goals

**Goals:**
- A **forge-resistant, screenshot-resistant** entry credential (signed short-TTL
  token rendered as an in-app dynamic QR), cross-platform, camera-scannable, no
  NFC hardware.
- **Signature + freshness verification, then online atomic duplicate-check** at
  admit as the integrity + concurrency controls.
- Render ⑤'s **covered-ticket face** on the presented credential.
- A browser-only reception scanner (Web-First), no native app.

**Non-Goals (design-level):**
- **Gate-time passkey step-up / any gate re-authentication** — NOT adopted.
- **OS Wallet passes (Apple/Google) as the MVP credential** — deferred to a later
  **convenience tier**, with explicit caveats: OS passes are **OS-shareable**
  (weaker anti-scalp); Apple Wallet has **no self-serve rotating barcode** (iOS
  would be static-screenshot-able); issuing them is a **個情法 §28 越境移転** to
  Apple/Google (US) needing consent/相当措置; and the covered-ticket face must
  render on the pass itself. The in-app QR avoids all of these.
- **NFC "tap to enter"** — impossible via PWA/Web NFC; needs certified gate reader
  hardware + platform programs; future venue-hardware initiative.
- **Offline reception validation** — MVP is online-first (fail-closed). The signed
  short-TTL token, however, makes a **future** light offline mode cheap
  (local signature+TTL verify + local used-list + reconcile) — NOT a COSE
  self-verifying credential, NOT in MVP.
- **Per-event 顔認証 / ID high-assurance mode** — closes the device-transfer hole;
  a separate future change (`face-auth-entry`); face templates are **特定生体情報**
  under the 令和8年 個情法改正 (notice + strengthened erasure/opt-out; NOT 要配慮) —
  handle in that change, not here.
- Order/charge/issuance and the covered-ticket face **content** (⑤); resale
  matching/refunds (⑦, which reuses the void→invalidate mechanism defined here).

## Decisions

- **Entry credential = in-app dynamic QR from a server-signed short-TTL token
  (app-first).** Signed over a claims set {ticket_id, event_id, holder_ref, epoch},
  ~30s TTL, secret server-side. This is the ONLY credential that is cross-platform,
  fully app-controlled, and not OS-shareable. Rejected: **OS-Wallet-first** (iOS has
  no self-serve rotating barcode → static-screenshot-able; OS passes are shareable
  → weaker anti-scalp; issuer programs + §28 越境移転 are lift for no anti-scalp
  gain) — demoted to a later convenience tier. Rejected: **bare ticket-id QR**
  (forgeable/leakable; makes dedup carry integrity it can't).
- **Signature + freshness is the integrity control; dedup is the concurrency
  control.** They are orthogonal: signature+TTL stops forgery and stale
  screenshots; the per-ticket atomic check-and-set resolves the 1:1 concurrent
  admit. The earlier draft conflated them ("dedup is the integrity control") —
  corrected.
- **Claims-set payload → SD-JWT-VC / mdoc migratable.** Sign over a structured
  claims object (not an opaque blob) and keep the signing primitive swappable, so
  a future verifiable-credential / mdoc path (EUDI direction; and a natural
  consumer for the face-auth tier) is not foreclosed. Adopting VC/mdoc now is
  premature (no verifier ecosystem for a closed JP event) — deferred, not walled off.
- **Online-first, fail-closed; signed token enables a principled future offline
  mode.** Reception needs a live server round-trip per scan (the secret is
  server-side; a browser PWA must not hold per-ticket secrets). If unreachable →
  fail closed. Because the credential is a self-verifiable signed token, a future
  offline mode can locally verify signature+TTL and reconcile dedup on reconnect
  (light allowlist model) — not built in MVP, but not architecturally precluded.
- **Covered-ticket face rendering is ⑥'s job; content is ⑤'s.** The presented
  credential (in-app view; and any future Wallet pass) MUST render ⑤'s 3-condition
  face, or 不正転売禁止法 §2③ "stated on its face" fails at the point of
  presentation. Assigned explicitly (was unassigned between ⑤ and ⑥).
- **Gate-time passkey step-up = NOT adopted.** WebAuthn proves phishing-resistance
  / origin binding, **not anti-collusion**; a holder can authenticate then hand
  over the device (the "escort" hand-off), so a gate step-up only dents an already
  non-scaling 1:1 residual at a disproportionate UX/auth-server cost. The
  strong-control budget goes to per-event 顔認証 (tier 5), which actually closes
  the hand-off. The identity-management step-up primitive is therefore **withdrawn**.
- **Same-time group entry is in-app (coherent).** The lead's authenticated session
  presents the group's credentials; M-of-N admit = scan M. Because they are in-app
  (not OS-shareable passes), there is no off-platform distribution vector and the
  group semantics are enforceable.
- **Reception = PWA + `getUserMedia`**, no NFC reader.
- **Void → invalidate at online validation**, the shared mechanism ⑦ (and admin)
  call; a voided token stops validating at admit.
- **Entity conventions (proto stage).** Entry state + token fields follow CLAUDE.md
  (wrapper-message type-safe IDs, enum entry state, protovalidate).

## Risks / Trade-offs

- **App-first costs lock-screen convenience at the gate** (fan opens the PWA).
  *→* Accepted for MVP: it removes two platform-program dependencies, kills the
  OS-shareable-pass residual and the §28 transfer, and makes anti-scalp coherent.
  OS Wallet convenience returns later as an explicit, caveated tier.
- **Online dependency at the gate** (secret is server-side → per-scan round-trip;
  fail-closed). *→* Mitigated operationally (reception on a network isolated from
  attendee traffic, reliable uplink); the signed token keeps a future offline mode
  cheap if needed.
- **Anti-scalp depends on unbuilt layers** (JPKI eKYC, official resale, per-event
  顔認証). *→* Scoped honestly (see Context); MVP does not claim full anti-scalp;
  the ⑤-captured 本人確認 is the MVP identity floor. Sequenced on the roadmap.
- **Camera scan is slower than NFC** at big gates. *→* Provision parallel reception
  stations; NFC tap is a future hardware tier.
- **Authored ahead of ⑤ (not specced).** *→* Reference `Ticket` + 本人確認 (and its
  covered-ticket face content), don't redefine; reconcile when ⑤ specs land.

## Migration Plan

New capability on ⑤'s Ticket. Sequence: proto (entry state, signed-token
issue/validate RPCs) → BSR → backend (token signer + secret store, validate =
signature+TTL then atomic check-and-set dedup, void→invalidate hook) → frontend
(in-app wallet rendering the covered-ticket face + live dynamic-QR) → reception PWA
(getUserMedia scanner, fail-closed). Gated on ⑤ for the Ticket entity. No
identity-management step-up primitive is needed (withdrawn). OS Wallet issuance is
a separate later convenience change.

## Open Questions

- **TTL length + clock-skew window** for the signed token — tunable; does not
  change the spec surface.
- **eKYC-lite in MVP?** whether to make the ⑤-captured 本人確認 a load-bearing
  1-account binding at MVP vs deferring all identity to `identity-ekyc-jpki` — a
  scope call for the ④/⑤ owners; does not change ⑥'s credential design.
