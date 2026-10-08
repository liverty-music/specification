## 0. Dependency gate and spike

- [ ] 0.1 Confirm ⑤ `ticket-purchase-and-issuance` is shipped (archived; the account-bound `Ticket` with 本人確認 and the covered-ticket face content this renders)
- [ ] 0.2 (No identity step-up prerequisite — gate-time passkey re-auth is NOT adopted; see design)
- [ ] 0.3 Confirm `first-come-ticket-sales`, when proposed, requires an open and a start time when a sale is set up, like the lottery rule in section 3 (#1074)
- [ ] 0.4 Spike on real devices: a Base45 AdmissionCode for 1, 3 and 10 tickets rendered by `@paulmillr/qr` on an iPhone and an Android phone, decoded by the reception screen's camera path (`BarcodeDetector` on Chrome for Android, `@paulmillr/qr` in a Worker on Safari for iOS) at normal and low screen brightness; record time-to-decode and failures in design.md. If the library decoder falls short on iOS, switch to ZXing WebAssembly behind the same interface before section 5

## 1. Proto / entity (specification → BSR)

- [ ] 1.1 `Ticket` gains an output-only admitted time (`components/entity/ticket`); type-safe ids and protovalidate per `proto/CLAUDE.md`
- [ ] 1.2 `WalletPublicKey` (id, user, P-256 public key, Active / Replaced, registered / replaced times) and fan ticket service `RegisterWalletPublicKey`
- [ ] 1.3 `ReceptionLink` (id, event, name 1-20 chars, Unused / InUse / Revoked, bound public key, created / bound / revoked times; the token only where the spec returns it) and `AdmissionRecord` (event, reception link, optional ticket, outcome, reason Forged / Expired / OtherEvent / NotHolder / Voided / AlreadyAdmitted, time)
- [ ] 1.4 Organizer reception link service: `Issue`, `List`, `Revoke`; reception service: `Open` (link token, public key, call signature) and `Admit` (link token, call signature, scanned text → head count, reasons, earlier admission time and link name; no personal data)
- [ ] 1.5 Document the AdmissionCode payload (version byte, user, event, up to 10 tickets, signed time, signature; Base45) and the reception call signature input in the proto PR
- [ ] 1.6 buf lint / format / breaking pass; merge PR → Release → BSR gen

## 2. Backend — entity operations and storage

- [ ] 2.1 Migration: ticket admitted time; wallet public key, reception link and admission record tables (admission records append-only)
- [ ] 2.2 `Ticket.Admit` (admitted time + Admitted record in one step, per-ticket conditional update) and `Ticket.ListByHolderAndEvent`; contract tests including concurrent admits (`components/entity/ticket/**`)
- [ ] 2.3 `WalletPublicKey.Register` (one Active per user, in one step) and `GetActiveByUser`; contract tests
- [ ] 2.4 `ReceptionLink` operations: Create, Get, GetByToken (constant-time), ListByEvent, BindDevice (concurrent first binds), Revoke; contract tests (`components/entity/reception-link/**`)
- [ ] 2.5 `AdmissionRecord.Append` (Rejected only) and `GetAdmissionByTicket`; `Event.Get`; contract tests
- [ ] 2.6 `AdmissionCode.Decode` / `Verify` and the reception call proof (ECDSA P-256 verification, freshness 30 s before / 15 s after); unit tests for malformed, changed, expired, replaced-key and fast-clock input

## 3. Backend — usecases and boundaries

- [ ] 3.1 `WalletPublicKeyUseCase.Register` and `TicketUseCase.Admit` per `components/usecase/**`; unit tests for every scenario, including partial groups, someone else's ticket, voided tickets and a link revoked mid-scan
- [ ] 3.2 `ReceptionLinkUseCase.Issue` (refuses events without an open time), `Revoke`, `ListByEvent`, `Open`
- [ ] 3.3 Fan `RegisterWalletPublicKey` handler gate (`components/adapter/fan/api/rpc/ticket`)
- [ ] 3.4 Organizer reception-link handlers behind the organizer-console sign-in and `ResolveCaller` (`components/adapter/organizer/api/rpc/reception-link`)
- [ ] 3.5 Reception handlers without sign-in, with link token + call signature and throttling of unknown tokens (`components/adapter/organizer/api/rpc/reception`); CORS for the organizer web origin
- [ ] 3.6 `LotteryUseCase.ConfigureLotteryPhase` fails with FailedPrecondition for an event without an open time or a start time (`components/usecase/lottery-sales-phase/configure-lottery-phase`); unit test
- [ ] 3.7 `make check` passes

## 4. Frontend — fan tickets screen (fan web app)

- [ ] 4.1 Tickets screen per `components/infrastructure/fan/web/route/tickets`: grouped by event, covered-ticket face, 未入場 / 入場済み / 無効, last loaded list viewable offline
- [ ] 4.2 Key pair: WebCrypto ECDSA P-256 `extractable: false`, kept in IndexedDB; register the public key on an online visit when none is registered or it was replaced; "needs a connection once" and "now shown from this device only" messages
- [ ] 4.3 Entry QR: one code for the ticked tickets (up to 10) with the head count; signed on the device every 15 s without a connection; Base45 payload; SVG via `@paulmillr/qr`; never shows a code older than 15 s
- [ ] 4.4 Screen Wake Lock while the code is shown: request in try/catch, re-acquire on `visibilitychange`, release on close; suggest raising brightness
- [ ] 4.5 Verify on the current and previous major Safari for iOS and Chrome for Android; `make check` passes

## 5. Frontend — organizer web app

- [ ] 5.1 Reception-links screen per `components/infrastructure/organizer/web/route/reception-links`, reached from the event in the console: issue with suggested names, copy / share URL, state, revoke and revoke-and-reissue with confirmation, reception window shown, no-open-time and draft messages
- [ ] 5.2 Reception screen per `components/infrastructure/organizer/web/route/reception`: route exempt from the console sign-in, used in a browser tab (not installed); device key pair created on first open and every call signed; outside-window, revoked and other-device messages
- [ ] 5.3 Scanning: rear camera via `getUserMedia` (`facingMode: { ideal: 'environment' }`) requested on tap; `BarcodeDetector` when it supports QR, else `@paulmillr/qr` in a Web Worker; OK + head count / NG + reason and next step, no personal data; fail closed when unreachable
- [ ] 5.4 Lottery phase editor: message and link to the concert editor when the event has no open or start time, no save (`components/infrastructure/organizer/web/route/lottery-phase-editor`)
- [ ] 5.5 Verify on the current and previous major Safari for iOS and Chrome for Android; `make check` passes

## 6. Anti-scalp / product constraints

- [ ] 6.1 No first-party distribution URL / transferable per-companion code (verify none exists)
- [ ] 6.2 A stale, changed or replaced-key code is rejected before any ticket is touched, and each ticket admits at most once
- [ ] 6.3 No personal data leaves the reception boundary: Admit responses carry no name, phone or account (test asserts the response shape)
- [ ] 6.4 The private keys are created non-extractable and never sent: no request carries private key material (test on both screens); CSP reviewed for both apps
- [ ] 6.5 Scope check: MVP anti-scalp = account passkey + device-bound codes with online atomic admission + ⑤-captured 本人確認 identity; do NOT claim bulk-scalp resistance (that is `identity-ekyc-jpki`)

## 7. Release and verification

- [ ] 7.1 Cross-repo release order: spec → BSR → backend → frontend (fan and organizer apps)
- [ ] 7.2 Reception runbook (ops doc, not code): issue one link per device; staff open it in the browser before the window; a lost or replaced device → revoke and reissue; what each NG reason means and what to tell the fan; fans open their tickets screen online once before the day; rehearse on a separate test event. Venue checks and the rehearsal itself are tracked in liverty-music/specification#1076, not here
- [ ] 7.3 End-to-end on production with a test event (`stories/enter-a-venue-with-a-ticket`): group of 3 admitted with one scan; code shown in airplane mode admitted; same code at two links admits once; screenshot after 30 seconds refused; code from a replaced phone refused; forwarded link refused on a second device; revoked link refused and the reissued link works; refunded ticket refused; reception screen shows no name; reception server unreachable fails closed
- [ ] 7.4 Sync delta specs to main specs (including the `Ticket` and fan ticket RPC Purpose updates listed in proposal.md) and archive the change

## 8. Future (out of MVP scope — do not implement now)

- [ ] 8.1 **OS Wallet convenience passes** (Apple/Google) — caveats: OS-shareable (weaker anti-scalp), iOS static (no self-serve rotating barcode), 個情法 §28 越境移転 consent to Apple/Google (US), must render the covered-ticket face on the pass
- [ ] 8.2 Per-event **顔認証 / ID high-assurance mode** at entry (closes the 1:1 device-transfer hole; roadmap `face-auth-entry`; face templates = 特定生体情報 under 令和8年改正)
- [ ] 8.3 **NFC tap-to-enter** (Apple VAS / Google Smart Tap) — certified gate reader hardware + platform programs; not a web app
- [ ] 8.4 **Offline reception** — verify AdmissionCodes locally with downloaded public keys and reconcile admissions on reconnect, if a venue outgrows online-first
- [ ] 8.5 **Zitadel `reception` role** for standing reception teams (`organizer-rbac-subowners`), coexisting with reception links
- [ ] 8.6 **Ticket types** on the reception screen (一般 / VIP …) once a sale defines them
