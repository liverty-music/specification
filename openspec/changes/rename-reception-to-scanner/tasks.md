## 0. Dependency gate

- [ ] 0.1 Confirm `ticket-wallet-and-checkin` is archived, so `openspec/specs/` holds `components/entity/reception-link/**`, `components/usecase/reception-link/**`, the two reception adapters, the two reception routes, `entity/admission/get-by-ticket`, `entity/ticket/admit`, `usecase/ticket/admit` and `stories/enter-a-venue-with-a-ticket` (design D9). No implementation PR of this change merges before this, because the retagged `@spec` annotations would break that change's coverage check. Verify the paths exist on specification `main` and `openspec validate rename-reception-to-scanner --strict` reports no "Archive would refuse this delta" line
- [ ] 0.2 Confirm `unify-ticket-sales` is archived, so `components/entity/ticket/list-by-user-and-event` exists on main for `usecase/ticket/admit` (design D9). Verify the path exists, or else change the MODIFIED `usecase/ticket/admit` back to `Ticket.ListByHolderAndEvent` and the user wording back to holder, and verify validation still passes

## 1. Specification — main specs and plan

- [ ] 1.1 Open the plan PR from a worktree cut from origin/main, staging only `openspec/changes/rename-reception-to-scanner`. Paste the `openspec show rename-reception-to-scanner --diff` part into the body (`openspec/AGENTS.md`). Verify `openspec-checks.yml` passes and the PR merges
- [ ] 1.2 After 0.1, edit the main spec Purposes directly (proposal "(Purpose)" items):
  - `components/entity/admission`: the row "reception link | the ReceptionLink that scanned" becomes "scanner | the Scanner that scanned", the erDiagram becomes `Scanner ||--o{ Admission`, and the sentence "through which ReceptionLink" becomes "through which Scanner";
  - `components/entity/rejected-scan`: the same for its row, sentence and diagram;
  - `entity/admission/get-by-ticket`, `entity/ticket/admit`, `usecase/ticket/admit` and `stories/enter-a-venue-with-a-ticket`: "link" / "ReceptionLink" / "reception link" become "Scanner".

  Verify `openspec validate --specs` and `scripts/check-spec-layout.py` pass, and `grep -rn -i "reception" openspec/specs` finds only the capabilities this change removes

## 2. Proto (specification → BSR)

- [ ] 2.1 Replace `entity/v1/reception_link.proto` with `entity/v1/scanner.proto` from `components/entity/scanner` (design D1, D2):
  - `Scanner`, `ScannerId`, `ScannerNumber`, `ScannerLinkToken`, `ScannerStatus` (`SCANNER_STATUS_*`, same numbers) and `AdmissionWindow`;
  - `Scanner.link_token` at the field number of `token`;
  - comments say Scanner, link token and admission window.

  Update `public_key.proto` and `wallet_public_key.proto` comments (`Scanner.bound_public_key`). Verify `buf lint` and `buf format -d` pass
- [ ] 2.2 `admission.proto` and `rejected_scan.proto`: `reception_link_id` → `scanner_id` (type `ScannerId`, same field numbers), and comments say Scanner (design D3). Verify `buf lint` passes
- [ ] 2.3 Replace `rpc/organizer/reception_link/v1` with `rpc/organizer/scanner/v1/scanner_service.proto` (design D4):
  - `ScannerService.Create(CreateRequest{event_id}) → CreateResponse{scanner}`;
  - `List(ListRequest{event_id}) → ListResponse{scanners}`;
  - `Revoke(RevokeRequest{scanner_id}) → RevokeResponse{scanner}`;
  - doc comments and error lists carried over from the old service, worded per `components/adapter/organizer/api/rpc/scanner`.

  Verify `buf lint` passes
- [ ] 2.4 Replace `rpc/organizer/reception/v1` with `rpc/scanner/v1/scanner_service.proto` (design D4):
  - `ScannerService.Open` and `Admit`, with the same request fields and `link_token` typed `ScannerLinkToken`;
  - `OpenResponse.scanner` and `admission_window`;
  - `RejectedTicket.earlier_scanner_number`;
  - the call signature doc with first line `liverty-music.scanner.v1` and the procedure `/liverty_music.rpc.scanner.v1.ScannerService/Admit`;
  - a package comment saying only the reception server serves it.

  Verify `buf lint` passes and `grep -rn -i "reception" proto/` finds only the hosting mention in that package comment and the admin organizer deletion comment, reworded to "scanner records"
- [ ] 2.5 Open the proto PR from a worktree with the `buf skip breaking` label, merge, and cut a Release; verify `buf-release.yml` succeeds and BSR has the new version

## 3. Backend (after 0.1 and 2.5)

- [ ] 3.1 Read the production row counts of `reception_links`, `admissions` and `rejected_scans` through the read-only db-proxy runbook and record them in design.md "Migration Plan"; verify that only test data exists, or stop and ask the user
- [ ] 3.2 Rename migration (design D8):
  - tables, columns, constraints, foreign keys and indexes renamed, and the comments rewritten;
  - `schema.sql` updated to the same state;
  - registered in the Atlas kustomization and `atlas.sum`.

  Verify the migration applies on a fresh database after every earlier migration and `make lint-schema` passes
- [ ] 3.3 Grants integration test: the expected sets name `scanners` (with `link_token` among the organizer and reception update columns) and keep the same privileges. Verify `migration_grants_integration_test.go` passes with every migration applied, which shows the grants survived the rename (design D8)
- [ ] 3.4 Entity: `entity/reception_link.go` → `entity/scanner.go` (`Scanner`, `ScannerID`, `ScannerStatus`, `ScannerCall`, `AdmissionWindow`, `AdmissionWindowOf`, `HashScannerLinkToken`, `ScannerRepository`, design D1, D2). `Admission.ScannerID`, `RejectedScan.ScannerID`. Mocks regenerated. Verify the unit tests are retagged `@spec components/entity/scanner` and pass for: First scanner, After a revoked scanner, New scanner, Scanner in use, Revoked scanner, Call from the bound device, Call from another device, Replayed call, Usual evening show, No open time, Before the window, Window closed, No start time
- [ ] 3.5 Repositories: `rdb/reception_link_repo.go` → `rdb/scanner_repo.go` with `GetByLinkToken`. Rename the SQL in `admission_repo.go`, `rejected_scan_repo.go`, `ticket_repo.go` (Admit) and `organizer_repo.go` (`deleteOrganizerScannersQuery`). Verify the contract tests, retagged to the new paths, pass:
  - `entity/scanner/create`: New scanner stored, Two scanners created at once
  - `entity/scanner/get`: Existing scanner, Unknown scanner
  - `entity/scanner/get-by-link-token`: Known link token, Unknown link token
  - `entity/scanner/list-by-event`: Event with scanners, Event without scanners
  - `entity/scanner/bind-device`: First device, Same device again, Another device, Two devices at once, Revoked scanner
  - `entity/scanner/revoke`: Scanner in use, Already revoked, Unknown scanner
  - `entity/admission/get-by-ticket`: Admitted ticket, Ticket not admitted
  - `entity/ticket/admit`: First admission, Second admission, Concurrent admissions, Voided ticket, Unknown ticket
  - `entity/organizer/delete`: Organizer with a published Series, Refunded purchase
- [ ] 3.6 Usecases: `usecase/reception_link_uc.go` → `usecase/scanner_uc.go` (`ScannerUseCase.Create`, `ListByEvent`, `Revoke`, `Open`). `TicketUseCase.Admit` takes the Scanner. Verify the unit tests, retagged to the new paths, pass:
  - `usecase/scanner/create`: Another organizer's event, Draft event, Event without a start time, Scanner created the day before
  - `usecase/scanner/list-by-event`: Scanners of an event, Another organizer's event
  - `usecase/scanner/open`: Staff open the link for the first time, Signature from another key, Link forwarded to another device, Revoked scanner, Unknown link token, Opened the day before, Opened during the window
  - `usecase/scanner/revoke`: Another organizer's scanner, Device lost during the show, Revoked twice
  - `usecase/ticket/admit`: Revoked link, Call from another device, Revoked during a group scan, After the window, Screenshot shown later, Code from a replaced phone, Not an entry code, Someone else's ticket, Ticket of another event in the code, Ticket for another event, Group of three admitted, Same code at two entrances, Already used earlier, Refunded ticket, Admission recorded, Rejection recorded, Result of a group scan
- [ ] 3.7 Handlers and servers (design D4, D5):
  - `organizer_reception_link_handler.go` → `organizer_scanner_handler.go` on the organizer server;
  - `reception_handler.go` → `scanner_handler.go` on the reception server, with `ReceptionPublicProcedures()` listing the new `Open` and `Admit` procedures;
  - the call signature check uses `liverty-music.scanner.v1`;
  - `mapper/reception.go` → `mapper/scanner.go`;
  - DI and the unknown-token interceptor comments updated.

  Verify the handler tests, retagged to the new paths, pass for `adapter/organizer/api/rpc/scanner` (Operator creates a scanner, Not signed in, Deactivated Organizer, Create without an event) and `adapter/organizer/api/rpc/scanner-device` (Staff device without an account, Missing signature, Token guessing). Verify the reception server test shows the old procedures are not served
- [ ] 3.8 Run `reception_admit_integration_test.go` against the renamed tables, connected as the `reception-api` role; verify it passes. Run `make check`; verify `grep -rn -i "reception_link\|ReceptionLink\|ReceptionWindow" internal cmd` finds nothing
- [ ] 3.9 Upgrade the generated package to the 2.5 release, open the backend PR citing the change, and merge. Verify the AtlasMigration applies in production and the `organizer-console-api` and `reception-api` rollouts are healthy (read-only checks)

## 4. Frontend (after 0.1 and 2.5)

- [ ] 4.1 Console screen (`components/infrastructure/organizer/web/route/scanners`):
  - `organizer/reception-links/*` → `organizer/scanners/*`;
  - `reception-link-client.ts` → `scanner-client.ts` calling `rpc.organizer.scanner.v1.ScannerService` (`Create`, `List`, `Revoke`);
  - `reception-window.ts` → `admission-window.ts`;
  - the route path and the console's link to it renamed;
  - the Japanese copy unchanged.

  Verify the component tests, retagged, pass: Create two scanners, Link opened by staff, Staff changed phones, Unpublished event, Event without a start time
- [ ] 4.2 Scanner app (`components/infrastructure/organizer/web/route/scanner`, design D5, D7):
  - inside `reception/`, `reception-route/*` → `scanner-route/*`;
  - `reception-client.ts`, `reception-transport.ts` and `reception-key-store.ts` → `scanner-*` names, calling `rpc.scanner.v1.ScannerService`;
  - `call-signature.ts` uses `liverty-music.scanner.v1` and the new procedure paths;
  - `QrScanner` → `QrCodeReader`;
  - `shared/lib/reception/` → `shared/lib/scanner/` (`scannerLabel`);
  - unchanged: the IndexedDB name `liverty-reception`, the build entry, the Dockerfile, the Caddyfile and the Japanese copy.

  Verify the tests, retagged, pass: Staff open the link, Forwarded link, Revoked scanner, Phone clock far off, Opened the day before, Admission over, Start scanning, Group admitted, Ticket used earlier, Code still in view after OK, Screenshot, Network down, Staff open the guide. Verify `verify:reception-bundle` and the dependency-cruiser rules still pass after their paths are updated
- [ ] 4.3 Fan tickets screen (design D6): `entry-code-session.ts` → `admission-code-session.ts` (`AdmissionCodeSession`, `AdmissionCodeSigner`), its test moved and renamed, and the "entry code" comments in `tickets-route.ts` and `wallet-view.ts` updated. UI text unchanged. Verify the session tests pass and `grep -rn "EntryCode" src test` finds nothing
- [ ] 4.4 Upgrade the generated clients to the 2.5 release and run `make check`. Verify `grep -rn -E "ReceptionLink|ReceptionWindow|reception_link|reception\.v1" organizer reception shared src test` finds nothing. Open the frontend PR citing the change, merge, and verify the `organizer-console-web` and `reception-web` production rollouts are healthy

## 5. cloud-provisioning

- [ ] 5.1 Update the comments that name `ReceptionService`: `k8s/namespaces/backend/base/reception-api/kustomization.yaml`, the `fan-api` configmap comments in base and overlays, `src/gcp/components/kubernetes.ts` and `src/gcp/components/network.ts`. They now name `rpc.scanner.v1.ScannerService`. No resource changes. Verify `kubectl kustomize` renders the same dev and prod objects as before (diff shows comments only, or no diff) and `make lint` passes

## 6. Production verification and archive

- [ ] 6.1 On production with a test event, check every scenario of `stories/enter-a-venue-with-a-ticket` and the scanner screen on a real iPhone (design "Manual verification"):
  - create two Scanners in the console;
  - open `受付1` at `reception.liverty-music.app` on an iPhone in Safari and bind it;
  - admit a group of 3 with one scan, from a fan phone in airplane mode;
  - the same code at `受付1` and `受付2` admits once;
  - the link forwarded to another phone is refused;
  - revoke and reissue `受付1`, then confirm the old phone is refused and the reissued Scanner works.

  Verify read-only that `admissions.scanner_id` and `rejected_scans.scanner_id` name the Scanners used
- [ ] 6.2 Verify read-only that `\dp scanners` shows the same grants as `reception_links` had (the `reception-api` bind columns and the `organizer-console-api` issue / revoke columns) and that a call to the old procedure paths fails
- [ ] 6.3 Run `/verify-before-archive` and archive the change (sync deletes the retired `reception-link` and `reception` specs, design D9); verify `openspec validate --specs` passes and `python3 scripts/check-scenario-coverage.py rename-reception-to-scanner` reports every scenario covered
