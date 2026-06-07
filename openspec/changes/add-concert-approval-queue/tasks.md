## 1. Proto Definitions (specification)

- [x] 1.1 Create `rpc/admin/v1/concert_moderation_service.proto` with `service ConcertModerationService`
- [x] 1.2 Define `PendingConcert` message: `staged_id`, performing `Artist`, `title`, `LocalDate local_date`, optional `StartTime start_time`, `listed_venue_name`, resolved `Venue` (name, admin_area, place id, coordinates), `source_url` (reuse `Url` VO), `discovered_at`
- [x] 1.3 Define `ListPendingConcerts` (request/response with `repeated PendingConcert`), `ApproveConcert` (`staged_id`), `RejectConcert` (`staged_id`, required `reason`) RPCs with protovalidate constraints
- [x] 1.4 Document each RPC's `Possible errors` (PERMISSION_DENIED for non-admin, INVALID_ARGUMENT, NOT_FOUND tolerated as idempotent no-op per design)
- [x] 1.5 Run `buf lint` and `buf format -w`; confirm additive-only (no breaking change; consumer protos untouched)
- [ ] 1.6 Open specification PR; after review + CI, merge and publish a GitHub Release (`vX.Y.Z`) to trigger BSR gen (CI-only; do NOT run `buf push`/`buf generate` locally)
- [ ] 1.7 Monitor `buf-release.yml` until BSR gen completes; record the published version

## 2. Database Migration (backend)

- [ ] 2.1 Atlas migration for `staged_concerts`: `id` UUID PK, `artist_id` FK→artists, `title`, `local_date` DATE, `start_at`/`open_at` TIMESTAMPTZ nullable, `listed_venue_name` TEXT, `admin_area` TEXT nullable, `source_url` TEXT, resolved-venue columns (`resolved_place_id`, `resolved_venue_name`, `resolved_admin_area`, `resolved_lat`, `resolved_lng`) nullable, `discovered_at` TIMESTAMPTZ NOT NULL
- [ ] 2.2 Add a uniqueness constraint over the staging natural key `(artist_id, local_date, resolved_place_id)` with a NULL-safe fallback path on `listed_venue_name` so re-discovery refreshes the pending row rather than duplicating it
- [ ] 2.3 Atlas migration for `rejected_concerts_log` (append-only): `id` UUID PK, raw scraped payload columns, resolved-venue preview columns, `reason` TEXT, `reviewed_by` TEXT, `rejected_at` TIMESTAMPTZ NOT NULL; no FK that would cascade-delete history
- [ ] 2.4 Apply locally with `atlas migrate apply --env local`; confirm `events`/`venues` schemas unchanged
- [ ] 2.5 Upgrade backend to the BSR-published proto version (`go get ...@vX.Y.Z`, `go mod tidy`); confirm `make check`

## 3. Backend Entity & Repository

- [ ] 3.1 Define `StagedConcert` entity (`internal/entity/staged_concert.go`) with the scraped + resolved-venue fields and a `pending`-only model
- [ ] 3.2 Define `StagedConcertRepository` interface: `Upsert(pending)` (refresh-on-conflict by natural key), `ListPending`, `GetByID`, `Delete`, plus a `ListPendingNaturalKeys` (or equivalent) for dedup
- [ ] 3.3 Implement pgx `StagedConcertRepository` (unnest where bulk; UPSERT refresh on natural key)
- [ ] 3.4 Define `RejectedConcertLogRepository` interface + pgx impl: `Append(entry)` only
- [ ] 3.5 Repository integration tests: refresh-on-conflict (no duplicate pending), delete, append-only log, NULL-safe natural key fallback

## 4. Backend Discovery → Staging Rewrite

- [ ] 4.1 Split `CreateFromDiscovered`: keep venue **resolution** (Google Places) on the discovery path; replace the `events`/`series`/`performers` insert + `CONCERT.created` publish with `StagedConcertRepository.Upsert(pending)`
- [ ] 4.2 Implement B2 venue handling: resolve via Places, denormalize onto the staged row; do NOT create a `venues` row on the discovery path
- [ ] 4.3 Extend `FilterNew` dedup to also exclude concerts already `pending` in `staged_concerts`; confirm it does NOT consult `rejected_concerts_log`
- [ ] 4.4 Unit tests: discovery stages pending and writes no `events`/`venues`; pending refresh; rejected key re-stages

## 5. Backend Approve / Reject Use Cases + RPC

- [ ] 5.1 Implement `ApproveConcert` use case: create/reuse `venues` row, run the existing series/event/performer bulk insert (UPSERT), delete the staged row, publish `CONCERT.created`; idempotent when the staged row is gone
- [ ] 5.2 Implement `RejectConcert` use case: append `rejected_concerts_log` (with reviewer identity + reason), delete the staged row; idempotent when gone
- [ ] 5.3 Confirm `CONCERT.created` is published ONLY from the approve path (removed from discovery)
- [ ] 5.4 Implement `ConcertModerationService` handler (`ListPendingConcerts`/`ApproveConcert`/`RejectConcert`) with mappers to `PendingConcert`
- [ ] 5.5 Apply admin-org authorization per `rpc-auth-scoping`; non-admin callers get PERMISSION_DENIED. Wire reviewer identity (Zitadel subject) into reject logging
- [ ] 5.6 Register the service in DI / RPC server wiring
- [ ] 5.7 Use-case + handler tests (approve publishes + notifies; reject logs + drops; idempotency; auth denial); `make check` green

## 6. Frontend Admin Console UI

- [ ] 6.1 Upgrade the frontend to the BSR-published proto version; generate the `ConcertModerationService` client
- [ ] 6.2 Add an approval-queue route + component in the bundle-isolated `admin/` app (no consumer-SPA import; respect the import-boundary lint)
- [ ] 6.3 Render the pending list with all reviewable fields (artist, title, date, start time, raw listed venue name, resolved venue name + admin_area, source URL, discovered-at)
- [ ] 6.4 Wire approve action (`ApproveConcert`) and reject action with a reason prompt (`RejectConcert`); remove the row on success; surface errors
- [ ] 6.5 Component/unit tests; `make check` green

## 7. Ship to Production

- [ ] 7.1 Open backend PR after the proto package upgrade + swap succeeds locally (CI green from first push); merge
- [ ] 7.2 Open frontend PR; merge
- [ ] 7.3 Release backend (`vX.Y.Z`) and frontend per each repo's release process so the gate runs in production; verify the discovery cron now stages (no direct publish) and the admin console approval queue works against prod
- [ ] 7.4 Confirm `CONCERT.created` (push notifications) fires only on approval in production
