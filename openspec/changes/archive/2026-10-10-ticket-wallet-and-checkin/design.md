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
- **One key per User; the entry device moves only when the fan asks (2026-10-08).**
  Registering a new device's key replaces the old one, so codes from a replaced phone
  are refused. Opening or reloading the tickets screen only *reads* the fan's key
  (`WalletPublicKeyService.Get`) and compares it with the device's own: the first
  device registers automatically, but another device only offers "use this device
  for the QR code" and registers on confirmation. Registering on every visit was
  rejected: glancing at tickets on a PC would silently move the key, and the phone,
  offline in the venue, would show codes that are refused.
- **Wallet keys have their own service.** `rpc.wallet_public_key.v1.WalletPublicKeyService`
  (`Register` / `Get`), not TicketService: the key is a resource of its own (one per
  User, replaced on a new device), and "Admission" already names the record of a
  ticket let in.
- **The fan app starts offline.** The service worker serves the app shell
  (`index.html`) and the last good `/config.json` when the network fails, so the
  tickets screen and the QR code open in a venue without signal even after the app
  was closed. `/config.json` is network-first with that fallback, not network-only.
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
- **Reception is hosted apart from the console (2026-10-09).** The reception screen
  and the reception guide are a separate build served at `reception.liverty-music.app`,
  and `ReceptionService` is served by its own `reception-api` workload at
  `api.reception.liverty-music.app` with a reception-only database role; the organizer
  console origin and API serve signed-in operators only. Decided and implemented in
  `isolate-venue-reception`, so that untrusted QR and fragment input is never decoded
  on the origin holding console tokens. Real-device checks and the production E2E run
  on the reception origin, since camera permission and the device key are stored per
  origin.
- **The start time is required when a sale is set up; the open time stays optional.**
  Publishing an event keeps both optional (dates are often announced before times),
  but a ticketed event must have a start time: the ticket face shows it and the
  reception window falls back to it when doors are not announced. This change adds the rule to the lottery (`ConfigureLotteryPhase` and the
  lottery phase editor), because no other active change owns it; the planned
  first-come sale must carry the same rule (#1074). Phases configured before this
  change are not revisited: the pilot sells first come, first served, and a reception
  link still refuses an event without a start time.
- **Decoding: `BarcodeDetector` when it supports QR, otherwise ZXing compiled to
  WebAssembly, in a Web Worker (2026-10-09).** Chrome's guidance treats the Shape
  Detection API as an optimisation to combine with one's own decoder. It is available
  on Chrome for Android but disabled by default on Safari up to the current iOS 27 and
  absent on Firefox, so staff iPhones use the fallback. The fallback is ZXing rather
  than `@paulmillr/qr`: the latter failed on 1–4% of perfectly rendered AdmissionCodes
  at the desk, and the reception path cannot afford a weak decoder in dim venues.
  `@paulmillr/qr` stays the encoder on the fan side. Frames are taken from
  `getUserMedia` with `facingMode: { ideal: 'environment' }` and decoded off the main
  thread, behind one decoder interface so the choice can change without touching the
  screen. No standalone decoder spike: the reception screen itself is measured on real
  iPhones and Android phones (task 5.6) and in the rehearsal (#1076).
- **The reception screen runs in a browser tab, not installed.** iOS does not keep the
  camera permission for home-screen web apps and asks again repeatedly (WebKit
  185448), and iOS 26 has camera orientation problems in home-screen apps. In a Safari
  tab the permission behaves normally. The camera is requested only when staff tap to
  start scanning.
- **Admission is one step.** `Ticket.Admit` sets the admitted time and
  stores the `Admission` together, under a per-ticket check-and-set
  (conditional update on the ticket row; never a table lock), so an admitted ticket
  always has its evidence and concurrent scans admit once. Rejections are appended
  separately as `RejectedScan`s; losing one is acceptable, losing an Admission is
  not. The two are separate entities because their guarantees differ: an Admission
  always names a ticket and has no reason; a RejectedScan has a reason and names a
  ticket unless the code was forged (2026-10-08).
- **Same-time group entry = one code for the group.** One code presents up to 10
  not-yet-entered tickets of the event, with no way to leave one out, so one scan
  admits the group and staff read a head count. Each ticket is decided
  independently. Because the code is made only on the holder's registered device,
  there is no off-platform distribution vector.
- **Companions enter together; no leaving a ticket out (2026-10-10).** An earlier draft
  let the fan untick companions arriving later. It was dropped: the ticketing roadmap
  (`docs/ticketing-platform-roadmap.md`, "Companion group entry = same-time entry")
  has the lead and companions enter together, and unticking made reception harder.
  Offline in the venue, the fan's phone does not learn which tickets were admitted,
  so a later code would present them again and staff would see a partial OK. Late
  companions wait with the lead. Account-bound distribution of companion tickets is
  the roadmap's open question (`docs/market-design-notes.md` "#4 分配
  reconsideration"), not part of this change.
- **A code presenting a ticket that is not the user's own is refused as a whole
  (2026-10-10).** The tickets screen only ever presents the user's own tickets of one
  event, and a ticket's holder never changes (official resale voids the ticket and
  issues a new one), so such a code can only be built outside the app. Admit refuses
  it as Forged, "not a valid entry code", instead of admitting the rest; staff have one
  reason less to learn. `RejectedScanReason.NOT_HOLDER` stays in the proto, unused.
- **No personal data on the reception screen.** Admit returns the head count, the
  reasons and, for an already-used ticket, the earlier time and link number; never a
  name or contact. 不正転売禁止法 is satisfied by the name on the ticket face the fan
  shows; when an identity check is wanted, staff compare that face with an ID.
- **Link tokens and throttling.** Link tokens are at least 128 random bits, compared in
  constant time and never shown again once bound; the reception boundary throttles
  clients that try many unknown tokens.
- **Void → refused at admission.** A Voided ticket (refund, resale) is refused by
  `Ticket.Admit`; ⑦ relies on this.
- **Entity conventions (proto stage).** Wrapper-message type-safe ids, enum statuses
  and reasons, protovalidate (`proto/CLAUDE.md`).

### Wire formats (fixed in the proto PR)

Documented on `entity.v1.AdmissionCode` and `rpc.organizer.reception.v1.ReceptionService`;
shared by the fan app, the reception screen and backend tests.

- **Keys and signatures.** Public keys are the 65-byte uncompressed SEC1 point
  (`exportKey("raw")`, `entity.v1.PublicKey`); signatures are ECDSA P-256 /
  SHA-256 in IEEE P1363 `r || s`, 64 bytes (`entity.v1.Signature`), as
  WebCrypto produces them.
- **AdmissionCode payload** (big-endian, ids as 16 raw UUID bytes, Base45 text):
  version `0x01` (1) · user id (16) · event id (16) · ticket count N, 1-10 (1) ·
  N ticket ids (16 each) · signed time, Unix seconds (4) · signature (64) over every
  byte before it. 118 bytes for one ticket, 262 bytes / 393 Base45 characters for ten.
- **Reception call signature input**: the UTF-8 lines `liverty-music.reception.v1`,
  the Connect procedure path, the link token, the signed time in decimal Unix seconds and
  the call content (Open: the device public key in base64url without
  padding; Admit: the scanned text), joined by `\n` with no trailing newline.
- **RPC packages.** One service per package with bare verbs, like
  `rpc.admin.organizer.v1`: `rpc.organizer.reception_link.v1.ReceptionLinkService`
  (Issue / List / Revoke) and `rpc.organizer.reception.v1.ReceptionService`
  (Open / Admit). The reception call signature names the full Connect procedure.
- **Timestamps** follow AIP-142 (`*_time`; `*_at` is for DB columns only).
- **One `PublicKey` value for both sides.** Fan and reception devices hold the same
  kind of key, so one `entity.v1.PublicKey` (and `entity.v1.Signature`) is used by
  both; the field says whose it is: `WalletPublicKey.public_key` for a fan's device,
  `ReceptionLink.bound_public_key` for a reception device. The reception call carries
  the link token, sign time and signature as plain request fields, as the adapter
  spec words them.
- **Reception links are numbered, not named (2026-10-08).** A free name only helped the
  Organizer tell devices apart, which a server-assigned number shown as 受付1, 受付2 …
  does as well, without a name rule, a duplicate check or an AlreadyExists failure.
  Numbers are never reused within an event, so a number always means one device in
  admission results. A link has no created time: no requirement reads it, and links
  are listed by number.

### Decoder spike (task 0.4)

- **Desk measurement, 2026-10-08 (before real devices).** `@paulmillr/qr`'s decoder
  failed on about 1–4% of perfectly rendered random AdmissionCodes (100 codes each for
  118 and 262 bytes, at 4, 6 and 8 px per module; no camera involved). Each scan reads
  many frames, so a single-frame failure rate may only cost time, but this is the
  iPhone reception path. The real-device runs below decide whether to switch to ZXing
  WebAssembly behind the same interface.
- **No standalone spike (2026-10-09).** A dev-only spike page was built (frontend #696)
  but not used: dev is shut down and a debug page should not go to prod. The decision
  above takes ZXing from the start instead, and real-device numbers come from the
  reception screen (task 5.6) and the rehearsal (#1076), recorded here.

- **Real devices, 2026-10-10 (prod).** Reception on Android Chrome (rear camera,
  `BarcodeDetector` path) read codes shown on a PC screen in about one second, for 3 and
  10 tickets at normal brightness and for 10 tickets at the lowest screen brightness.
  Every scenario of `stories/enter-a-venue-with-a-ticket` behaved as specified. Not
  measured: the ZXing path on a real iPhone (no iPhone available); in CI's WebKit it
  decodes a 300-character code in about 100 ms. Revisit at the pilot rehearsal (#1076).

### Manual verification

@spec-manual components/infrastructure/fan/web/route/tickets "iPhone" -- not verified on an iPhone (none available); the screen was checked on prod in desktop Chrome and Edge and on Android Chrome on 2026-10-10, and runs in WebKit in CI
@spec-manual components/infrastructure/organizer/web/route/reception "Staff iPhone" -- not verified on an iPhone (none available); scanning was checked on prod with Android Chrome on 2026-10-10, and the ZXing worker decodes under the reception CSP in WebKit in CI
@spec-manual stories/enter-a-venue-with-a-ticket "Group of three enters" -- one scan of a 3-ticket code showed OK 3名 with no name; checked by hand on prod on 2026-10-10 (task 7.3): fan on desktop Chrome/Edge, reception on Android Chrome scanning with its camera; a camera reading a code from another screen cannot be automated
@spec-manual stories/enter-a-venue-with-a-ticket "No signal in the venue" -- the fan's tab was offline (DevTools) while a 10-ticket code was shown and admitted; checked by hand on prod on 2026-10-10 (task 7.3): fan on desktop Chrome/Edge, reception on Android Chrome scanning with its camera; a camera reading a code from another screen cannot be automated
@spec-manual stories/enter-a-venue-with-a-ticket "Same code at two entrances" -- a used code was refused as already used with the earlier time and link; the concurrent case is covered by the backend integration test of TicketUseCase.Admit; checked by hand on prod on 2026-10-10 (task 7.3): fan on desktop Chrome/Edge, reception on Android Chrome scanning with its camera; a camera reading a code from another screen cannot be automated
@spec-manual stories/enter-a-venue-with-a-ticket "Screenshot sent to a friend" -- a screenshot shown 60 s later, with the live code closed, was refused as expired; checked by hand on prod on 2026-10-10 (task 7.3): fan on desktop Chrome/Edge, reception on Android Chrome scanning with its camera; a camera reading a code from another screen cannot be automated
@spec-manual stories/enter-a-venue-with-a-ticket "Link forwarded" -- the same reception link opened in a second browser was refused as in use on another device; checked by hand on prod on 2026-10-10 (task 7.3): fan on desktop Chrome/Edge, reception on Android Chrome scanning with its camera; a camera reading a code from another screen cannot be automated
@spec-manual stories/enter-a-venue-with-a-ticket "Lost phone revoked" -- a revoked link could no longer be used and the reissued link worked; checked by hand on prod on 2026-10-10 (task 7.3): fan on desktop Chrome/Edge, reception on Android Chrome scanning with its camera; a camera reading a code from another screen cannot be automated

Deferred follow-ups (OS Wallet passes, 顔認証 / ID mode, NFC tap, offline reception, a
Zitadel `reception` role, ticket types at reception) are tracked in
liverty-music/specification#1112.

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
- **Decoder speed and accuracy on iPhones** in dim light are measured only once the
  reception screen exists. *→* ZXing from the start, behind one decoder interface;
  time-to-decode and failures are recorded from task 5.6 and the rehearsal.
- **A bound reception device is lost or replaced mid-show.** *→* Revoke-and-reissue in
  the console; documented in the reception runbook.
- **Ticket type is not modelled.** The reception screen shows a head count only.

## Migration Plan

New capability on ⑤'s Ticket. Sequence: proto (ticket admitted time, WalletPublicKey,
AdmissionCode format, ReceptionLink, Admission, RejectedScan, fan RegisterWalletPublicKey,
organizer reception-link and reception services) → BSR → backend (migration for the
admitted time and the wallet key, reception link, admission and rejected scan tables;
signature verification for AdmissionCodes and reception calls; atomic admit with its
record; reception link usecases; reception boundary without sign-in, with throttling)
→ frontend (tickets screen with key registration, offline code generation and wake
lock in the fan app; reception and reception-links screens in the organizer app, the
reception route exempt from the console sign-in). The Base45 payload layout is
specified once in design notes of the proto PR and shared by the fan app and backend
tests.

## Open Questions

- **Are the 15-second rotation and the 30-second acceptance right?** Revisit after the
  pilot's admissions and rejected scans (#1076).
- ~~Payload layout details~~ — fixed in the proto PR (see "Wire formats" below).
