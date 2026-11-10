## 1. backend: shared contracts and layer direction

- [ ] 1.1 Move the event message contract (payload decoding, `ce_subject`, the redelivery mark and its reader) from `internal/infrastructure/messaging` into a new `pkg/` package. Switch `internal/adapter/event` and `internal/infrastructure/messaging` to it. Verify that `go test ./internal/adapter/event/... ./internal/infrastructure/messaging/... ./pkg/...` passes, including the redelivery tests.
- [ ] 1.2 Move the caller context contract (`Claims`, the caller Organization id, their context setters and getters) from `internal/infrastructure/auth` into a new `pkg/` package. The interceptors stay in `infrastructure/auth`. Switch the adapters (`rpc`, `pb`, `webhook`) to it. Verify that the auth interceptor tests and the handler tests pass.
- [ ] 1.3 Declare the webhook token check as an interface in `internal/adapter/webhook`, and inject `auth.WebhookValidator` through it in `internal/di`. Verify that the `pre_access_token_handler` tests pass with a mockery mock of the interface.
- [ ] 1.4 Move `PrefectureName` into `internal/entity` and switch `adapter/linkpreview` and `infrastructure/geo` to it. Move `SeriesImageURLBuilder` into `infrastructure/gcp/storage` behind a `SeriesImageURLs` interface declared in `adapter/pb`, wired in `internal/di`; the variant object key stays in the storage package. Verify that the moved unit tests pass and `adapter/pb` no longer imports `infrastructure/gcp/storage`.
- [ ] 1.5 Make `messaging.Announcement.Payload` the announced entity, declare `messaging.Encoder`, implement it in `adapter/pb` (with the `ForAnnouncement` variants), and pass it to `messaging.NewOutbox` in `internal/di`. Remove the `pb.From…` calls from the 21 infrastructure files and update backend `AGENTS.md` "Announcements". Verify with an `adapter/pb` table test that encodes every announced entity type and fails an unknown one, and that `go test ./internal/infrastructure/database/rdb/...` passes, including every announcement test.
- [ ] 1.6 Switch the `follow`, `concert`, `push_subscription`, `notification`, `wallet_public_key` and `ticket_journey` handlers from `entity.UserRepository` to `usecase.UserUseCase` (`callerUserID` / `ResolveCaller`), and update their wiring in `internal/di`. Verify that each handler's tests pass with the UserUseCase mock, including the NotFound case for a caller without a stored User.
- [ ] 1.7 Route `BackendOrganizationHandler` and `BackendUserHandler` through a usecase that owns the identity-provider ports they call today. Verify that their tests pass with the usecase mock and return the same codes as before.
- [ ] 1.8 Enable depguard in `.golangci.yml` with the layer rules of design.md. Verify that `make lint` reports no depguard finding.

## 2. backend: errors

- [ ] 2.1 Make every entity validator and guard return an `apperr` error with the code its callers attach today: InvalidArgument for the validators, FailedPrecondition for `ValidateLotteryEntrySale` and the state guards. Rewrite the comments at `user.go:35`, `user.go:70` and `settlement.go:136` to state the rule. Verify with entity tests that assert the code of each rule's failure.
- [ ] 2.2 Make the callers in `internal/usecase` and `internal/infrastructure/database/rdb` return those errors as they are. Replace the nine `apperr.New(code, err.Error())` sites listed in design.md with `apperr.Wrap`, or with a plain return where the entity now carries the code. Verify that usecase tests assert the same codes as before, and that `grep -rn 'apperr.New(.*err.Error()' internal` finds nothing.
- [ ] 2.3 Replace the code-only sentinels of design.md (`ErrScannerNotUsable`, `ErrUnsupportedImage`, `ErrResaleWinNotRevertible`, `errInvalidAdmissionCode`, `errBase45`, and the seven gemini errors) with `apperr` errors created with their code, and switch each `errors.Is` to the code. Verify that the affected tests assert the codes and pass.
- [ ] 2.4 Upgrade go-apperr to the release that closes pannpers/go-apperr#8. Verify that `make check` passes.
- [ ] 2.5 Replace `ErrResaleListingCancelled`, `ErrUnknownScannerLinkToken`, `errSubjectGone` and `ErrPasskeyAccountPending` with `apperr` errors carrying the reasons of design.md, drop `errScannerRefused`, and switch each `errors.Is` to the code and reason. Keep `SCANNER_LINK_TOKEN_UNKNOWN` off the wire as design.md says. Verify that the tests of each caller pass (`order_lottery_workflow`, the reception rate limiter, `notification_uc`, `notification_delivery`, `passkey_workflow`), that a scanner client gets the same error for an unknown and a revoked token, and that `grep -rnE '^\s*(var )?[eE]rr[A-Za-z]* *= *(errors\.New|fmt\.Errorf)' internal --include='*.go'` finds no non-test hit.

## 3. backend: clock and test doubles

- [ ] 3.1 Pass the time into `NewIdentityVerification` and `DiscoveredTicketSale.Validate`. Verify that `grep -n 'time.Now' internal/entity/*.go` finds no non-test hit, and that their tests use a fixed time.
- [ ] 3.2 Make every usecase that calls `time.Now()` read the injected `Clock` (workflows read it inside a step). Verify that `grep -n 'time.Now()' internal/usecase/*.go` finds only the `Clock` default, and that the affected tests pin the time.
- [ ] 3.3 Replace the hand-written fakes in usecase tests with the mockery mocks (`make mocks`). Verify that `go test ./internal/usecase/...` passes, and that `grep -nE '^type (fake|stub|spy|recording|memory)[A-Za-z]* struct' internal/usecase/*_test.go` finds nothing.

## 4. backend: docs

- [ ] 4.1 Remove "One PR per repository." from backend `AGENTS.md` line 20, leaving the rest of the rule. Verify that `grep -n 'One PR per repository' AGENTS.md` finds nothing.

## 5. frontend: docs

- [ ] 5.1 Remove "One PR per repository." from frontend `AGENTS.md` line 20, leaving the rest of the rule. Verify that `grep -n 'One PR per repository' AGENTS.md` finds nothing.
