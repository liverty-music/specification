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

- [ ] 2.1 Commit proto + change artifacts on a new branch in the specification repo
- [ ] 2.2 Open PR with the `buf skip breaking` label; `buf-pr-checks.yml` must pass
- [ ] 2.3 Obtain review and merge to `main`
- [ ] 2.4 Create GitHub Release on specification (new minor version `vX.Y.0`, body flagged as containing breaking changes) so `buf-release.yml` pushes to BSR
- [ ] 2.5 Monitor `buf-release.yml` via `gh run watch --repo liverty-music/specification` until BSR gen completes

## 3. Backend — Prepare branch against planned type shape

- [ ] 3.1 Branch the backend repo from current `main`
- [ ] 3.2 In `internal/adapter/rpc/ticket_handler.go`, update `MintTicket`: insert `if err := mapper.RequireUserIDMatch(user.ID, req.Msg.GetUserId().GetValue()); err != nil { return nil, err }` immediately after the `userRepo.GetByExternalID` call and before the Safe-address block
- [ ] 3.3 Similarly update `ListTickets`: insert `RequireUserIDMatch(user.ID, req.Msg.GetUserId().GetValue())` before `ticketUseCase.ListTicketsForUser`
- [ ] 3.4 Locate the `EntryService.GetMerklePath` handler and insert `RequireUserIDMatch(user.ID, req.Msg.GetUserId().GetValue())` before the Merkle-path lookup
- [ ] 3.5 At each of the three call sites, leave a `// TODO: swap to generated type after BSR gen` comment next to the `req.Msg.GetUserId().GetValue()` call to mark the placeholder
- [ ] 3.6 Confirm `GetTicket` and `VerifyEntry` handlers remain unchanged

## 4. Backend — Handler tests

- [ ] 4.1 In `internal/adapter/rpc/ticket_handler_test.go`, add a table-driven test case for `MintTicket` where `request.user_id != jwt.sub`-resolved user.ID, asserting `connect.CodePermissionDenied`
- [ ] 4.2 Add a test case for `MintTicket` with matching `user_id` that proceeds to mint (happy path)
- [ ] 4.3 Add equivalent mismatch + match test cases for `ListTickets`
- [ ] 4.4 Add equivalent mismatch + match test cases for `GetMerklePath` (in the appropriate entry handler test file)
- [ ] 4.5 Confirm existing JWT-absent tests still produce `UNAUTHENTICATED` (middleware still runs first)

## 5. Frontend — Prepare branch against planned type shape

- [ ] 5.1 Branch the frontend repo from current `main`
- [ ] 5.2 Grep for every call site of `ticketService.mintTicket` / `.listTickets` and `entryService.getMerklePath`; list them in a local note
- [ ] 5.3 Inject the cached `user_id` (from the `UserIdCache` service introduced by `standardize-user-scoped-rpc-auth`) into each request body — same pattern as existing `userService.get` / `userService.updateHome` call sites
- [ ] 5.4 Add a `// TODO: swap to generated type after BSR gen` comment at each injection point

## 6. Cross-repo release — BSR coordination

- [ ] 6.1 After specification Release + BSR gen completes (task 2.5), run `go get buf.build/gen/go/liverty-music/schema/...@vX.Y.0` in backend; `go mod tidy`
- [ ] 6.2 Swap placeholder types for generated types at the three backend handler call sites; remove the TODO comments
- [ ] 6.3 Run `make check` in backend — lint + tests must pass
- [ ] 6.4 Run `npm install @buf/liverty-music_schema.connectrpc_es@latest` in frontend
- [ ] 6.5 Swap placeholder types for generated types at frontend call sites; remove TODO comments
- [ ] 6.6 Run `make check` in frontend — lint + tests must pass

## 7. Backend and Frontend PRs

- [ ] 7.1 Push backend branch and open PR; CI must pass from first push (do not submit as draft)
- [ ] 7.2 Push frontend branch and open PR; CI must pass from first push
- [ ] 7.3 Obtain review, land both PRs to `main`
- [ ] 7.4 Monitor ArgoCD / deployment workflows to confirm dev rollout completes

## 8. Post-merge verification

- [ ] 8.1 In dev: call `MintTicket` via curl with matching `user_id` — expect `200` and minted ticket
- [ ] 8.2 In dev: call `MintTicket` via curl with mismatched `user_id` — expect `PERMISSION_DENIED`
- [ ] 8.3 In dev: call `ListTickets` via curl with missing `user_id` — expect `INVALID_ARGUMENT`
- [ ] 8.4 In dev: call `GetMerklePath` via curl with mismatched `user_id` — expect `PERMISSION_DENIED`
- [ ] 8.5 Smoke-test the frontend ticket flow signed in as a real user: ticket list renders, mint flow works, QR generation works

## 9. Follow-up handoff

- [ ] 9.1 Flag to the owner of `implement-ticket-system-mvp` that `manual-verification.md` needs `user_id` added to the sample curl payloads for `MintTicket`, `ListTickets`, and `GetMerklePath`
- [ ] 9.2 Once all tasks above are done, this change is ready for `/opsx:archive`
