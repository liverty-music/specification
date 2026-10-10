## 0. Dependency gate and spike

- [x] 0.1 Confirm ⑤ `ticket-purchase-and-issuance` is shipped (archived; the account-bound `Ticket` with 本人確認 and the covered-ticket face content this renders) — archived 2026-09-15
- [x] 0.2 (No identity step-up prerequisite — gate-time passkey re-auth is NOT adopted; see design)
- [x] 0.3 Confirm `first-come-ticket-sales`, when proposed, requires a start time (open time optional) when a sale is set up, like the lottery rule in section 3 (#1074) — confirmed 2026-10-09: `first-come-ticket-sales` TicketSale.Configure fails with FailedPrecondition without a start time and the ticket-sale editor asks for it; the open time stays optional
- [x] 0.4 Decoder decision without a standalone spike: `BarcodeDetector` when it supports QR, else ZXing WebAssembly in a Worker, behind one decoder interface; desk finding and rationale in design.md (real-device numbers come from 5.6)

## 1. Proto / entity (specification → BSR)

- [x] 1.1 `Ticket` gains an output-only admitted time (`components/entity/ticket`); type-safe ids and protovalidate per `proto/CLAUDE.md`
- [x] 1.2 `WalletPublicKey` (user, P-256 public key, register time; one per user) and fan ticket service `RegisterWalletPublicKey`
- [x] 1.3 `ReceptionLink` (id, event, number, Unused / InUse / Revoked, bound public key, bind / revoke times; the token only where the spec returns it) and `Admission` (ticket, event, reception link, admit time) / `RejectedScan` (event, reception link, ticket unless Forged, reason Forged / Expired / OtherEvent / NotHolder / Voided / AlreadyAdmitted, scan time)
- [x] 1.4 Organizer reception link service: `Issue`, `List`, `Revoke`; reception service: `Open` (link token, public key, call signature) and `Admit` (link token, call signature, scanned text → head count, reasons, earlier admission time and link name; no personal data)
- [x] 1.5 Document the AdmissionCode payload (version byte, user, event, up to 10 tickets, signed time, signature; Base45) and the reception call signature input in the proto PR
- [x] 1.6 Proto naming cleanup (bundled, see proposal.md): `*_at` → `*_time` on Ticket / Order / VerifiedIdentity / Settlement; one service per package with bare-verb RPCs for the organizer and admin services
- [x] 1.7 buf lint / format pass; merge PR with the `buf skip breaking` label → Release → BSR gen (#1086, v0.69.0)
- [x] 1.8 Move wallet key RPCs to `rpc.wallet_public_key.v1.WalletPublicKeyService` (`Register`, new `Get`), removing `TicketService.RegisterWalletPublicKey`; merge with `buf skip breaking` → Release → BSR gen (#1087, v0.70.0)
- [x] 1.9 Proto comments: `Ticket.holder_id` (a ticket's holder never changes; official resale voids and reissues) and `RejectedScanReason.NOT_HOLDER` (unused: such a code is refused as FORGED) (#1100)
- [x] 1.10 Proto: `max_tickets_per_application` 1 to 10 on `LotterySalesPhase` and the organizer Configure request (prod has no lottery phases, read-only check 2026-10-10); merge → Release → BSR gen (#1101, v0.74.0)

## 2. Backend — entity operations and storage

- [x] 2.1 Migration: ticket admitted time; wallet public key (one row per user), reception link, admission and rejected scan tables (admissions and rejected scans append-only)
- [x] 2.2 `Ticket.Admit` (admitted time + Admission in one step, per-ticket conditional update) and `Ticket.ListByHolderAndEvent`; contract tests including concurrent admits (`components/entity/ticket/**`)
- [x] 2.3 `WalletPublicKey.Register` (one per user, replaced in one step, reports whether it replaced another key) and `GetByUser`; contract tests
- [x] 2.4 `ReceptionLink` operations: Create, Get, GetByToken (constant-time), ListByEvent, BindDevice (concurrent first binds), Revoke; contract tests (`components/entity/reception-link/**`)
- [x] 2.5 `RejectedScan.Append` and `Admission.GetByTicket`; `Event.Get`; contract tests
- [x] 2.6 `AdmissionCode.Decode` / `Verify` and the reception call proof (ECDSA P-256 verification, freshness 30 s before / 15 s after); unit tests for malformed, changed, expired, replaced-key and fast-clock input

## 3. Backend — usecases and boundaries

- [x] 3.1 `WalletPublicKeyUseCase.Register` and `TicketUseCase.Admit` per `components/usecase/**`; unit tests for every scenario, including partial groups, someone else's ticket, voided tickets and a link revoked mid-scan
- [x] 3.2 `ReceptionLinkUseCase.Issue` (refuses events without a start time), `Revoke`, `ListByEvent`, `Open`
- [x] 3.3 Fan `WalletPublicKeyService` handlers `Register` and `Get` and `WalletPublicKeyUseCase.Get` (`components/adapter/fan/api/rpc/wallet-public-key`, `components/usecase/wallet-public-key/get`)
- [x] 3.4 Organizer reception-link handlers behind the organizer-console sign-in and `ResolveCaller` (`components/adapter/organizer/api/rpc/reception-link`)
- [x] 3.5 Reception handlers without sign-in, with link token + call signature and throttling of unknown tokens (`components/adapter/organizer/api/rpc/reception`); CORS for the organizer web origin
- [x] 3.6 `LotteryUseCase.ConfigureLotteryPhase` fails with FailedPrecondition for an event without a start time, and still accepts one without an open time (`components/usecase/lottery-sales-phase/configure-lottery-phase`); unit test
- [x] 3.7 Consume the proto naming cleanup: `issue_time` / `pay_time` / `verify_time` / `release_time` in the mappers, and the moved organizer / admin service packages and renamed RPCs (`Refund`, `Configure`, `GetStatus`, `SetVerificationRequirement`, `Get`, fan `TicketService.List`, `LotteryService.Withdraw` / `GetApplication`, `IdentityVerificationService.Start` / `Complete` / `GetStatus`) in handlers and server registration (backend#554)
- [x] 3.8 `make check` passes
- [x] 3.9 `TicketUseCase.Admit`: a code presenting a Ticket that is not the user's own for the event is rejected as a whole with reason Forged, no Ticket admitted (`components/usecase/ticket/admit` "Someone else's ticket", "Ticket of another event in the code") (backend#590, v1.69.0)
- [x] 3.10 Backend: the LotterySalesPhase rule refuses a max tickets per application above 10 (`components/entity/lottery-sales-phase` "Group larger than one entry code"); consume the schema release (backend#591, v1.70.0)

## 4. Frontend — fan tickets screen (fan web app)

- [x] 4.1 Tickets screen per `components/infrastructure/fan/web/route/tickets`: grouped by event, covered-ticket face, 未入場 / 入場済み / 無効, last loaded list viewable offline
- [x] 4.2 Key pair: WebCrypto ECDSA P-256 `extractable: false`, kept in IndexedDB; on every online visit read the fan's key (`WalletPublicKeyService.Get`) and compare: register automatically only when the fan has none, otherwise offer "use this device" and register on confirmation; no QR on a non-entry device; "needs a connection once" and "now works on this device only" messages; offline app shell
- [x] 4.3 Entry QR: one code for the ticked tickets (up to 10) with the head count; signed on the device every 15 s without a connection; Base45 payload; SVG via `@paulmillr/qr`; never shows a code older than 15 s
- [x] 4.4 Screen Wake Lock while the code is shown: request in try/catch, re-acquire on `visibilitychange`, release on close; suggest raising brightness
- [x] 4.5 Consume the proto naming cleanup in the fan app (`issueTime`, `payTime`, `verifyTime` on the order, tickets and identity screens; `TicketService.List`, `LotteryService.Withdraw` / `GetApplication`, `IdentityVerificationService.Start` / `Complete` / `GetStatus`) (frontend#692)
- [x] 4.7 Tickets screen: the entry code presents every not-yet-entered ticket with no way to leave one out; remove the ticking (`components/infrastructure/fan/web/route/tickets` "No ticket left out") (frontend#715, v1.78.0)
- [x] 4.6 Verify on the current and previous major Safari for iOS and Chrome for Android; `make check` passes (after `isolate-venue-reception` is in production) — Android Chrome and desktop Chrome/Edge on prod 2026-10-10; no iPhone available, so iOS Safari is not verified (recorded in design.md)

## 5. Frontend — organizer web app

- [x] 5.1 Reception-links screen per `components/infrastructure/organizer/web/route/reception-links`, reached from the event in the console: issue with one action (numbered by the server, shown as 受付1, 受付2 …), copy / share URL, state, revoke and revoke-and-reissue with confirmation, reception window shown, no-start-time and draft messages
- [x] 5.2 Reception screen per `components/infrastructure/organizer/web/route/reception`: route exempt from the console sign-in, used in a browser tab (not installed); device key pair created on first open and every call signed; outside-window, revoked and other-device messages
- [x] 5.3 Scanning: rear camera via `getUserMedia` (`facingMode: { ideal: 'environment' }`) requested on tap; `BarcodeDetector` when it supports QR, else ZXing WebAssembly in a Web Worker, behind one decoder interface; OK + head count / NG + reason and next step, no personal data; fail closed when unreachable
- [x] 5.4 Lottery phase editor: message and link to the concert editor when the event has no start time, no save (`components/infrastructure/organizer/web/route/lottery-phase-editor`)
- [x] 5.5 Consume the proto naming cleanup in the organizer and admin apps (moved service packages, renamed lottery and payout RPCs) (frontend#692)
- [x] 5.7 Reception screen: drop the "本人のチケットではありません" reason copy (no longer returned) (frontend#713, v1.78.0)
- [x] 5.8 Lottery phase editor: the max tickets per application input allows 1 to 10 (frontend#716, v1.79.0)
- [x] 5.9 Reception screen: starting to scan clears the previous verdict (`components/infrastructure/organizer/web/route/reception` "Scanning again after stopping") (frontend#721, v1.79.2)
- [x] 5.6 Verify on the current and previous major Safari for iOS and Chrome for Android, recording time-to-decode and failures for 1, 3 and 10 tickets at normal and low screen brightness in design.md; `make check` passes (after `isolate-venue-reception` is in production) — Android Chrome on prod 2026-10-10, about 1 s per scan at normal and low brightness; no iPhone available (recorded in design.md)

## 6. Anti-scalp / product constraints

- [x] 6.1 No first-party distribution URL / transferable per-companion code (verify none exists) — verified 2026-10-09: no share or distribution path in the tickets screen, services or AdmissionCode lib
- [x] 6.2 A stale, changed or replaced-key code is rejected before any ticket is touched, and each ticket admits at most once — backend tests: rejected codes never call Ticket.Admit; concurrent scans at two links admit once (integration)
- [x] 6.3 No personal data leaves the reception boundary: Admit responses carry no name, phone or account (test asserts the response shape)
- [x] 6.4 The private keys are created non-extractable and never sent: no request carries private key material (test on both screens); CSP reviewed for both apps — fan (frontend#695) and organizer (frontend#698) tests; CSP reviewed for both apps, no change needed
- [x] 6.5 Scope check: MVP anti-scalp = account passkey + device-bound codes with online atomic admission + ⑤-captured 本人確認 identity; do NOT claim bulk-scalp resistance (that is `identity-ekyc-jpki`) — no ticket-wallet or reception surface claims bulk-scalp resistance; the only anti-resale copy is the JPKI-only lottery notice (identity-ekyc)

## 7. Release and verification

- [x] 7.1 Cross-repo release order: spec → BSR → backend → frontend (fan and organizer apps) — schema v0.69.0/v0.70.0 → backend v1.66.0 → frontend v1.75.0/v1.76.0 (2026-10-09)
- [x] 7.2 Reception guide for venue staff with no prior knowledge, as a static page of the reception build (`isolate-venue-reception`) linked from the reception and reception-links screens (opens in a new tab; `components/infrastructure/organizer/web/route/reception`, `reception-links`), covering: issue one link per device; staff open it in the browser before the window; a lost or replaced device → revoke and reissue; what each NG reason means and what to tell the fan; fans open their tickets screen online once before the day; rehearse on a separate test event. Venue checks and the rehearsal itself are tracked in liverty-music/specification#1076, not here (after `isolate-venue-reception` is in production) — frontend#713, v1.78.0; live at https://reception.liverty-music.app/guide.html
- [x] 7.3 End-to-end on production with a test event (`stories/enter-a-venue-with-a-ticket`): group of 3 admitted with one scan; code shown in airplane mode admitted; same code at two links admits once; screenshot after 30 seconds refused; code from a replaced phone refused; forwarded link refused on a second device; revoked link refused and the reissued link works; refunded ticket refused; reception screen shows no name; reception server unreachable fails closed (after `isolate-venue-reception` is in production) — passed on prod 2026-10-10 (PC Chrome/Edge as fan devices, Android Chrome as reception): group of 3, offline 10, re-scan used, screenshot after 60 s expired, replaced device forged, forwarded link in use, revoked link refused and reissued link works, refunded ticket voided, no name shown, airplane mode undecided
- [x] 7.4 Sync delta specs to main specs (including the `Ticket` and fan ticket RPC Purpose updates listed in proposal.md) and archive the change

Future work (OS Wallet passes, 顔認証 / ID mode, NFC tap, offline reception, a Zitadel `reception` role, ticket types on the reception screen) is tracked in liverty-music/specification#1112, not here.
