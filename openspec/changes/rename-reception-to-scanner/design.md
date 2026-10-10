## Context

See proposal.md - Why. State verified on 2026-10-10 (specification `d272bcd7`, backend `origin/main` `023c33a` = v1.70.0, frontend `origin/main` `efe5127`, cloud-provisioning `origin/main`):

- **Specs.** Every reception capability is added by `ticket-wallet-and-checkin`, which is at 42/53 tasks. Its remaining tasks are the real-device checks (4.6, 5.6), the production end-to-end run (7.3) and the archive (7.4); see `changes/ticket-wallet-and-checkin/tasks.md:51,62,76-77`. None of these capabilities is in `openspec/specs/` yet. The only main spec that names reception is `components/entity/organizer/delete` ("the reception links of those Events", `openspec/specs/components/entity/organizer/delete/spec.md:15`). `isolate-venue-reception` sets `skip_specs: true` and changed only the hosting.
- **Proto.** The entity file is `entity/v1/reception_link.proto` (`ReceptionLink`, `ReceptionLinkId`, `ReceptionLinkNumber`, `ReceptionLinkToken`, `ReceptionLinkStatus`, `ReceptionWindow`). `admission.proto` and `rejected_scan.proto` reference it through `reception_link_id`. The services are `rpc/organizer/reception_link/v1` (`Issue`, `List`, `Revoke`) and `rpc/organizer/reception/v1` (`Open`, `Admit`). The call signature's first line is `liverty-music.reception.v1`, followed by the Connect procedure path (`rpc/organizer/reception/v1/reception_service.proto:30-31`).
- **Database** (`k8s/atlas/base/migrations/20261008000000_add_ticket_wallet_and_reception.sql`, released in backend v1.68.1):
  - `reception_links` with `token` and `token_hash` (lines 29-61);
  - `admissions.reception_link_id` (line 69, index line 79);
  - `rejected_scans.reception_link_id` (line 90, index line 110).

  `20261009120000_grant_reception_api_and_restrict_organizer_console_api.sql` grants the `reception-api` IAM user columns of `reception_links` by name. `migration_grants_integration_test.go:75,90` pins those grants by table name.
- **Backend names.**
  - `entity/reception_link.go` holds `ReceptionLink`, `ReceptionLinkID`, `ReceptionLinkStatus`, `ReceptionCall`, `ReceptionWindow`, `ReceptionWindowOf` and `ReceptionLinkRepository`.
  - `usecase/reception_link_uc.go` holds `ReceptionLinkUseCase` (`Issue`, `ListByEvent`, `Revoke`, `Open`).
  - The handlers are `adapter/rpc/organizer_reception_link_handler.go` and `adapter/rpc/reception_handler.go`, with `adapter/rpc/mapper/reception.go`.
  - The repositories are `rdb/reception_link_repo.go` and `rdb/admission_repo.go:25-27`.
  - Organizer deletion is `rdb/organizer_repo.go:336-337,415`.
  - The reception server is `app.ReceptionServer`, started in `cmd/api/main.go:92-95`. Its public procedures are listed by `auth/public_procedures.go:34-37`.
- **Frontend names.**
  - Console: `organizer/reception-links/*` and `organizer/services/reception-link-client.ts`.
  - Scanner app (its own build since `isolate-venue-reception`): `reception/*`, `vite.reception.config.ts`, `Dockerfile.reception` and `Caddyfile.reception`.
  - Shared: `shared/lib/reception/jst-format.ts` (`receptionLinkLabel`).
  - Fan: `src/routes/tickets/entry-code-session.ts` (`EntryCodeSession`, `EntryCodeSigner`).

  Both venue screens are Japanese only. They are hard-coded with `lang="ja"` and use no i18n (`reception/reception-route/reception-route.html:3`, `organizer/reception-links/reception-links-route.html:1`), so they have no English copy to rename. The fan's English copy says "entry QR code" (`src/locales/en/translation.json:391-409`).
- **Name clashes.** The scanner app already has a `QrScanner` class: the camera frame loop that decodes QR codes (`reception/reception-route/qr-scanner.ts`, used at `reception-route.ts:11,83`). The device keys are stored in the IndexedDB database `liverty-reception` (`reception/services/reception-key-store.ts:18`).
- **Hosting names in other changes.** `harden-backend-process-lifecycle` names the `reception-api` Deployment (`changes/harden-backend-process-lifecycle/tasks.md:37`). cloud-provisioning mentions `ReceptionService` only in comments (`k8s/namespaces/backend/base/reception-api/kustomization.yaml:4`, `k8s/namespaces/backend/base/fan-api/configmap.env:28`, `src/gcp/components/kubernetes.ts:361`, `src/gcp/components/network.ts:389`).

## Goals / Non-Goals

**Goals:**
- One vocabulary from spec to proto, DB and code: `Scanner`, link token, admission window, `scanner_id`, `AdmissionCode`.
- No behavior change and no data loss. Scanners that are already bound keep working across the release.
- `openspec validate --strict` passes for this change now, and it can archive once `ticket-wallet-and-checkin` is archived.

**Non-Goals:**
- Renaming hosts, workloads, cloud identities or the Japanese UI copy (D5).
- Adding English copy or i18n to the two venue screens.
- Moving the admission window from the Scanner to the Event entity. The window stays where `ticket-wallet-and-checkin` put it, under its new name.
- Renaming `RejectedScanReason` values or any wire format other than the call signature's first line and the procedure paths.

## Decisions

### D1 — `Scanner` is the right; the link token is its field

`ReceptionLink` becomes `Scanner`. Its `token` becomes `link token` (`link_token` in proto and DB, `ScannerLinkToken` as the wrapper message). The other attributes keep their meaning. The operations keep their names, except `GetByToken`, which becomes `GetByLinkToken` because the Scanner no longer is a link.

- **Proto names:**
  - `ReceptionLinkId` → `ScannerId`, `ReceptionLinkNumber` → `ScannerNumber`, `ReceptionLinkToken` → `ScannerLinkToken`, `ReceptionLinkStatus` → `ScannerStatus` (`SCANNER_STATUS_UNUSED` = 1, `IN_USE` = 2, `REVOKED` = 3, the same numbers);
  - `ReceptionLink.token` → `Scanner.link_token`, at the same field number;
  - `bind_time` and `revoke_time` stay.
- **Go names:**
  - `entity/scanner.go`: `Scanner`, `ScannerID`, `ScannerStatus`, `ScannerCall` (was `ReceptionCall`), `AdmissionWindow`, `AdmissionWindowOf`, `ScannerRepository` and `HashScannerLinkToken`;
  - `usecase/scanner_uc.go` with `ScannerUseCase.Create`, `ListByEvent`, `Revoke` and `Open`.
- **Rejected — keep `ReceptionLink` and only fix the English copy**: the name is the problem. It is in proto, Go, TS and SQL, and a reader of any of them meets "reception".
- **Rejected — `CheckIn`**: a person checks in, and that is what an `Admission` records. A second name for the same act would make two entities hard to tell apart.

### D2 — The reception window becomes the admission window

`ReceptionWindow` → `AdmissionWindow` (proto, Go `AdmissionWindow` / `AdmissionWindowOf`, TS `admission-window.ts`). The rule (3 hours before doors or start, until 04:00 Japan time the next day) and its place as a Scanner requirement do not change.

- **Why "admission"**: the window bounds when Admissions can be made. It is the same for every Scanner of the event.
- **Not done — moving it onto `Event`**: it would be a cleaner home, but it changes the spec structure, and this change is limited to the rename.

### D3 — Admissions and rejected scans name the Scanner

`Admission.reception_link_id` and `RejectedScan.reception_link_id` → `scanner_id`. `RejectedTicket.earlier_reception_link_number` → `earlier_scanner_number`. The field numbers stay. The Go and DB names follow (D8).

### D4 — Two services named after the entity, one per caller

| Caller | Service | Methods | Served by |
|---|---|---|---|
| organizer operator, signed in | `rpc.organizer.scanner.v1.ScannerService` | `Create`, `List`, `Revoke` | organizer server (`organizer-console-api`) |
| scanner device, link token + signature | `rpc.scanner.v1.ScannerService` | `Open`, `Admit` | reception server (`reception-api`) |

- **Console methods:**
  - `Create(CreateRequest{event_id}) → CreateResponse{scanner}` replaces `Issue`. It is the standard create method on the resource's own service (specification `CLAUDE.md:148`).
  - `List(ListRequest{event_id}) → ListResponse{scanners}` is unchanged.
  - `Revoke(RevokeRequest{scanner_id}) → RevokeResponse{scanner}` stays a custom method.
- **Device methods:** `Open` and `Admit` are custom methods.
  - `OpenRequest.link_token` and `AdmitRequest.link_token` keep their names, with the type `ScannerLinkToken`.
  - `OpenResponse.reception_link` → `scanner`, and `reception_window` → `admission_window`.
- **Why two packages:**
  - The two callers have different authentication. The organizer server must have no public procedure (`isolate-venue-reception` D2, `changes/isolate-venue-reception/design.md:44-46`).
  - The reception server mounts exactly one package (D1 there, line 39).
  - Splitting one resource's service by caller is the existing pattern: `rpc.concert.v1`, `rpc.organizer.concert.v1` and `rpc.admin.concert.v1` each have a `ConcertService`.
- **Why the device package has no audience prefix:** the scanner device acts on its own Scanner. This is like a fan's self-scoped calls (`rpc.wallet_public_key.v1`), not like an operator acting for an Organizer. The package comment states that only the reception server serves it. A top-level package has meant "fan" so far; this is the first that is not, and the comment says so.
- **Rejected — one `rpc.organizer.scanner.v1.ScannerService` with all five methods, each server implementing its part**: both apps would get stubs for methods their server answers with Unimplemented. One service would also document two authentication models.
- **Rejected — a new audience prefix (`rpc.venue.scanner.v1`) or the hosting name (`rpc.reception.scanner.v1`)**: the spec tree has only the audiences fan, admin and organizer (`scripts/check-spec-layout.py:16`). "reception" is the word this change removes from code vocabulary.
- **Spec paths:**
  - The console gate is `components/adapter/organizer/api/rpc/scanner`.
  - The device gate is `components/adapter/organizer/api/rpc/scanner-device`. The spec tree requires an audience, and `ticket-wallet-and-checkin` already placed the device gate under organizer, since venue staff act for the Organizer.
  - The proto package and the spec path differ for the device gate only. This mapping is recorded here.
- **Call signature.** The first line becomes `liverty-music.scanner.v1`. The second line is the new procedure path (`/liverty_music.rpc.scanner.v1.ScannerService/Open` and `/Admit`). The rest of the input is unchanged.
  - The procedure path changes anyway with the service, so changing the first line costs nothing more.
  - Backend and scanner app ship it together. A device still running the old app calls a procedure that no longer exists, so it admits no one until it reloads.

### D5 — What keeps the word "reception"

Unchanged:
- the hosts `reception.liverty-music.app` and `api.reception.liverty-music.app`;
- the `reception-api` and `reception-web` workloads, their GSA, Cloud SQL IAM user and Kubernetes resources;
- `RECEPTION_SERVER_PORT` and `RECEPTION_CORS_ALLOWED_ORIGINS`;
- the backend's reception server (`app.ReceptionServer`, `ReceptionPublicProcedures()`);
- the scanner app's build entry (`reception.html`, `vite.reception.config.ts`, `Dockerfile.reception`, `Caddyfile.reception`) and its directory `reception/`;
- the guide at `/guide.html`;
- the IndexedDB name `liverty-reception`;
- the Japanese copy 受付, 受付リンク and 受付N.

These names say where the scanner app is hosted, or what staff read in Japanese. Inside that app, the domain types, clients and components are renamed (Scanner, admission window, AdmissionCode).

- **Why keep the hosts and workloads:**
  - Renaming the IAM user needs a new Pulumi identity, a new grant migration and new k8s overlays.
  - Renaming the host loses the camera permission and the device keys, which browsers store per origin (`ticket-wallet-and-checkin` design, "Reception is hosted apart", line 151).
  - `harden-backend-process-lifecycle` already plans work on `reception-api`.
  - None of these names reaches the ubiquitous language: specs do not name hosts.
- **Why keep the IndexedDB name**: renaming it would orphan the key of every bound Scanner, and the next Open would report OtherDevice.
- **Why keep the Japanese copy**: 受付 is the natural Japanese word for the door desk. The English problem does not exist in Japanese.
- **English copy**: there is none on the two venue screens (Context). If English is added later, it uses "scanner" for the device and "check-in" for the act (for example "Check-in starts at 15:00").

### D6 — `AdmissionCode` keeps its name; `EntryCode*` code names go

`AdmissionCode` is the signed statement. The QR code is its current rendering; OS wallet passes and NFC are possible future renderings (`ticket-wallet-and-checkin` tasks 8.1, 8.3). The fan app's `EntryCodeSession` and `EntryCodeSigner` become `AdmissionCodeSession` and `AdmissionCodeSigner` (`src/routes/tickets/admission-code-session.ts`). The comments in `tickets-route.ts` and `wallet-view.ts` that say "entry code" are updated too.

- **UI text is unchanged**: 入場用QRコード, "entry QR code", and the staff reason 有効な入場QRコードではありません (`reception/reception-route/verdict.ts`, FORGED copy). The scanner screen spec quotes that reason as "not a valid entry QR code". The `ticket-wallet-and-checkin` spec says "not a valid entry code", which does not match the shipped copy.
- **Exception — the usecase scenario name "Not an entry code"**: it is kept. Archive refuses a MODIFIED block that drops a scenario name (openspec `core/specs-apply.js:388-389`).

### D7 — `QrScanner` becomes `QrCodeReader`

With `Scanner` as an entity, the scanner app's camera decoding loop `QrScanner` would read as the entity. It becomes `QrCodeReader` (`reception/scanner-route/qr-code-reader.ts`). The decoder interface `qr-decoder.ts` and the worker keep their names.

### D8 — One in-place rename migration

One Atlas migration, `<timestamp>_rename_reception_links_to_scanners.sql`, following the precedent `20260310000000_rename_passion_level_to_hype.sql`:

- `ALTER TABLE reception_links RENAME TO scanners`;
- columns `token` → `link_token` and `token_hash` → `link_token_hash`;
- `admissions.reception_link_id` and `rejected_scans.reception_link_id` → `scanner_id`;
- the constraints `chk_reception_links_*` → `chk_scanners_*` (including `chk_scanners_link_token_only_unused` and `chk_scanners_link_token_hash_len`), and `uq_reception_links_event_number` / `uq_reception_links_token_hash` → `uq_scanners_event_number` / `uq_scanners_link_token_hash`;
- the foreign key constraints `admissions_reception_link_id_fkey` and `rejected_scans_reception_link_id_fkey` → `*_scanner_id_fkey`;
- the indexes `idx_admissions_reception_link_id` and `idx_rejected_scans_reception_link_id` → `*_scanner_id`;
- every `COMMENT ON` of the renamed objects is rewritten.

Further details:
- **Grants.** PostgreSQL keeps table and column privileges on a rename, because they are stored on the object and not on its name. So the `reception-api` and `organizer-console-api` grants carry over, and no grant migration is needed. This is inferred from how privileges are stored. The grants integration test verifies it once its expected sets name `scanners` and `link_token` (task 3.3).
- **History stays.** Earlier migrations are left as they are (Atlas checksums). Any later grant loop names `scanners`.
- **Code with SQL text:**
  - `schema.sql` (the desired state for `make lint-schema`);
  - the repositories (`rdb/scanner_repo.go`, `admission_repo.go`, `rejected_scan_repo.go`, `ticket_repo.go` Admit);
  - the deletion query in `organizer_repo.go`, now `deleteOrganizerScannersQuery`;
  - the integration tests.
- **Data:**
  - Rows are untouched, so issued link URLs (`https://reception.liverty-music.app/#<link token>`) and bound devices keep working.
  - Production has only test data (`CLAUDE.md`, current operating state). Task 3.1 reads the row counts read-only before and after.
- **Rejected — create new tables and copy the rows**: it needs more SQL, re-granting and a copy step, for no benefit when a rename keeps everything.

### D9 — Specs: ADDED at the new paths plus REMOVED at the old, written against the post-`ticket-wallet-and-checkin` main specs

What `openspec` 1.13.2 does, verified on 2026-10-10 in a scratch copy of this store:
- `openspec validate --strict` accepts this change today, before `ticket-wallet-and-checkin` is archived.
  - A REMOVED delta against a missing main spec raises no finding.
  - A MODIFIED delta against a missing main spec raises only `[INFO] Archive would refuse this delta: … target spec does not exist`.
  - The validate output above shows both.
- Archive refuses MODIFIED and RENAMED against a missing spec, and ignores REMOVED for it with a warning (`core/specs-apply.js:258-265`). So this change can only archive after `ticket-wallet-and-checkin` has.
- With the main specs built from `ticket-wallet-and-checkin`'s deltas, this change validates, and `openspec show rename-reception-to-scanner --diff` applies every delta, including the RENAMED requirement of `usecase/ticket/admit`. A script also checked that each MODIFIED block keeps every scenario name of its base requirement.
- Removing the last requirement of a capability deletes its spec only when `.openspec.yaml` has `retire_capabilities: true` (`core/archive.js`, "retire the capability"). This change sets it. The same marker was used by `remove-event-postponement` and four other archived changes.

Choices:
- **ADDED + REMOVED, not a direct move of main specs.** The schema's direct move is for moving or splitting specs without changing them (`openspec/AGENTS.md`, "Capability files"). Here the Purpose, the subject and every requirement's wording change. This follows `unify-ticket-sales` D12.
- **Not editing `ticket-wallet-and-checkin`'s specs in place.** `isolate-venue-reception` amended that change for one URL line (its task 0.1). Doing that here would make that change's specs say Scanner while the shipped code says ReceptionLink. Its archive would then fail `check-scenario-coverage.py`, which looks for `@spec` annotations on the specs' paths in the implementing repositories, until this change's code merged. The two changes would be tied together.
- **Sequencing:**
  1. `ticket-wallet-and-checkin` archives first (task 0.1).
  2. This change's implementation PRs retag the `@spec` annotations from `reception-link` / `reception` paths to the new paths. They must merge only after step 1, or step 1's coverage check fails.
  3. `unify-ticket-sales` archives before this change, because `usecase/ticket/admit` here calls `Ticket.ListByUserAndEvent` (`unify-ticket-sales` design D9, `changes/unify-ticket-sales/design.md:121`).
- **The main spec Purposes** of `entity/admission`, `entity/rejected-scan` and the four modified capabilities are edited directly after step 1 (task 1.2), as the schema requires.

### Manual verification

The story and the real-iPhone scenario are run by hand on production with a test event (task 6.1), as in `ticket-wallet-and-checkin`:

@spec-manual stories/enter-a-venue-with-a-ticket "Group of three enters" -- production check with a test event, task 6.1
@spec-manual stories/enter-a-venue-with-a-ticket "No signal in the venue" -- production check, fan phone in airplane mode, task 6.1
@spec-manual stories/enter-a-venue-with-a-ticket "Same code at two entrances" -- production check with two Scanners, task 6.1
@spec-manual stories/enter-a-venue-with-a-ticket "Link forwarded" -- production check on a second phone, task 6.1
@spec-manual stories/enter-a-venue-with-a-ticket "Lost phone revoked" -- production check, revoke and reissue, task 6.1
@spec-manual components/infrastructure/organizer/web/route/scanner "Staff iPhone" -- scanned on a real iPhone in Safari (current iOS), task 6.1

### Assumptions to confirm

1. **The device-side package is `rpc.scanner.v1`** (D4). It is the first top-level package that is not fan-facing. The alternative is `rpc.organizer.scanner_device.v1.ScannerService`, which keeps the audience prefix but needs a non-entity package name.
2. **The device gate's spec path is `adapter/organizer/api/rpc/scanner-device`** (D4). "Scanner device" means the device a Scanner is bound to. It is not a new entity.
3. **The screens are `route/scanner` (staff) and `route/scanners` (console)**. They follow the plain singular/plural of the entity. If they read too alike, the console screen could be `route/event-scanners`.
4. **The reception guide is called "the staff guide" in specs.** Its page and Japanese title (受付の使い方) stay.
5. **The call signature's first line becomes `liverty-music.scanner.v1`** (D4) rather than staying `liverty-music.reception.v1`.

## Risks / Trade-offs

- [The migration runs before the new pods. Until the rollout finishes, old pods query `reception_links` and fail.] → There are no users. Deploy outside any event: the migration and the rollout take minutes, and a scan in that gap fails closed on the screen.
- [A console tab or scanner tab still running the old app calls procedures that no longer exist] → The console gets Unimplemented until reload. The scanner screen shows an error and admits no one until reload (it fails closed). The production check (task 6.1) reloads both.
- [`check-scenario-coverage.py` for `ticket-wallet-and-checkin` breaks if this change's retagged tests merge first] → Task 0.1 gates every implementation PR on that archive.
- [`unify-ticket-sales` slips behind this change] → Task 0.2 checks it. If it has not archived, `usecase/ticket/admit` here goes back to `Ticket.ListByHolderAndEvent` before this change archives.
- [One large breaking proto release] → Same as `ticket-wallet-and-checkin`'s naming cleanup: no outside clients, and `buf skip breaking`.

## Migration Plan

1. Gate: `ticket-wallet-and-checkin` and `unify-ticket-sales` are archived (tasks 0.1, 0.2).
2. Specification: main spec Purposes (task 1.2), then the proto PR and release (group 2).
3. Backend: the rename migration, code and server registration in one release (group 3). Atlas applies the migration before the rollout.
4. Frontend: the console, the scanner app and the fan app in one release (group 4).
5. cloud-provisioning: comments only (group 5).
6. Production checks (group 6), then sync and archive (task 6.3).

Rollback: the migration is a rename, and the reverse renames restore the old schema. With test data only, a failed release is fixed forward. If the old code must come back, a follow-up migration renames back first.
