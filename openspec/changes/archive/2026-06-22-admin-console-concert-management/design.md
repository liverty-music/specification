## Context

The admin console (split onto a dedicated admin Connect server by `admin-rpc-server`)
currently exposes only the concert approval queue via
`liverty_music.rpc.admin.v1.ConcertModerationService` (`ListPendingConcerts`,
`ApproveConcert`, `RejectConcert`). Backend logic lives in a standalone
`ConcertApprovalUseCase` (`concert_approval_uc.go`), called by
`ConcertModerationHandler`. There is no surface for managing concerts **after**
they are published — a wrongly-approved concert is permanent from the console.

Two layers are conflated in the discussion and must be kept separate:
- **RPC service / server boundary** — about authorization, host, CORS. Admin RPCs
  live in `rpc/admin/v1` and are served on the admin Connect server, gated by a
  boundary `RequireRoleInterceptor("admin")`. This boundary is preserved.
- **Use-case layer** — auth-agnostic business logic. Authorization is *not* a
  use-case concern, so the use-case layer is free to be organized by capability,
  not by audience.

Published concerts and their dependents are linked by `ON DELETE CASCADE` foreign
keys: deleting an `events` row cascades to `event_performers`, `concerts`,
`tickets` (on-chain SBT records), `ticket_journeys`, `ticket_emails`, `merkle_tree`,
and — via the parent `series` — `sales_phases` / `sales_phase_reminders`.

## Goals / Non-Goals

**Goals:**
- Give operators a way to list every published concert (grouped by artist) and
  hard-delete mistakes.
- Rename the admin concert service to `ConcertService` with bare-verb methods,
  matching the consumer service shape and the established convention.
- Remove use-case duplication: a single concrete concert use case, with reuse at
  the repository layer and capability-segregated interfaces at the handler layer.

**Non-Goals:**
- Delete guards, soft-delete, impact preview, or audit logging (deferred; this is
  an unconditional operator correction tool).
- Burning the on-chain ERC-5192 tokens for cascade-deleted `tickets` rows.
- Any change to the consumer `liverty_music.rpc.concert.v1.ConcertService`.
- Renaming the admin server's port/host/CORS or the boundary auth layer.

## Decisions

### D1: Rename `ConcertModerationService` → `admin.v1.ConcertService` (breaking)

The package `liverty_music.rpc.admin.v1` already conveys the admin audience, so a
`Moderation`/`Admin` qualifier on the service is redundant — and inaccurate once the
service also lists and deletes published concerts. The fully-qualified name
disambiguates it from the consumer `rpc.concert.v1.ConcertService` with no
collision. Methods drop the entity suffix the service already carries:
`ListPendingConcerts`→`ListPending`, `ApproveConcert`→`Approve`,
`RejectConcert`→`Reject`, plus new `List` and `Delete`. The proto file is renamed
`concert_moderation_service.proto`→`concert_service.proto`.

- *Alternative — additive only (keep the old name, just add `List`/`Delete`):*
  non-breaking and faster, but locks in a name that misdescribes the surface and
  perpetuates the verbose method style. Rejected: naming hygiene is worth one
  coordinated breaking release on an internal, pre-launch surface.
- *Alternative — fold admin concert RPCs into the consumer `ConcertService`:*
  rejected earlier — it would move admin methods onto the consumer server/host/CORS
  and outside the boundary interceptor, reintroducing the per-method-auth fragility
  `admin-rpc-server` removed.

### D2: Merge `ConcertApprovalUseCase` into the single `concertUseCase`

`concertUseCase` already holds every dependency the approval use case needs except
two (`rejectedConcertRepo`, `seriesRepo`). Merging removes a parallel use case
whose reads would otherwise duplicate concert-read logic. Auth is handled by the
interceptor, so a unified use case does not weaken any boundary.

- *Alternative — keep two use cases:* rejected; organizing use cases by audience
  (admin vs consumer) is the duplication source, and the dependency overlap here is
  near-total, so the merge is cheap.

### D3: Interface Segregation, not one fat interface

One concrete `concertUseCase` implements two interfaces consumed where needed:
- The consumer `ConcertHandler` depends on the existing read-only `ConcertUseCase`
  interface — **unchanged**, so it never sees `Delete`/`Approve` (least privilege).
- The admin handler depends on a new admin interface
  (`ListPending`/`Approve`/`Reject`/`List`/`Delete`).

This yields DRY (one implementation, read logic shared via `ConcertRepository`) and
least privilege (the consumer handler structurally cannot delete). In Go the
interfaces live next to the use case; the concrete struct satisfies both.

### D4: Go handler naming under a shared package

Both concert handlers live in the single Go package `internal/adapter/rpc`, so the
proto-level symmetry (both services named `ConcertService`) cannot extend to the Go
structs. The consumer handler stays `ConcertHandler`; the admin handler is renamed
`ConcertModerationHandler`→`AdminConcertHandler`. The admin-server registration
switches to the renamed generated `ConcertServiceHandler` constructor.

### D5: Reuse at the repository layer

Add `ConcertRepository.List(ctx)` (all published concerts, hydrated like the other
list methods) and `ConcertRepository.Delete(ctx, eventID)` (a single
`DELETE FROM events WHERE id = $1`, relying on the existing FK cascade — no manual
multi-table deletes). Both admin and any future caller reuse these; the use-case
layer stays thin over them.

### D6: Client-side artist grouping

`List` returns a flat slice; the admin SPA groups by performing artist in the view
model. This keeps the proto minimal (no nested `ArtistGroup` message) and mirrors
how the existing approval queue maps flat rows.

### D7: Catalog presentation — Artist → Series → events, native disclosure, grid, modal confirm

Enumerating every event inline made the screen unscannable once an artist had many
dates. The presentation is therefore a two-level grouping computed client-side from
the flat `List` result: performing artist, then series. Each series is a collapsed
**native `<details>`/`<summary>`** disclosure whose summary carries the event count
and date range, so an operator scans the catalog without expanding everything. The
expanded body lists each event with local date, start time, open time, and venue.
Start/open time render from the `Timestamp` wrapper (`.value` → `toDate()`); local
date stays the timezone-free `LocalDate` triple.

Column alignment across the separate sibling series sections uses a **shared CSS
Grid `grid-template-columns` token** applied to every header and event row, rather
than per-artist `<table>`s (which size columns independently and drift) or
`subgrid` (not needed when one token is shared by all rows and avoids the
Baseline-Newly-Available dependency).

Delete is gated by a **native `<dialog>` modal** opened with `showModal()`. The
confirm control receives initial focus (autofocus) so the operator confirms with
Enter and dismisses with Escape (native `<dialog>` cancel) — no `Delete` RPC is
issued until confirmation. The native dialog is preferred over the Invoker Commands
API (`command`/`commandfor`), which is Baseline 2025 and would require a polyfill;
`<dialog>` is widely available and needs none.

## Risks / Trade-offs

- **Breaking rename leaves a cutover gap** → The admin console's old client calls
  dead RPC paths once the backend serves the renamed service. Mitigation: release
  backend and frontend close together; the surface is admin-only, consumer-impact-
  free, and pre-launch, so the worst case is a brief internal-tool outage with no
  security exposure (same shape as the `admin-rpc-server` cutover).
- **Unconditional delete cascades into fan-owned data** → On a populated database,
  `Delete` would silently remove `ticket_journeys`/`tickets`. Mitigation (accepted,
  not engineered): pre-launch there is no real fan data; guards/soft-delete are an
  explicit follow-up if/when the catalog carries live tickets. Documented as a
  Non-Goal so the gap is a known decision, not an oversight.
- **Orphaned on-chain SBTs** → Deleting a `tickets` row does not burn the ERC-5192
  token on Base Sepolia, leaving a token pointing at a deleted event. Mitigation:
  out of scope pre-launch; revisit alongside any real ticketing launch.
- **Merged use case grows two dependencies** → `concertUseCase` gains
  `rejectedConcertRepo` + `seriesRepo`. Trade-off accepted: still far smaller than
  maintaining a parallel use case, and the struct remains capability-cohesive.

## Migration Plan

Follows the cross-repo release coordination workflow (breaking proto change):
1. **specification**: rename service + methods, add `List`/`Delete`, rename proto
   file; `buf lint`/`format`; confirm `buf breaking` reports only the intended
   service/method renames. Open PR with this OpenSpec change; merge after review/CI.
2. **specification Release**: publish GitHub Release `vX.Y.Z` → `buf-release.yml`
   pushes to BSR; monitor to success.
3. **backend** (prepared in parallel against the planned shape, finalized after BSR
   gen): merge the use case, add repo `List`/`Delete`, rename handler to
   `AdminConcertHandler`, swap to the regenerated `ConcertServiceHandler`; bump the
   BSR package; `make check` green; open PR; merge.
4. **frontend** (likewise): new `admin/approved-concerts/` route + view model,
   rename `concert-moderation-client.ts`, re-point at the regenerated admin
   `ConcertService`; `make check` green; open PR; merge.
5. **Ship to prod**: backend Release `vX.Y.Z` (retag dev AR image), then frontend
   Release; release the two close together to minimize the admin-tool cutover gap.
   Verify in prod: `List` returns published concerts, `Delete` removes a test
   concert end-to-end, and the approval queue (`ListPending`/`Approve`/`Reject`)
   still works under the new names.

**Rollback**: revert the backend/frontend deploys to the prior pinned versions; the
old `ConcertModerationService` paths return. The BSR schema is additive-forward, so
a downstream revert is a version pin change, not a schema rollback.

## Open Questions

- None blocking. (Deferred design — guards, soft-delete, impact preview, audit log,
  SBT burn — is captured as Non-Goals and follow-up, not open questions for this
  change.)
