## Why

The admin console can review the discovery queue (approve/reject pending concerts) but has no way to see or correct **already-published** concerts. A wrongly-approved concert — wrong artist, duplicate, bad date — is currently permanent from the console's side. Operators need to list approved concerts per artist and remove mistakes.

In building this, the admin concert RPC surface also stops fitting its name: `ConcertModerationService` was scoped to moderation (approve/reject), but it now also lists and deletes published concerts. The package `liverty_music.rpc.admin.v1` already conveys the admin audience, so the `Moderation` qualifier is redundant and the verbose method names (`ListPendingConcerts`, `ApproveConcert`) duplicate context the service already carries.

## What Changes

- **BREAKING** Rename `liverty_music.rpc.admin.v1.ConcertModerationService` to `ConcertService`, mirroring the consumer `liverty_music.rpc.concert.v1.ConcertService` (package disambiguates the two). Rename the proto file `concert_moderation_service.proto` → `concert_service.proto`.
- **BREAKING** Simplify the existing methods to bare verbs now that the service name carries the entity: `ListPendingConcerts` → `ListPending`, `ApproveConcert` → `Approve`, `RejectConcert` → `Reject`.
- Add `List` — returns every published concert (no follower/proximity filter), carrying the `event_id` needed for deletion. Grouping by artist is done client-side.
- Add `Delete` — hard-deletes a published concert by `event_id`. The delete cascades through the existing `ON DELETE CASCADE` foreign keys (`event_performers`, `tickets`, `ticket_journeys`, `ticket_emails`, `merkle_tree`, and `sales_phases` via the series). **No guard**: deletion is unconditional, intended as an operator correction tool on a pre-launch internal surface where published rows have no real fan-owned data yet.
- Add a frontend admin route (`admin/approved-concerts/`) that lists approved concerts grouped by artist with a per-row manual delete (confirm dialog only).
- Backend (implementation, see design): merge `ConcertApprovalUseCase` into the single `concertUseCase` implementation (gaining `rejectedConcertRepo` + `seriesRepo`), exposed through segregated interfaces so the consumer handler keeps a read-only view and the admin handler gets the admin view; add `ConcertRepository.List` and `ConcertRepository.Delete`.

## Capabilities

### New Capabilities
- `admin-concert-management`: the admin `ConcertService` surface for managing **published** concerts — listing every approved concert (with the identifiers needed for follow-up actions) and hard-deleting a concert by event id with full database cascade and no precondition guard. Establishes the renamed, bare-verb admin concert RPC service as the home for admin concert operations.

### Modified Capabilities
- `admin-rpc-server`: the admin-scoped service registered on the admin server's mux (and targeted by the admin console's RPC client) is renamed from `ConcertModerationService` to `ConcertService`; scenarios that name the service are updated. The boundary admin-role authorization, dedicated port/host/CORS, and consumer-exclusion guarantees are unchanged.

## Impact

- **specification**: Breaking proto change (service + three method renames, two added methods, file rename) → requires the cross-repo release coordination workflow (specification PR → merge → GitHub Release `vX.Y.Z` → BSR gen) before backend/frontend can build.
- **backend**: Merge `ConcertApprovalUseCase` into `concertUseCase`; delete the standalone approval use case + interface; add a segregated admin use-case interface consumed by the renamed `AdminConcertHandler` (the Go handler struct keeps an admin-distinct name to avoid colliding with the consumer `ConcertHandler` in the shared `rpc` package). Add `ConcertRepository.List` (all published) and `Delete` (cascade). Update admin-server handler registration to the renamed generated `ConcertServiceHandler`.
- **frontend**: New `admin/approved-concerts/` route + view-model; rename `concert-moderation-client.ts` and re-point it at the renamed generated `ConcertService` client; client-side artist grouping; confirm-dialog delete.
- **cutover**: Breaking rename means the admin console's old client calls dead RPC paths once the backend swaps; backend and frontend release close together (admin-only, consumer-impact-free, pre-launch) so the gap is a brief internal-tool outage with no security exposure.
- **Out of scope**: delete guards / soft-delete / impact preview / audit log (explicitly deferred — operator correction tool only); on-chain SBT burn for cascade-deleted tickets (pre-launch, no real minted tickets); any consumer `ConcertService` change.
