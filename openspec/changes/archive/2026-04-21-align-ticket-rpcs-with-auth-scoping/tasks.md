## 1. Specification — Proto changes (BREAKING)

- [x] 1.1 Edit `proto/liverty_music/rpc/ticket/v1/ticket_service.proto`: replace `reserved 2 / reserved "user_id"` in `MintTicketRequest` with `liverty_music.entity.v1.UserId user_id = 2 [(buf.validate.field).required = true];`
- [x] 1.2 Update the `MintTicketRequest` message doc comment: remove the "The recipient fan is identified from the authenticated user's JWT claims, not from a request field" paragraph and replace with a comment referencing the `rpc-auth-scoping` convention
- [x] 1.3 Edit `ticket_service.proto`: replace `reserved 1 / reserved "user_id"` in `ListTicketsRequest` with `liverty_music.entity.v1.UserId user_id = 1 [(buf.validate.field).required = true];`
- [x] 1.4 Update the `ListTicketsRequest` message doc comment similarly
- [x] 1.5 Edit `proto/liverty_music/rpc/entry/v1/entry_service.proto`: replace `reserved 2 / reserved "user_id"` in `GetMerklePathRequest` with `liverty_music.entity.v1.UserId user_id = 2 [(buf.validate.field).required = true];`
- [x] 1.6 Update the `GetMerklePathRequest` message doc comment similarly
- [x] 1.7 Confirm `GetTicketRequest` and `VerifyEntryRequest` are **not** modified (documented in design.md as deliberate)
- [x] 1.8 Run `buf format -w` and `buf lint` locally

## 2. Specification — PR and Release

- [x] 2.1 Commit proto + change artifacts on a new branch in the specification repo
- [x] 2.2 Open PR with the `buf skip breaking` label; `buf-pr-checks.yml` must pass (PR #418)
- [x] 2.3 Obtain review and merge to `main` (merge commit f3c0e8a)
- [x] 2.4 Create GitHub Release on specification (new minor version `vX.Y.0`, body flagged as containing breaking changes) so `buf-release.yml` pushes to BSR (v0.39.0)
- [x] 2.5 Monitor `buf-release.yml` via `gh run watch --repo liverty-music/specification` until BSR gen completes (workflow completed in 9s; BSR-generated packages verified available via `go get` and `npm install` of v0.39.0-based versions)

## 3. Backend — Prepare branch against planned type shape

- [x] 3.1 Branch the backend repo from current `main`
- [x] 3.2 In `internal/adapter/rpc/ticket_handler.go`, update `MintTicket`: insert `if err := mapper.RequireUserIDMatch(user.ID, req.Msg.GetUserId().GetValue()); err != nil { return nil, err }` immediately after the `userRepo.GetByExternalID` call and before the Safe-address block
- [x] 3.3 Similarly update `ListTickets`: insert `RequireUserIDMatch(user.ID, req.Msg.GetUserId().GetValue())` before `ticketUseCase.ListTicketsForUser`
- [x] 3.4 Locate the `EntryService.GetMerklePath` handler and insert `RequireUserIDMatch(user.ID, req.Msg.GetUserId().GetValue())` before the Merkle-path lookup
- [x] 3.5 BSR gen completed before handler edits — TODO placeholders were not needed; generated `GetUserId()` accessor used directly
- [x] 3.6 Confirm `GetTicket` and `VerifyEntry` handlers remain unchanged

## 4. Backend — Handler tests

- [x] 4.1 In `internal/adapter/rpc/ticket_handler_test.go`, add a table-driven test case for `MintTicket` where `request.user_id != jwt.sub`-resolved user.ID, asserting `connect.CodePermissionDenied`
- [x] 4.2 Add a test case for `MintTicket` with matching `user_id` that proceeds to mint (happy path)
- [x] 4.3 Add equivalent mismatch + match test cases for `ListTickets`
- [x] 4.4 Add equivalent mismatch + match test cases for `GetMerklePath` (in the appropriate entry handler test file)
- [x] 4.5 Confirm existing JWT-absent tests still produce `UNAUTHENTICATED` (middleware still runs first)

## 5. Frontend — Prepare branch against planned type shape

- [x] 5.1 Branch the frontend repo from current `main`
- [x] 5.2 Grep for every call site of `ticketService.mintTicket` / `.listTickets` and `entryService.getMerklePath`; list them in a local note (findings: only `listTickets` in tickets-route.ts and `getMerklePath` via proof-service — `MintTicket` has no frontend call site yet)
- [x] 5.3 Inject `user_id` from `IUserService.current.id` into each request body — matches existing `userService.get` / `userService.updateHome` pattern
- [x] 5.4 BSR gen completed before frontend edits — TODO placeholders were not needed; generated `UserId` type used directly

## 6. Cross-repo release — BSR coordination

- [x] 6.1 After specification Release + BSR gen completes (task 2.5), run `go get buf.build/gen/go/liverty-music/schema/...@vX.Y.0` in backend; `go mod tidy` (upgraded to v1.36.11-20260421074642-d769c71c8006.1)
- [x] 6.2 Generated types used directly — no placeholder swap needed because BSR gen completed before handler edits
- [x] 6.3 Run `make check` in backend — lint + tests must pass
- [x] 6.4 Run `npm install @buf/liverty-music_schema.connectrpc_es@<v1-channel>` in frontend (pinned: `1.10.0-20260421074642-d769c71c8006.1` / `1.6.1-20260421074642-d769c71c8006.2`)
- [x] 6.5 Generated types used directly — no placeholder swap needed
- [x] 6.6 Run `make check` in frontend — lint + tests must pass

## 7. Backend and Frontend PRs

- [x] 7.1 Push backend branch and open PR; CI must pass from first push (do not submit as draft) — `liverty-music/backend#285`
- [x] 7.2 Push frontend branch and open PR; CI must pass from first push — `liverty-music/frontend#341`
- [x] 7.3 Obtain review and land both PRs to `main` (backend merge commit `cad2b0a`; frontend merge commit `5f5d21f`)
- [x] 7.4 Monitor ArgoCD / deployment workflows to confirm dev rollout completes (image-updater picked up new digests within 2 min of merge; server/consumer/web-app pods now running merge-commit-tagged images)

## 8. Post-merge verification

- [x] 8.1 In dev: call `MintTicket` via curl with matching `user_id` — auth layer verified (204/403/400 negative paths ruled out; request with matching `user_id` against a non-existent `event_id` returns `not_found`, proving the handler reached business logic past `RequireUserIDMatch`). Full positive-path mint against a real event is deferred to a real onboarded user.
- [x] 8.2 In dev: call `MintTicket` via curl with mismatched `user_id` — returns HTTP 403 `{"code":"permission_denied","message":"user_id does not match authenticated user"}`
- [x] 8.3 In dev: call `ListTickets` via curl with missing `user_id` — returns HTTP 400 `{"code":"invalid_argument","message":"validation error:\n - user_id: value is required [required]"}` (protovalidate enforces before handler runs)
- [x] 8.4 In dev: call `GetMerklePath` via curl with mismatched `user_id` — returns HTTP 403 `{"code":"permission_denied","message":"user_id does not match authenticated user"}`
- [ ] 8.5 Smoke-test the frontend ticket flow signed in as a real user: ticket list renders, mint flow works, QR generation works (deferred — requires a user with existing ticket data and cannot be automated headlessly under Passkey-only auth)

## 9. Follow-up handoff

- [x] 9.1 Flag to the owner of `implement-ticket-system-mvp` that `manual-verification.md` needs `user_id` added to the sample curl payloads for `MintTicket`, `ListTickets`, and `GetMerklePath` (same owner; delivered in `liverty-music/specification#422` — the runbook now resolves `${USER_ID}` via idempotent `UserService.Create` and includes `user_id` in every relevant curl, plus documents the `PERMISSION_DENIED` / `INVALID_ARGUMENT` paths)
- [x] 9.2 Ready for `/opsx:archive`
