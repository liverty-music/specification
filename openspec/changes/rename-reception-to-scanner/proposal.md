## Why

`ticket-wallet-and-checkin` named the venue door's vocabulary after the Japanese word 受付. In English, "reception" is a front desk, so `ReceptionLink`, `ReceptionService` and "reception window" read as a hotel lobby, not as a device that admits fans. The thing the Organizer hands out is one device's right to admit fans to one event; the link is only how that right travels. Scanner apps are the industry's own term, and the name connects to `RejectedScan` and to "scan". "Check-in" was rejected: a person checks in, and that act is already the `Admission`. The vocabulary shipped in backend v1.68.1 and has never been used at a live event, so renaming now costs one rename migration and no client migration.

## What Changes

- **BREAKING** The entity `ReceptionLink` becomes `Scanner`: one device's right to admit fans to one event. Its link token becomes a field of the Scanner (`link token`). The other attributes stay the same: event, number (shown as 受付N), bound public key, status Unused / InUse / Revoked, bound time and revoked time.
- **BREAKING** The reception window becomes the **admission window**. The rule does not change: it opens 3 hours before the open time (or before the start time when the event has no open time) and closes at 04:00 Japan time on the day after the event date.
- **BREAKING** An `Admission` and a `RejectedScan` name the Scanner that scanned, not "the reception link" (`scanner_id` in proto and DB).
- **BREAKING** RPC services are named after the entity, one service per caller:
  - `rpc.organizer.scanner.v1.ScannerService` with `Create`, `List` and the custom method `Revoke` replaces `rpc.organizer.reception_link.v1.ReceptionLinkService` (`Issue`, `List`, `Revoke`). The operator console calls it on the organizer API.
  - `rpc.scanner.v1.ScannerService` with the custom methods `Open` and `Admit` replaces `rpc.organizer.reception.v1.ReceptionService`. The scanner device calls it on the `reception-api` workload that `isolate-venue-reception` set up.
- `AdmissionCode` keeps its name. It is the signed statement; the QR code is only how it is shown today. The fan app's `EntryCode*` code names become `AdmissionCode*`. The words the fan and staff see ("入場用QRコード", "entry QR code") do not change.
- Unchanged:
  - the hosting names `reception.liverty-music.app`, `api.reception.liverty-music.app` and the `reception-api` and `reception-web` workloads;
  - the Japanese UI copy (受付, 受付リンク, 受付1);
  - the reception guide page.

  Only the code and spec vocabulary is renamed.
- No behavior changes. Every rule, threshold, error and scenario of the renamed specs keeps its meaning. Scanners issued before the release keep working, because the migration renames tables and columns in place.

## Capabilities

### New Capabilities

Each replaces the `reception-link` / `reception` capability of `ticket-wallet-and-checkin` at the same layer, with its rules unchanged:

- `components/entity/scanner`: one device's right to admit fans to one event; numbering, lifecycle, device proof and the admission window
- `components/entity/scanner/create`, `get`, `get-by-link-token`, `list-by-event`, `bind-device`, `revoke`: the operations of the former `ReceptionLink` (`GetByToken` becomes `GetByLinkToken`)
- `components/usecase/scanner/create`, `list-by-event`, `open`, `revoke`: the former `ReceptionLinkUseCase` methods (`Issue` becomes `Create`)
- `components/adapter/organizer/api/rpc/scanner`: the operator gate for creating, listing and revoking Scanners
- `components/adapter/organizer/api/rpc/scanner-device`: the gate a scanner device calls, identified by the link token and the device's signature, with no sign-in
- `components/infrastructure/organizer/web/route/scanner`: the screen venue staff scan with (formerly the reception screen)
- `components/infrastructure/organizer/web/route/scanners`: the console screen listing an event's Scanners (formerly the reception-links screen)

### Modified Capabilities

These capabilities are added by `ticket-wallet-and-checkin`. They are written against the main specs as they will be once that change is archived; see design.md "Sequencing".

- `components/entity/admission/get-by-ticket`: returns the number of the Admission's Scanner.
- `components/entity/ticket/admit`: takes a Scanner instead of a reception link.
- `components/usecase/ticket/admit`: goes through a Scanner and its admission window, and reads the user's tickets with `Ticket.ListByUserAndEvent` (`unify-ticket-sales`).
- `stories/enter-a-venue-with-a-ticket`: venue staff admit through a Scanner.
- `components/entity/admission` (Purpose): the "reception link" row and diagram become "scanner".
- `components/entity/rejected-scan` (Purpose): the "reception link" row and diagram become "scanner".
- Purpose sentences of `components/entity/admission/get-by-ticket`, `components/entity/ticket/admit`, `components/usecase/ticket/admit` and `stories/enter-a-venue-with-a-ticket` (Purpose): "reception link" becomes "Scanner".

Already in the main specs:

- `components/entity/organizer/delete`: deleting an Organizer removes the Scanners of its events.

Entity operations this change relies on and does not change: `Event.Get`, `Event.GetOrganizerID`, `Event.IsEventPublished`, `OrganizerUseCase.ResolveCaller`, `WalletPublicKey.GetByUser`, `AdmissionCode.Decode`, `AdmissionCode.Verify`, `RejectedScan.Append`, and `Ticket.ListByUserAndEvent` (from `unify-ticket-sales`).

### Removed Capabilities

Written as REMOVED deltas, each moved to the capability named above:

- `components/entity/reception-link` and its operations `create`, `get`, `get-by-token`, `list-by-event`, `bind-device`, `revoke`
- `components/usecase/reception-link/issue`, `list-by-event`, `open`, `revoke`
- `components/adapter/organizer/api/rpc/reception-link`, `components/adapter/organizer/api/rpc/reception`
- `components/infrastructure/organizer/web/route/reception`, `components/infrastructure/organizer/web/route/reception-links`

## Impact

- **specification (proto)**:
  - `entity/v1/reception_link.proto` becomes `scanner.proto` (`Scanner`, `ScannerId`, `ScannerNumber`, `ScannerLinkToken`, `ScannerStatus`, `AdmissionWindow`).
  - `Admission.scanner_id`, `RejectedScan.scanner_id` and `RejectedTicket.earlier_scanner_number`.
  - The two services above replace `rpc/organizer/reception_link/v1` and `rpc/organizer/reception/v1`.
  - The scanner call signature's first line becomes `liverty-music.scanner.v1`.
  - These are breaking changes on BSR (`buf skip breaking`). No client outside this product uses them.
- **backend**:
  - One Atlas migration renames the tables and columns in place: `reception_links` → `scanners`, `token` → `link_token`, `token_hash` → `link_token_hash`, and `reception_link_id` → `scanner_id` on `admissions` and `rejected_scans`.
  - Entity, repository, usecase, handler, mapper and DI names follow the rename.
  - The two servers mount the renamed services.
  - The grants integration test names the renamed tables.
- **frontend**:
  - The console Scanner screen and its client.
  - The scanner app (`reception/`) client, call signature and verdict code.
  - `AdmissionCodeSession` on the tickets screen.
  - Generated clients.
- **cloud-provisioning**: comments that name `ReceptionService`. No resource changes.
- **Other in-flight changes**:
  - `ticket-wallet-and-checkin` archives before this change syncs its specs.
  - `unify-ticket-sales` lands before this change.
  - `harden-backend-process-lifecycle` keeps naming the `reception-api` workload, which does not change.
- **Production data**: test data only. Rows survive the rename unchanged.
