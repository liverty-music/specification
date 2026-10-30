## 1. Proto (specification)

- [x] 1.1 Rename `LotteryEntryService.ListByTicketType` to `ListByTicketSale` with `ListByTicketSaleRequest` / `ListByTicketSaleResponse`, keeping every field name and number, and update the service and message comments (design D1); verify `buf lint`, `buf format -d` and `make words` pass and the proto PR carries `buf skip breaking`
- [x] 1.2 Merge the proto PR and cut the release; verify `gh run list --repo liverty-music/specification --workflow buf-release.yml --limit 1` succeeds for it

## 2. Entity operations (components/entity/lottery-entry/*)

- [x] 2.1 Rename `LotteryEntryRepository.GetStatsByTicketType`, `ListByTicketTypeAndUser` and `ListUndrawnForTicketType` to `GetStatsByTicketSaleAndTicketStock`, `ListByTicketSaleAndUser` and `ListEnteredByTicketSaleAndTicketStock` in `internal/entity/lottery_entry.go`, the rdb implementation and the regenerated mocks, and switch their callers in the use cases (checkout start's draw guard, AuthorizeCard, Confirm, RunDraw, ListOwnByEvent); verify `go build ./...` and `go test ./internal/usecase/...`
- [x] 2.2 Move the contract tests' annotations to the new paths, one test per scenario: `get-stats-by-ticket-sale-and-ticket-stock` "After the draw", "Before the draw", "No entries"; `list-by-ticket-sale-and-user` "Entry of the user", "Never entered"; `list-entered-by-ticket-sale-and-ticket-stock` "Mixed states", "No candidates"; verify the rdb tests pass against a migrated database

## 3. Use cases

- [x] 3.1 Rename `LotteryEntryUseCase.ListByTicketType` to `ListByTicketSale` and its handler call; move the `list-by-ticket-sale` unit tests' annotations ("Entered entry", "Fan won", "Fan lost", "Never entered"); verify `go test ./internal/usecase/...` and that the existing scenarios of `checkout/start`, `lottery-entry/authorize-card`, `lottery-entry/run-draw` and `ticket-sale/list-own-by-event` still pass

## 4. Adapter (components/adapter/fan/api/rpc/lottery-entry)

- [x] 4.1 Upgrade the generated package to the release of 1.2 and serve `ListByTicketSale` from the lottery entry handler; update the handler tests of "No stock", "Not signed in" and the other scenarios of the fan lottery entry RPC to the new method; verify `make check`
- [x] 4.2 Open the backend PR; verify CI passes, merge, release, and confirm the prod rollout (`kubectl -n backend get deploy` shows the new tag)

## 5. Frontend (fan)

- [x] 5.1 Upgrade the generated package and call `listByTicketSale` in the lottery entry client, read by the lottery entry status screen and `HeldSeatTypeService`; update the functional e2e stubs to `LotteryEntryService/ListByTicketSale`; verify `make check`
- [x] 5.2 Run `e2e/functional/lottery-entry-status.spec.ts` and `seat-types.spec.ts` with Playwright on a local build against stubbed RPCs; verify the fan's entries show Entered, Won and Lost as before
- [x] 5.3 Open the frontend PR, merge and release it right after 4.2's rollout (design D2); verify the fan-web rollout and that a signed-in fan's lottery entry status screen loads in prod

## 6. Close-out

- [x] 6.1 At archive time, edit the usecase diagram in `stories/win-tickets-in-a-lottery`'s Purpose to `LotteryEntryUseCase.ListByTicketSale`; verify `python3 scripts/check-scenario-coverage.py rename-ticket-type-operations` reports every moved scenario covered on main
