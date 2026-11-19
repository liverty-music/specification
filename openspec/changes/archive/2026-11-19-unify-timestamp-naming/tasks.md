## 1. specification: proto and naming rule

- [x] 1.1 Rename `ResaleListing.sold_time` to `sell_time` and `ResaleListing.deadline_time` to `close_time` in `proto/liverty_music/entity/v1/resale_listing.proto`, and `discovered_time` to `find_time` in `proto/liverty_music/rpc/admin/concert_candidate/v1/concert_candidate_service.proto`, keeping field numbers and rewording their comments ("close time", "find time"); verify `buf lint` passes and `buf breaking` reports only these three renames
- [x] 1.2 Rewrite the timestamp rule in `AGENTS.md` (and its `CLAUDE.md` copy) to the rule in design.md "The rule": every layer uses the present-tense verb plus `_time`, only the last word is the verb, a badly reading verb takes a natural one; verify `grep -n '_at' AGENTS.md` finds no rule that reserves `_at` for the DB
- [x] 1.3 Open the proto PR with the `buf skip breaking` label, merge it, publish the release and wait for `buf-release.yml` to finish; verify with `gh run list --repo liverty-music/specification --workflow buf-release.yml --limit 1`

## 2. backend: schema and migration

- [x] 2.1 Rename every column in design.md "Column renames" in `schema.sql`, with the index names that contain an old column name and the `COMMENT ON COLUMN` texts that quote one; verify `make lint-schema` passes
- [x] 2.2 Write the Atlas migration by hand as `ALTER TABLE ... RENAME COLUMN` and `ALTER INDEX ... RENAME TO` statements (never drop and add), update `atlas.sum`, and verify `atlas migrate diff` against `schema.sql` reports no remaining difference and `atlas migrate lint` reports no destructive change
- [x] 2.3 Add the `_at` column check to `scripts/lint-schema.sh` and spell the audit-column check as `update_time` / `delete_time`; verify `make lint-schema` fails on a scratch copy of `schema.sql` with an `x_at TIMESTAMPTZ` column and passes on the real one
- [x] 2.4 Rewrite `backend/AGENTS.md` lines that state the DB `_at` rule (Database naming, "When a timestamp exists", the column-review bullet) to the single rule; verify `grep -nE '_at\b' AGENTS.md` finds only references to external payload keys

## 3. backend: code (components/entity and components/usecase listed in proposal.md)

- [x] 3.1 Upgrade the generated proto package to the release from 1.3 and adopt `SellTime`, `CloseTime` and `FindTime` at the RPC mapping; verify `go build ./...` passes
- [x] 3.2 Rename the Go entity fields in design.md "Go, TS and log keys" (`DiscoveredTime` to `FindTime`, `LastFoundTime` to `LastFindTime`, `SoldTime` to `SellTime`, `RejectedTime`, `SuppressedTime`, `ScannedTime`, `SearchedTime`, `SignedTime`, `BoundTime`, `RevokedTime`, `RegisteredTime` to their present forms, the listing deadline to `CloseTime`), the webhook `CreatedAt` / `ReceivedAt` fields (JSON keys kept), and every `slog` key that names a timestamp; verify `go build ./...` and `go vet ./...` pass
- [x] 3.3 Update every repository query and the outbox query in `internal/infrastructure/messaging/outbox.go` to the new column names; verify `grep -rnE '\b[a-z_]+_at\b' internal cmd pkg` finds only the external JSON keys listed in design.md Non-Goals, and the repository integration tests pass against a database migrated with 2.2
- [x] 3.4 Update the `@spec` annotations that cite the five renamed scenario titles (proposal.md table) and run `python3 scripts/check-scenario-coverage.py unify-timestamp-naming --repos <backend worktree> <frontend worktree>` from the specification store; add an annotated test for any scenario of the delta specs it reports uncovered, and verify it reports none
- [x] 3.5 Run `make check`; verify it passes

## 4. frontend: code

- [x] 4.1 Upgrade the generated proto package to the release from 1.3 and rename `soldTime` to `sellTime` and `deadlineTime` to `closeTime` in `src/entities/resale-listing.ts` and `src/adapter/rpc/mapper/resale-listing-mapper.ts` and their readers; verify `npm run typecheck` and the resale listing unit tests pass
- [x] 4.2 Rename `discoveredTime` to `findTime` in the admin approval queue (`admin/approval-queue/approval-queue-route.ts` and `.html`), and `startsAt` to `startTime` in the organizer data-list story and the `organizer/i18n/converters.ts` examples; verify `npm run test` passes for those files
- [x] 4.3 Rename the wallet snapshot's `savedAt` to `saveTime` (`src/routes/tickets/wallet-view.ts`, `tickets-route.ts`, `ticket-device-notices`) and the referral record's `expiresAt` to `expireTime` (`src/adapter/storage/referral-storage.ts`); verify the storage unit tests pass, including one that shows a record saved under the old key is dropped like a missing one
- [x] 4.4 Run `make check`; verify it passes

## 5. Cutover (prod)

- [x] 5.1 Before merging the backend PR, check that no workflow input, step result, output or message type of a registered DBOS workflow (serialized as JSON) holds a renamed Go field without a `json` tag, so a pending workflow resumes unchanged on the new release; verify a reflect walk over those types finds none
- [x] 5.2 Merge the backend PR, publish the backend release, merge the cloud-provisioning tag bump, and merge and release the frontend PR in the same window; verify the `backend-migration` AtlasMigration reports the new version applied and every backend rollout completes
- [x] 5.3 Verify prod logs show no `column ... does not exist` error for 30 minutes after the rollout, and the fan resale listing screen shows a listing's close time
