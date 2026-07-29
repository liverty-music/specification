## 1. Specification

- [x] 1.1 Add `open_time = 10` field (type `entity.v1.OpenTime`, optional) to `PendingConcert` in `proto/liverty_music/rpc/admin/v1/concert_service.proto`
- [x] 1.2 Run `buf lint`, `buf format -w`, and `buf breaking --against '.git#branch=main'` to verify no proto issues
- [ ] 1.3 Open a PR for the specification change and merge it
- [ ] 1.4 Create a GitHub Release tag on the specification repo to trigger BSR code generation
- [ ] 1.5 Confirm `buf-release.yml` CI completes successfully and the new package version is available on BSR

## 2. Backend

> **Requires task 1.5 to be complete first.** Do not run 2.1 until `buf-release.yml` has finished and the new BSR package version is confirmed available — otherwise `go get` resolves the pre-change schema.

- [ ] 2.1 Upgrade the generated Go package: `go get buf.build/gen/go/liverty-music/schema/...` then `go mod tidy`
- [ ] 2.2 Add `OpenTime` mapping to `PendingConcertToProto` in `internal/adapter/rpc/mapper/pending_concert.go` (follow the `StartTime` pattern at lines 31–33)
- [ ] 2.3 Create `internal/adapter/rpc/mapper/pending_concert_test.go` with a `TestPendingConcertToProto` function covering `open_time` present and absent (note: `concert_test.go` tests `ConcertToProto` — the new tests belong in a dedicated file for the `PendingConcert` mapper)
- [ ] 2.4 Run `make check` and confirm it passes
- [ ] 2.5 Open a PR for the backend change, confirm CI green, and merge

## 3. Frontend

> **Requires task 1.5 to be complete first.** BSR-generated npm packages use timestamped pre-release version strings (e.g., `^1.10.0-20260725094030-xxx.1`); `@latest` does not reliably resolve to them. After 1.5 completes, find the new version by running `npm view @buf/liverty-music_schema.bufbuild_es versions --json` or checking the BSR release page, then pin to that version.

- [ ] 3.1 Upgrade the generated npm packages: `npm install @buf/liverty-music_schema.bufbuild_es@<new-version> @buf/liverty-music_schema.connectrpc_es@<new-version>`
- [ ] 3.2 Add `readonly openTime: string` to the `QueueRow` interface in `admin/approval-queue/approval-queue-route.ts`
- [ ] 3.3 Add `openTime: formatTimeOfDay(concert.openTime?.value)` to `toRow()` in `approval-queue-route.ts`
- [ ] 3.4 Add `readonly stagedOpenTime: string` to the `ConflictView` interface
- [ ] 3.5 Set `stagedOpenTime: row.openTime` in `toConflictView()` (replaces the hardcoded `—`)
- [ ] 3.6 Add an **Open time** `<th>` and `<td>` column to the approval queue table in `approval-queue-route.html`, positioned after Start time
- [ ] 3.7 Replace the hardcoded `${'—'}` for staged open time in the conflict dialog with `${conflictView.stagedOpenTime}`
- [ ] 3.8 In `test/admin/approval-queue/approval-queue-route.spec.ts`, add test cases covering: (a) `toRow()` maps `concert.openTime?.value` via `formatTimeOfDay` correctly for present and absent values; (b) `toConflictView()` sets `stagedOpenTime` from `row.openTime`
- [ ] 3.9 Run `make check` and confirm it passes
- [ ] 3.10 Open a PR for the frontend change, confirm CI green, and merge

## 4. Ship to Production

- [ ] 4.1 Create a GitHub Release for the backend repo to publish to prod
- [ ] 4.2 Create a GitHub Release for the frontend repo to publish to prod
- [ ] 4.3 Confirm prod deployment completes and the Open time column is visible in the approval queue
