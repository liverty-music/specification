## Why

A fan who enters a lottery with a name or phone number the server refuses is told that they asked for too many tickets (frontend#1077). The fan changes the count, which was never the problem, and gets the same error again. The cause is on both sides: LotteryEntryUseCase.AuthorizeCard and ResaleEntryUseCase.AuthorizeCard answer InvalidArgument both for a count above the event's per-account limit and for missing or malformed personal details, and the screens read every InvalidArgument as a count problem.

The per-account limit is the event's data, set by its Organizer, so a count above it is a failed precondition, not a bad argument. gRPC defines INVALID_ARGUMENT as "arguments that are problematic regardless of the state of the system" and FAILED_PRECONDITION as "the system is not in a state required for the operation's execution". The related case, the fan's held tickets plus the count over the limit, is already FailedPrecondition. Splitting the codes this way leaves InvalidArgument with one meaning the screens can act on: fix the name or phone number.

## What Changes

- CheckoutUseCase.Start, LotteryEntryUseCase.AuthorizeCard and ResaleEntryUseCase.AuthorizeCard fail with **FailedPrecondition** (was InvalidArgument) when the count is above the event's per-account limit. A count below 1 and missing or malformed personal details stay InvalidArgument. A count above 10, the highest limit any event can have, is still refused at the RPC boundary with InvalidArgument, as before.
- ResaleEntryUseCase.AuthorizeCard's spec states the count and personal details failures, which it does today but the spec never said.
- The checkout, lottery entry and resale entry screens send only a count from 1 to the event's per-account limit, and explain a refused card authorization by its code: InvalidArgument takes the fan to the personal details step with a message about the name or phone number; FailedPrecondition keeps the existing reasons (window closed, already entered, another seat type, per-account limit).
- The proto comments of CheckoutService.Start, LotteryEntryService.AuthorizeCard and ResaleEntryService.AuthorizeCard document the new codes.
- **BREAKING** for a client that reads InvalidArgument from these three calls as "count above the limit". The only client is this frontend, which ships first (see design.md, Rollout order).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/usecase/checkout/start`: a count above the per-account limit fails with FailedPrecondition. Purpose (sequence diagram) edited directly.
- `components/usecase/lottery-entry/authorize-card`: the same, and InvalidArgument is left for a count below 1 or the personal details. Purpose (sequence diagram) edited directly.
- `components/usecase/resale-entry/authorize-card`: states the count and personal details failures with the new split.
- `components/infrastructure/fan/web/route/checkout`: the count sent is checked against the per-account limit, and an AuthorizeCard InvalidArgument returns the fan to the personal details.
- `components/infrastructure/fan/web/route/new-lottery-entry`: the same for LotteryEntryService.AuthorizeCard, with the existing refusal reasons for FailedPrecondition.
- `components/infrastructure/fan/web/route/new-resale-entry`: the same for ResaleEntryService.AuthorizeCard.

The entity operations these usecases call (Event's per-account limit rule, Order.GetHeldForEvent, Checkout.GetOrCreateHeld, LotteryEntry.Create, ResaleEntry.Create, User.UpdatePersonalDetails) are unchanged: they already fail with FailedPrecondition when the application does not fit the event, and the count check that changes belongs to the usecases. The RPC boundary specs (`components/adapter/fan/api/rpc/{checkout,lottery-entry,resale-entry}`) are unchanged: their InvalidArgument cases are fixed-range checks of the request.

## Impact

- specification: proto comments of `rpc/checkout/v1`, `rpc/lottery_entry/v1`, `rpc/resale_entry/v1` (comments only; no field or type change).
- backend: `internal/entity/order.go` (`ValidateTicketCount`), the `# Possible errors` of `internal/usecase/checkout_uc.go`, `lottery_entry_uc.go`, `resale_entry_uc.go`, and their tests.
- frontend: `src/routes/checkout/checkout-route.ts`, `src/routes/new-lottery-entry/new-lottery-entry-route.ts`, `src/routes/new-resale-entry/new-resale-entry-route.ts`, new i18n text in `src/locales/{ja,en}/translation.json`, and their tests.
- Deploy order: frontend before backend, since each merge deploys to production.
