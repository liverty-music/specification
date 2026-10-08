## Context

See [proposal.md](./proposal.md) for motivation. ⑥ is the wallet + entry layer on
top of the `Ticket` entity of ⑤ `ticket-purchase-and-issuance`, which has shipped
and is in the main specs; this change adds an admitted time to it and builds on its
Issued / Voided lifecycle. It honors **Web-First / No Native App**: both the fan's
tickets screen and the reception screen are web pages using standard browser APIs,
with no NFC reader hardware.

**Pilot context (2026-10-07/08).** The first real use is a pilot with an independent
artist (liverty-music/specification#1074): a small, often basement venue with poor
mobile signal, tickets sold first come, first served, and **reception run by venue
staff from outside the Organizer**. The decisions below were settled for that
setting and are meant to hold after it. Venue-side checks that can only happen at
the venue are tracked in liverty-music/specification#1076, not in this change.

**Anti-scalp posture (tiered platform model — not a gate re-auth):**

```
1. Account passkey login .................... phishing-resistant identity (always)
2. JPKI eKYC (マイナンバーカード) high-assurance lane  ...... kills BULK/industrial scalping
   (1 person = 1 verified account) — separate backlog change; JPKI certs only
   (never the 個人番号 → outside 番号法); the 基本4情報 + cert serial it returns are
   STILL 個情法 personal data → retain minimally. A lane, not mandatory.
3. Device-bound, short-lived AdmissionCode + online atomic admit ... forgery /
   screenshot / double entry
4. Official resale (⑦) ...................... sanctioned cannot-attend / demand valve
5. Per-event 顔認証 / ID check at entry (FUTURE) .. closes the 1:1 device-transfer hole
   for top-demand shows (roadmap `face-auth-entry`)
```

Honest MVP scope: MVP ships tiers 1 + 3 (+ the ⑤-captured 本人確認 rendered on the
ticket face). The spec's anti-scalp language is scoped to "convenience + double-entry
prevention + covered-ticket identity", not a claim of full anti-scalp at MVP.

## Goals / Non-Goals

**Goals:**
- A **forge-resistant, screenshot-resistant** entry QR code that the fan's phone can
  show **without a connection** at the venue.
- **One admission per ticket**, even for concurrent scans at several entrances, with
  a permanent record of every admission.
- Render ⑤'s **covered-ticket face** on the tickets screen.
- Let **external venue staff** admit fans for **one event** from their own phones,
  without an account, without any other Organizer right, and without seeing fans'
  personal data.

**Non-Goals (design-level):**
- **Gate-time passkey step-up / any gate re-authentication** — NOT adopted.
- **OS Wallet passes (Apple/Google)** — deferred convenience tier: OS-shareable
  (weaker anti-scalp), no self-serve rotating barcode on iOS, a 個情法 §28 越境移転 to
  Apple/Google, and the covered-ticket face would have to render on the pass.
- **NFC "tap to enter"** — impossible from a web page; needs certified reader
  hardware.
- **Offline reception** — the reception device needs a connection for each scan
  (fail closed); only the fan side works offline.
- **Per-event 顔認証 / ID mode** — separate future change (`face-auth-entry`); face
  templates are 特定生体情報 under the 令和8年 個情法改正.
- **A Zitadel `reception` role** for staff accounts — stays in
  `organizer-rbac-subowners` for standing reception teams and can coexist with
  reception links.
- **A reception test mode** — rehearsals use a separate test event.
- **Organizer-configurable reception windows** and a **PIN** on links.
- **Installing the reception screen to the home screen** — see the decision below.
- Order/charge/issuance and the covered-ticket face **content** (⑤); resale
  matching and refunds (⑦), which rely on Voided tickets being refused here.

## Decisions

### Entry code

- **AdmissionCode signed on the fan's device with a device-bound key pair
  (2026-10-08).** On the first visit with a connection, the tickets screen creates an
  ECDSA P-256 key pair with WebCrypto (`extractable: false`), keeps the `CryptoKey`
  in IndexedDB and registers only the public key (`WalletPublicKey`). At the venue
  the device signs {user, event, tickets, signed time} every 15 seconds with no
  connection; the server verifies with the registered public key, then admits.
  Alternatives considered:
  - **Server-signed token fetched every ~20 s** (the earlier design) — needs a
    connection on the fan's phone at the door, which small basement venues often
    lack; it is also not how the industry does it.
  - **Shared-secret TOTP (Ticketmaster SafeTix, RFC 6238)** — works offline, but the
    secret travels from the server to the device and was extracted from SafeTix's
    traffic and used to generate codes off-device; a leak of the server's secrets
    would also let anyone forge codes.
  - **Device-bound key pair (chosen)** — the private key never leaves the device and
    the server keeps only public keys. This is the pattern of OAuth DPoP (RFC 9449)
    with WebCrypto non-extractable keys, and the holder-binding idea of SD-JWT-VC and
    mdoc, so a later verifiable-credential path stays open.
- **What device binding does not stop.** A non-extractable key cannot be copied by
  page script, but script running on the page (an XSS) can still ask the device to
  sign. The outcome is the same as handing over the unlocked phone, which the
  tiered model already accepts; strict CSP stays essential. Online atomic admission
  still lets each ticket in once.
- **One active key per User.** Registering a new device's key replaces the old one, so
  tickets are shown from one device at a time and codes from a replaced phone are
  refused. Clearing site data or changing phones means registering again, which the
  tickets screen does automatically when online.
- **Freshness: 15 s rotation, accepted from 30 s before to 15 s after the server
  time.** The window allows a code shown just before rotation plus a slightly fast
  or slow phone clock (the TOTP practice of accepting adjacent steps).
- **QR payload: compact binary in Base45, QR alphanumeric mode.** The payload (ids as
  16-byte values, a 4-byte time, a 64-byte signature) is encoded with Base45
  (RFC 9285), which maps onto the QR alphanumeric character set and gives smaller
  codes than Base64 in byte mode; decoders return text, so a text encoding is needed
  anyway. At most 10 tickets per code keeps the code small enough to scan from a
  phone screen. Error correction level M.
- **Rendering: `@paulmillr/qr` as SVG.** Compared with `uqr` and `lean-qr`
  (2026-10-08): all are small, dependency-free and output SVG; `@paulmillr/qr` also
  ships a decoder, so one library both makes and reads the code. White quiet zone and
  high contrast.
- **Screen stays awake while the code is shown.** Screen Wake Lock API, requested in
  try/catch, re-acquired on `visibilitychange` (the browser releases it when the page
  is hidden) and released when the code is closed. Browsers cannot raise brightness;
  the screen suggests it.

### Reception

- **Reception links instead of operator sign-in (2026-10-07).** Reception staff are
  external, so the reception caller is a `ReceptionLink`: issued by the Organizer per
  event and per device, scoped to admitting that one event, no account. Considered:
  a Zitadel `reception` role (accounts and passkeys for one-night staff are
  impractical) and lending the Organizer's signed-in device (hands staff every console
  right). A leaked link can only admit holders of fresh, genuine codes to that one
  event during its window.
- **The reception device proves itself with its own key pair.** The first device that
  opens a link creates an ECDSA P-256 key pair the same way as the fan side and binds
  its public key to the link; every later call is signed over the link token, the
  call's content and a signed time, and the server checks it with the bound key.
  Nothing secret travels after the link URL itself, and a forwarded link cannot be
  used from another device. Chosen over a random device secret sent with each call,
  which page script could read and which travels on every call.
- **Fixed reception window, not organizer-configurable.** From 3 hours before the open
  time, or before the start time when the event has no open time, to 04:00 JST on the
  day after the event date, from the event's current date and times. Events have no end time, and a configurable window is one more field
  to get wrong on the day. Links can be issued any time before; outside the window the
  screen says when reception starts. A link cannot be issued for an event without a
  start time.
- **The start time is required when a sale is set up; the open time stays optional.**
  Publishing an event keeps both optional (dates are often announced before times),
  but a ticketed event must have a start time: the ticket face shows it and the
  reception window falls back to it when doors are not announced. This change adds the rule to the lottery (`ConfigureLotteryPhase` and the
  lottery phase editor), because no other active change owns it; the planned
  first-come sale must carry the same rule (#1074). Phases configured before this
  change are not revisited: the pilot sells first come, first served, and a reception
  link still refuses an event without a start time.
- **Decoding: `BarcodeDetector` when it supports QR, otherwise `@paulmillr/qr`, in a
  Web Worker.** Chrome's guidance treats the Shape Detection API as an optimisation
  to combine with one's own decoder. It is available on Chrome for Android but
  disabled by default on Safari up to the current iOS 27 and absent on Firefox, so
  staff iPhones use the library. Frames are taken from `getUserMedia` with
  `facingMode: { ideal: 'environment' }` and decoded off the main thread.
- **The reception screen runs in a browser tab, not installed.** iOS does not keep the
  camera permission for home-screen web apps and asks again repeatedly (WebKit
  185448), and iOS 26 has camera orientation problems in home-screen apps. In a Safari
  tab the permission behaves normally. The camera is requested only when staff tap to
  start scanning.
- **Admission and its record are one step.** `Ticket.Admit` sets the admitted time and
  stores the Admitted `AdmissionRecord` together, under a per-ticket check-and-set
  (conditional update on the ticket row; never a table lock), so an admitted ticket
  always has its evidence and concurrent scans admit once. Rejections are appended
  separately; losing one is acceptable, losing an admission record is not.
- **Same-time group entry = one code for the group.** One code presents up to 10
  not-yet-entered tickets of the event (the fan may untick companions arriving later),
  so one scan admits the group and staff read a head count. Each ticket is decided
  independently. Because the code is made only on the holder's registered device,
  there is no off-platform distribution vector.
- **No personal data on the reception screen.** Admit returns the head count, the
  reasons and, for an already-used ticket, the earlier time and link name; never a
  name or contact. 不正転売禁止法 is satisfied by the name on the ticket face the fan
  shows; when an identity check is wanted, staff compare that face with an ID.
- **Link tokens and throttling.** Link tokens are at least 128 random bits, compared in
  constant time and never shown again once bound; the reception boundary throttles
  clients that try many unknown tokens.
- **Void → refused at admission.** A Voided ticket (refund, resale) is refused by
  `Ticket.Admit`; ⑦ relies on this.
- **Entity conventions (proto stage).** Wrapper-message type-safe ids, enum statuses
  and reasons, protovalidate (`proto/CLAUDE.md`).

## Risks / Trade-offs

- **App-first costs lock-screen convenience at the gate** (the fan opens the tickets
  screen). *→* Accepted for MVP; OS Wallet convenience can return later as a caveated
  tier.
- **The fan must open the tickets screen online once before the venue.** *→* The screen
  registers the key on any online visit, says plainly when it has not, and purchase
  confirmation leads to the tickets screen.
- **One device at a time.** A fan who opens the tickets screen on a second device moves
  the key there; codes from the first device stop working. *→* The screen says so when
  it happens; staff see "not a valid entry code" with the next step.
- **XSS can make the device sign.** *→* Strict CSP and the usual XSS discipline; the
  impact is bounded by one admission per ticket.
- **Reception needs a connection per scan** (fail closed). *→* Reception devices on
  venue Wi-Fi or a reliable uplink; checked for the pilot venue in #1076. An offline
  reception mode is the future lever.
- **Decoder accuracy on iPhones** with the library decoder is unproven on fans' phone
  screens in dim light. *→* An early spike on real devices (tasks 0.4); if it falls
  short, the fallback is ZXing compiled to WebAssembly behind the same interface.
- **A bound reception device is lost or replaced mid-show.** *→* Revoke-and-reissue in
  the console; documented in the reception runbook.
- **Ticket type is not modelled.** The reception screen shows a head count only.

## Migration Plan

New capability on ⑤'s Ticket. Sequence: proto (ticket admitted time, WalletPublicKey,
AdmissionCode format, ReceptionLink, AdmissionRecord, fan RegisterWalletPublicKey,
organizer reception-link and reception services) → BSR → backend (migration for the
admitted time and the wallet key, reception link and admission record tables;
signature verification for AdmissionCodes and reception calls; atomic admit with its
record; reception link usecases; reception boundary without sign-in, with throttling)
→ frontend (tickets screen with key registration, offline code generation and wake
lock in the fan app; reception and reception-links screens in the organizer app, the
reception route exempt from the console sign-in). The Base45 payload layout is
specified once in design notes of the proto PR and shared by the fan app and backend
tests.

## Open Questions

- **Are the 15-second rotation and the 30-second acceptance right?** Revisit after the
  pilot's admission records (#1076).
- **Payload layout details** (field order, version byte) are fixed in the proto PR;
  they do not change the specs.
