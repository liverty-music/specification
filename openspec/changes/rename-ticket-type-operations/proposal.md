## Why

`remodel-ticket-sales` replaced TicketType with SeatType and TicketStock, but four lottery entry operations and one fan RPC kept their TicketType names because a spec path is not moved inside a change (its design D11). They now take a TicketSale and a TicketStock, so the names tell a reader the wrong input and break the rule that a method's name says what it narrows by (`rpc-design` skill, "A Key in a ListBy name is always a field in the request").

## What Changes

- Rename the entity operations of LotteryEntry, keeping their behaviour:
  - `GetStatsByTicketType(sale, stock)` → `GetStatsBySaleAndStock`
  - `ListByTicketTypeAndUser(sale, user)` → `ListBySaleAndUser`
  - `ListUndrawnForTicketType(sale, stock)` → `ListEnteredBySaleAndStock` (it returns the Entered entries)
- Rename the use case `LotteryEntryUseCase.ListByTicketType(sale, user)` → `ListBySale`.
- **BREAKING** Rename the fan RPC `LotteryEntryService.ListByTicketType` → `ListBySale`, with `ListBySaleRequest` / `ListBySaleResponse` (fields unchanged: `ticket_sale_id`; `lottery_entries`, `orders`). The frontend lottery entry status screen moves to the new RPC in the same release.
- Move each spec to the path of its new name; no requirement or scenario changes.

## Capabilities

### New Capabilities

- `components/entity/lottery-entry/get-stats-by-sale-and-stock`: the requirements of `get-stats-by-ticket-type`, unchanged.
- `components/entity/lottery-entry/list-by-sale-and-user`: the requirements of `list-by-ticket-type-and-user`, unchanged.
- `components/entity/lottery-entry/list-entered-by-sale-and-stock`: the requirements of `list-undrawn-for-ticket-type`, unchanged.
- `components/usecase/lottery-entry/list-by-sale`: the requirements of `list-by-ticket-type`, unchanged.

### Modified Capabilities

- `components/entity/lottery-entry/get-stats-by-ticket-type`: removed, moved to `get-stats-by-sale-and-stock`.
- `components/entity/lottery-entry/list-by-ticket-type-and-user`: removed, moved to `list-by-sale-and-user`.
- `components/entity/lottery-entry/list-undrawn-for-ticket-type`: removed, moved to `list-entered-by-sale-and-stock`.
- `components/usecase/lottery-entry/list-by-ticket-type`: removed, moved to `list-by-sale`.
- `components/usecase/checkout/start`, `components/usecase/lottery-entry/authorize-card`, `components/usecase/lottery-entry/run-draw`, `components/usecase/ticket-sale/list-own-by-event`: name the renamed operations.
- `components/adapter/fan/api/rpc/lottery-entry`: names `ListBySale` instead of `ListByTicketType`.
- `stories/win-tickets-in-a-lottery`: names `LotteryEntryUseCase.ListBySale`; its usecase diagram (Purpose) is edited in the main spec.

## Impact

- specification: `proto/liverty_music/rpc/lottery_entry/v1/lottery_entry_service.proto` (breaking rename, `buf skip breaking`), and the spec moves above.
- backend: `internal/entity/lottery_entry.go`, `internal/usecase/lottery_entry_uc.go`, `checkout_uc.go`, `ticket_sale_uc.go`, `internal/infrastructure/database/rdb/lottery_entry_repo.go`, the lottery entry handler, mocks and tests.
- frontend: the lottery entry client, the lottery entry status screen and the held-seat-type read that call `ListBySale`, and the functional e2e stubs.
- No database change; no data migration.
