## Why

The backend's tests are large and hard to trust because the business rules do not live where the layers say they should. Rules that belong to an entity are written inline in usecases, several times over. The entity methods that state those rules (`Event.CanTransitionTo`, `Order.CanBecomeVoid`, `Checkout.CanBecome`, `ResaleEntry.IsWithdrawable`) have no production caller. As a result, a rule that one table test on the entity could check is instead checked through mock-heavy usecase tests, once per usecase that repeats it. For example, `concert_uc_test.go` sets 200 mock expectations, and `orderUseCase` has 19 dependencies.

The layering also leaks:

- 27 adapter files import infrastructure packages.
- 21 infrastructure files import `internal/adapter/pb`.
- Six RPC handlers read the user repository directly instead of going through a usecase.
- Entity validation errors come in two styles, so usecases attach error codes after the fact. Nine call sites use `apperr.New(code, err.Error())`, which drops the original error. That is a bug: the cause no longer appears in the logs.
- No lint rule bounds function size. An ad-hoc run of funlen, gocognit and cyclop reports 84 findings.

Fixing the tests means fixing these responsibilities first, so this change does both together.

## What Changes

- **Layer dependencies**
  - Adapters stop importing infrastructure, and infrastructure stops importing adapters. Each contract the two sides share moves to a place both may import:
    - the event message contract (payload decoding, `ce_subject`, the redelivery marker);
    - the signed-in caller carried on the request context;
    - the Series image variant key;
    - the prefecture names;
    - the entity-to-`entity/v1` mapping that announcements encode.
  - The webhook token check becomes an interface that the adapter declares.
  - A depguard rule in `.golangci.yml` keeps each dependency pointing inward.
- **Caller resolution**: the six fan RPC handlers that read `UserRepository` resolve the caller through `UserUseCase.ResolveCaller`, as `lottery_entry_handler.go` already does.
- **Domain rules on entities**
  - Each rule that a usecase repeats moves onto the entity that owns it, and the usecases call it. This covers:
    - the 本人確認 (identity check) gate on a sale;
    - the required purchaser details;
    - the deactivated-Organizer guard;
    - the refund of unresold tickets;
    - Settlement split invariants;
    - publish readiness;
    - the deletion-blocker classification;
    - TicketSale windows against event start;
    - reminder quiet hours;
    - "same performance" matching.
  - The entity transition methods that have no caller today are used where their meaning matches the usecase's check.
- **Errors**
  - Entity validation and guard functions return `apperr` errors carrying the code (InvalidArgument or FailedPrecondition), and usecases and repositories pass them through. The codes a client sees do not change.
  - Every `apperr.New(code, err.Error())` becomes a wrap that keeps the cause.
- **Clock**
  - The entity layer stops reading the wall clock. `NewIdentityVerification` and `DiscoveredTicketSale.Validate` take the time from their caller.
  - Usecases read time only through their injected `Clock`.
- **Fan visibility**
  - The rule for what fans may see is owned by the entity: `Event.IsPubliclyVisible`, `Concert.IsVisibleToFans` and `DerivePublishState`.
  - Repository list methods that filter by that rule in SQL say so in their doc comments.
  - For each of those methods, a test proves that the SQL filter returns exactly the rows the entity predicate accepts.
- **Function size**
  - `.golangci.yml` enables funlen (60 lines, 40 statements), gocognit (20) and cyclop (15) for non-test code.
  - Every existing violation is fixed by splitting the function by responsibility.
  - An exclusion is added only after the user agrees to it.
- **Tests follow the code**
  - Each moved rule gets a table test on its entity.
  - Usecase tests keep one case per usecase spec scenario and stub ports with the mockery mocks, not hand-written fakes.

No API, proto, schema or client-visible behaviour changes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. Every rule this change moves is already stated by a spec, and its observable behaviour (outcome and error code) stays the same:

- `components/entity/ticket-sale`: verification requirement and window.
- `components/entity/organizer`: only an active Organizer serves its members.
- `components/entity/event`: what makes two Events the same performance, and public visibility.
- `components/entity/user`: personal details.
- `components/usecase/order/refund`: refund of Tickets still Issued.
- `components/usecase/series/publish`: what must exist before a publish.
- `components/usecase/user/list-deletion-blockers`
- `components/usecase/ticket-sale/scan-due-reminders`: quiet hours.
- `components/usecase/resale-entry/authorize-card`, `components/usecase/lottery-entry/authorize-card` and `components/usecase/checkout/start`: the 本人確認 gate.

The change moves code to match these specs and does not change them, so `.openspec.yaml` sets `skip_specs: true`.

## Impact

- **Code**: `backend` only.
  - `internal/entity`, `internal/usecase`, `internal/adapter/{rpc,event,webhook,pb,linkpreview}` and `internal/infrastructure/{auth,messaging,geo,gcp/storage,database/rdb}`.
  - New shared packages under `pkg/` and `internal/` (see design.md).
  - `.golangci.yml`, and the wiring in `internal/di`.
  - Every function the new lint rules flag.
- **Docs**: backend `AGENTS.md`, which names `internal/adapter/pb` as the home of announcement payloads, and the stale entity comments that say the entity layer returns stdlib errors (`user.go:35`, `user.go:70`, `settlement.go:136`).
- **Not affected**: proto, database schema, frontend, cloud-provisioning, deployed behaviour.
