## Why

Phase 3 step ⑥ — the last ticketing MVP capability. ⑤ issues **account-bound
Tickets**, but a fan cannot yet *use* one: there is no wallet to show it, no
forge-resistant entry credential, and no way for staff to admit attendees. This
change adds the **wallet + entry** layer: view your ticket (incl. its
covered-ticket face), enter with an **in-app dynamic QR made and signed on the fan's own
device**, companion **same-time group entry**, and a **reception screen**
that scans via the web camera and validates each scan with **signature + freshness
then an online atomic admission**.

The pilot with an independent artist (liverty-music/specification#1074) needs this
at the venue, where **reception is run by venue staff from outside the Organizer**.
They have no account and must not get the Organizer's console rights, so admission
goes through an **Organizer-issued, event-scoped reception link** bound to one
device (decided 2026-10-07).

Anti-scalp is **not** enforced by a gate-time re-authentication (explored and
rejected — see design.md); it rests on the platform's tiered model (account
passkey + JPKI eKYC lane + signed-credential/dedup + official resale + future
per-event 顔認証). **OS Wallet passes are a deferred convenience tier**, not the
MVP baseline (see design Non-Goals). Roadmap:
[`ticketing-platform-roadmap.md`](../../../docs/ticketing-platform-roadmap.md).

## What Changes

- **Ticket wallet** — a fan views their issued tickets grouped by event, each with
  its **covered-ticket (特定興行入場券) face** (resale-without-consent notice, holder
  name, no seat) and its state (未入場 / 入場済み / 無効); the last loaded list stays
  viewable offline.
- **Entry QR code made on the fan's phone, offline (2026-10-08)** — on the first online
  visit the phone creates a non-extractable key pair and registers only its public key
  (`WalletPublicKey`); at the venue it signs an **AdmissionCode** every 15 seconds with
  no connection. The server checks the signature and freshness, so a screenshot or a
  code from another device admits no one. One active key per fan. **Not an
  OS-shareable pass; no gate-time re-auth.**
- **Same-time group entry with one QR** — one code presents up to 10 not-yet-entered
  tickets of the event (the fan may untick companions arriving later); one scan admits
  the group and staff see the head count. **No first-party distribution URL.**
- **Admission = signature + freshness, then a per-ticket atomic admit** — the ticket's
  admitted time and its admission record are stored together, so concurrent scans at
  two entrances admit each ticket exactly once; a voided (refunded or resold) ticket
  and someone else's ticket are refused; server unreachable **fails closed**.
- **Reception links** — the Organizer issues named links (受付A, 受付B …) per event in
  the console; the first device that opens a link **binds its own public key** and
  signs every later call; the link works only inside a **fixed reception window**
  (3 hours before doors until 04:00 JST the next day) and can be **revoked or
  revoked-and-reissued** at once. No account, no PIN, no organizer rights for staff.
- **Reception screen** — opened from the link in the phone's browser tab without a
  sign-in or install; scans with the rear camera (`BarcodeDetector` where available,
  a small decoder otherwise); shows **OK + head count or NG + reason and next step,
  never any personal data**.
- **Admission record as attendance evidence** — every admission and every rejected
  scan is recorded append-only with the reception link and the time, for a future
  chargeback representment (`dispute-representment`).

Scope guardrails (MVP): electronic tickets only; the fan side works offline, the
reception side is **online-first, fail-closed**. **OS Wallet passes, NFC tap, offline
reception, per-event 顔認証/ID, a Zitadel `reception` role and a reception test mode
are out of scope** (rehearsals use a separate test event). MVP anti-scalp = account
passkey + device-bound codes with online atomic admission + the ⑤-captured 本人確認
identity; bulk-scalp resistance arrives with `identity-ekyc-jpki`.

## Capabilities

### New Capabilities

- `components/entity/admission-code`: the device-signed, short-lived code the entry QR carries
- `components/entity/admission-code/decode`, `verify`
- `components/entity/wallet-public-key`: the public key of the fan's device that shows tickets, one active per User
- `components/entity/wallet-public-key/register`, `get-active-by-user`
- `components/entity/reception-link`: the link venue staff admit through; name rule, lifecycle, device proof, reception window
- `components/entity/reception-link/create`, `get`, `get-by-token`, `list-by-event`, `bind-device`, `revoke`
- `components/entity/admission-record`: append-only admission and rejection records
- `components/entity/admission-record/append`, `get-admission-by-ticket`
- `components/entity/ticket/admit`: admit a ticket once, together with its admission record
- `components/entity/ticket/list-by-holder-and-event`
- `components/entity/event/get`: an event's current date, open and start times
- `components/usecase/wallet-public-key/register`
- `components/usecase/reception-link/issue`, `revoke`, `list-by-event`, `open`
- `components/usecase/ticket/admit`
- `components/adapter/organizer/api/rpc/reception-link`: operator gate for issuing, listing and revoking links
- `components/adapter/organizer/api/rpc/reception`: the link-and-device-signature gate for reception calls, no sign-in
- `components/infrastructure/fan/web/route/tickets`: the wallet and the offline entry QR code
- `components/infrastructure/organizer/web/route/reception`: the reception screen
- `components/infrastructure/organizer/web/route/reception-links`: the console screen for reception links
- `stories/enter-a-venue-with-a-ticket`

### Modified Capabilities

- `components/entity/ticket`: "A ticket is admissible only once and only while Issued" (added). (Purpose) attribute table gains a row **admitted time** — when the ticket was admitted; optional, absent until admitted, kept when the ticket is later Voided; updated in the main spec at archive.
- `components/usecase/lottery-sales-phase/configure-lottery-phase`: "Configure a phase for a published event" (modified) — a lottery phase can be configured only for an event with an open time and a start time.
- `components/infrastructure/organizer/web/route/lottery-phase-editor`: "An event goes on sale only with its times" (added).
- `components/adapter/fan/api/rpc/ticket`: "RegisterWalletPublicKey is for the signed-in fan only" (added). (Purpose) now covers registering the wallet public key; updated in the main spec at archive.

## Impact

- **Depends on:** ⑤ `ticket-purchase-and-issuance` (archived; the issued Ticket,
  its 本人確認 and covered-ticket face). Works the same for tickets issued by the
  lottery and by the planned first-come sale.
- **Enables:** ⑦ `official-resale` — a resold seat's old ticket is Voided and its
  credential refused at admission; `dispute-representment` — admission records as
  attendance evidence.
- **New:** wallet public keys and signature verification, per-ticket atomic admit
  with its record, reception links bound to a device key, reception screen in the
  organizer web app reachable without a sign-in, console screen for links.
- **Sales rule (in this change for the lottery):** a lottery phase can only be set up
  for an event with an open time and a start time; the planned `first-come-ticket-sales`
  must carry the same rule (recorded in liverty-music/specification#1074). A reception
  link cannot be issued for an event without an open time.
- **Product constraints honored:** **Web-First / No Native App**; **no first-party
  distribution URL**; no personal data shown to external staff.
- **Deferred (future):** OS Wallet passes; NFC tap; offline scanning; per-event
  顔認証; a Zitadel `reception` role for standing reception teams (can coexist
  with links).
- **Withdrawn:** the previously-proposed identity-management **step-up primitive**.
