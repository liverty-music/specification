## Context

See proposal.md - Why. `remodel-ticket-sales` (design D11) left four operation names and one fan RPC named after TicketType while they take a TicketSale and a TicketStock. On `main`:

- backend: `entity.LotteryEntryRepository.GetStatsByTicketType`, `ListByTicketTypeAndUser`, `ListUndrawnForTicketType` (`internal/entity/lottery_entry.go`, realized by `internal/infrastructure/database/rdb/lottery_entry_repo.go`), called by `checkout_uc.go` (the draw guard), `lottery_entry_uc.go` (AuthorizeCard, Confirm, RunDraw, ListByTicketType) and `ticket_sale_uc.go` (ListOwnByEvent); `usecase.LotteryEntryUseCase.ListByTicketType`, served by `internal/adapter/rpc/lottery_entry_handler.go`; mockery mocks of both interfaces.
- frontend: `src/adapter/rpc/client/lottery-entry-client.ts` calls `listByTicketType`, read by the lottery entry status screen and `HeldSeatTypeService`; two functional e2e specs stub `LotteryEntryService/ListByTicketType`.
- Tests on `main` are annotated `@spec components/entity/lottery-entry/get-stats-by-ticket-type "…"` and the like.

## Goals / Non-Goals

**Goals:**
- Every operation, method, RPC and spec path says what it takes; behaviour, data and error codes stay as they are.

**Non-Goals:**
- No change of what any operation returns, no database change.
- The scenario name "Entries for two ticket types" in `entity/lottery-entry/list-by-user` stays: it is an unrelated scenario name, and renaming it moves its test annotation for no reader's benefit.

## Decisions

### D1 — Names

| Before | After | Why |
|---|---|---|
| `LotteryEntry.GetStatsByTicketType(sale, stock)` | `GetStatsByTicketSaleAndTicketStock` | Names both inputs. |
| `LotteryEntry.ListByTicketTypeAndUser(sale, user)` | `ListByTicketSaleAndUser` | Names both inputs. |
| `LotteryEntry.ListUndrawnForTicketType(sale, stock)` | `ListEnteredByTicketSaleAndTicketStock` | Returns the Entered entries; "undrawn" restated the state indirectly. |
| `LotteryEntryUseCase.ListByTicketType(sale, caller)` | `ListByTicketSale` | The caller is never named (`rpc-design` skill). |
| RPC `LotteryEntryService.ListByTicketType` | `ListByTicketSale` (`ListByTicketSaleRequest`, `ListByTicketSaleResponse`) | `ListBy<Key>` where the Key is the request's `ticket_sale_id`. |

Field numbers and names inside the request and response stay (`ticket_sale_id = 2`; `lottery_entries`, `orders`), so only the method and message names change on the wire path.

### D2 — A breaking rename, released backend then frontend

The proto renames the RPC in one release (`buf skip breaking`), the backend serves only `ListByTicketSale`, and the frontend calls only `ListByTicketSale`. Between the backend rollout and the frontend rollout the fan's lottery entry status screen and the held-seat-type read fail with Unimplemented.

- Rejected — serve both names for one release, then drop the old: two proto releases and two backend deploys for a window of minutes. The product has no users besides the owner and one tester, and the workspace allows trading availability for cost.

### D3 — Spec moves

Each renamed operation's spec moves to the path of its new name: the change ADDs its requirements unchanged at the new path and REMOVEs them at the old one (`retire_capabilities: true`). Specs that name these operations (checkout start, authorize card, run draw, list own by event, the fan lottery entry RPC, the win-tickets story) are MODIFIED only in those names. The story's usecase diagram is in its Purpose and is edited directly in the main spec at archive time.

## Risks / Trade-offs

- [Unimplemented on the fan status screen between the backend and the frontend rollouts] → Cut the frontend release right after the backend rollout is confirmed (D2).
- [A test annotation left on the old spec path] → The scenario coverage check on the archive PR fails until every moved scenario's test carries the new path.

## Migration Plan

1. Merge and release the proto (specification), wait for BSR generation.
2. Backend: rename, upgrade the generated package, release, confirm the rollout.
3. Frontend: upgrade the generated package, call `ListByTicketSale`, release right after step 2, confirm the rollout.
Rollback: revert the frontend and backend releases together; no data changes.
