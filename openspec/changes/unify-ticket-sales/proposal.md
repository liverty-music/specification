## Why

A ticket sale is modelled three times today: the discovered `SalesPhase` (one sale for a whole Series), the organizer's `LotterySalesPhase` (one lottery for one event) and the first-come `TicketSale` that `first-come-ticket-sales` adds (one sale for one event). They share the method, the window and the result time, but they cannot express a real Japanese tour: one fan-club presale and one general sale, each covering several dates. A second phase on the same event is also accepted silently. The first-come `TicketSale` is not released yet, and the lottery has no production users. This is the cheapest moment to settle one sale model before the pilot Organizer sells its first presale.

The same review found names that confuse readers. `TicketApplication` sits in `lottery_application.proto`. The same User is called applicant, buyer and holder. "Seller" means the Organizer in one place and the reselling fan in another. A fan's name and phone number are stored up to four times (application, checkout, User, every Ticket).

## What Changes

- **New `TicketSale`**: one sale opportunity (受付) for some or all events of a Series. It has a name such as "ファンクラブ先行", a method, a window, an identity-verification requirement and a drawn time. This change implements the method `Lottery`. `first-come-ticket-sales` adds `FirstCome` on top of it. Discovered sales move into this entity in a later change.
- **New `TicketType`**: what a sale offers for one event. It has a price (税込, tax-inclusive), a quantity and a per-account limit. A sale has at most one ticket type per event.
- **An event can have several sales.** The windows of two sales that share an event must not overlap. A fan's per-account limit counts the tickets the fan already holds for the event, so a presale winner cannot add a full second allowance in the general sale.
- **BREAKING** `LotterySalesPhase` is removed. Its window, capacity, group size, price, verification requirement and drawn time move to `TicketSale` and `TicketType`.
- **BREAKING** `TicketApplication` is renamed `LotteryEntry`. A fan enters one ticket type. The state `Applied` becomes `Entered`. The usecase methods become `Enter`, `WithdrawEntry`, `GetMyEntry`, `DrawDueSales`.
- **BREAKING** A fan's full name and phone number are stored only on the `User`. A lottery entry no longer stores them. A Ticket shows the User's current name and phone on its face. The fan can change them at any time.
- **BREAKING** Every reference to the User in a ticketing record is named `user`: Order `buyer`, Ticket `holder` and the applicant become `user`. Order and Ticket operations are renamed to match.
- **BREAKING** The organizer lottery RPCs (`Configure`, `GetStatus`, `SetVerificationRequirement`) are replaced by an organizer ticket sale service. The fan lottery RPCs take a ticket type instead of a phase.
- The organizer console's lottery editor creates a lottery `TicketSale` for one event.
- Outside the spec deltas, `first-come-ticket-sales` is updated to build on this model. The update covers the following:
  - `Reservation` becomes `Checkout`.
  - The Organizer's seller details become plain Organizer fields (legal name, representative name, business address, business phone number, contact email). The word "seller" leaves code identifiers.
  - The holder name and phone leave `Checkout`.

## Capabilities

### New Capabilities

- `components/entity/ticket-sale`: the sale opportunity (受付), its window, method, verification requirement and drawn state
- `components/entity/ticket-sale/create`: stores a sale together with its ticket types
- `components/entity/ticket-sale/get`: reads one sale with its ticket types
- `components/entity/ticket-sale/list-by-event`: lists the sales that offer a ticket type for one event
- `components/entity/ticket-sale/list-due-for-draw`: lists the lottery sales whose window has closed and that are not drawn
- `components/entity/ticket-sale/update-verification-requirement`: changes a sale's verification requirement
- `components/entity/ticket-type`: what a sale offers for one event: price, quantity and per-account limit
- `components/entity/ticket-type/get`: reads one ticket type with its sale
- `components/entity/lottery-entry`: one fan's entry into a lottery ticket type
- `components/entity/lottery-entry/create`, `get`, `get-by-ticket-type-and-user`, `list-entered-for-ticket-type`, `get-ticket-type-stats`, `run-lottery-draw`, `persist-draw-outcome`, `update-state`, `create-authorization`, `verify-authorization`, `capture-authorization`, `cancel-authorization`: the operations of `TicketApplication`, renamed and keyed by ticket type
- `components/entity/order/get-by-lottery-entry-id`, `components/entity/order/list-lottery-entry-ids-awaiting-issuance`, `components/entity/order/list-by-user`: the renamed Order operations
- `components/entity/ticket/list-by-user`, `components/entity/ticket/list-by-user-and-event`: the renamed Ticket operations
- `components/entity/user/update-personal-details`: stores a User's full name and phone number
- `components/usecase/ticket-sale/create`: an Organizer creates a lottery sale for its published events
- `components/usecase/ticket-sale/list-own-by-event`: an Organizer reads the sales of one event with their tallies
- `components/usecase/ticket-sale/set-verification-requirement`: an Organizer changes a sale's verification requirement
- `components/usecase/lottery-entry/enter`, `create-authorization`, `draw-due-sales`, `run-draw`, `get-my-entry`, `get-result`, `withdraw-entry`: the lottery usecase methods, keyed by ticket type
- `components/adapter/organizer/api/rpc/ticket-sale`: the organizer ticket sale service boundary

### Modified Capabilities

- `components/entity/order` (Purpose): `buyer` becomes `user`, `application` becomes `lottery entry`
- `components/entity/ticket` (Purpose and requirement): `holder` becomes `user`, the holder full name and phone attributes leave, and the covered-ticket face reads the User's name and phone
- `components/entity/user` (Purpose and requirement): gains full name and phone number with their validation
- `components/usecase/order/issue-from-captured-win`: issues from a won lottery entry and its ticket type, binds tickets to the user, and copies no name or phone
- `components/usecase/order/issue-due-wins`: lists won lottery entries without an Order
- `components/usecase/order/get-order`: the caller is the Order's user
- `components/usecase/ticket/get-my-tickets`: lists by user
- `components/adapter/fan/api/rpc/lottery`: Enter, Withdraw, GetEntry and GetResult take a ticket type, and the identity rule is the User's
- `components/infrastructure/fan/web/route/lottery-apply`: the screen enters a ticket type and prefills the fan's saved name and phone
- `components/infrastructure/organizer/web/route/lottery-phase-editor`: the editor creates a named lottery sale for one event
- `stories/win-tickets-in-a-lottery`: the story runs on a lottery ticket sale
- `components/entity/concert/delete-and-suppress`, `components/entity/organizer/delete`, `components/entity/user/delete`: the deleted or kept records are named TicketSale, TicketType and LotteryEntry, and a deleted User takes its full name and phone number with it
- `components/usecase/user/delete`: reads `Ticket.ListByUser` and `Order.ListByUser`

### Removed Capabilities

These are written as REMOVED deltas:
- `components/entity/lottery-sales-phase` and its operations `create`, `get`, `list-phases-due-for-draw` and `update-verification-requirement`
- `components/usecase/lottery-sales-phase/*`
- `components/entity/ticket-application` and its 12 operations
- `components/usecase/ticket-application/*`
- `components/entity/order/get-by-application-id`, `components/entity/order/list-application-ids-awaiting-issuance`, `components/entity/order/list-by-buyer`
- `components/entity/ticket/list-by-holder`
- `components/adapter/organizer/api/rpc/lottery`

Entity operations that this change relies on and does not change: `Event.IsEventPublished`, `Event.Get`, `Event.GetOrganizerID`, `VerifiedIdentity.GetByUserID`, `Order.GetCapturedPayment`, `Order.Issue`, `TicketJourney.Upsert`, `User.GetByExternalID`, `OrganizerUseCase.ResolveCaller`.

## Impact

- **specification**: entity protos `ticket_sale.proto` (rewritten), new `ticket_type.proto` and `lottery_entry.proto` (from `lottery_application.proto`), `user.proto`, `order.proto`, `ticket.proto`, `organizer.proto` (seller details flattened); RPC protos `rpc/organizer/ticket_sale/v1` (rewritten), `rpc/organizer/lottery/v1` (removed), `rpc/lottery/v1` (fan). These are breaking changes on BSR. No client outside this product consumes them.
- **backend**:
  - Migration: `lottery_sales_phases` → `ticket_sales` + `ticket_types`; `ticket_applications` → `lottery_entries`; `applicant_*` and `tickets.holder_*` columns dropped after their values move to `users`; `orders.buyer_id` / `tickets.holder_id` renamed `user_id`.
  - Lottery usecase, draw and issuance code.
  - Organizer handlers.
  - The unmerged `worktree-first-come-ticket-sales` branch rebases onto the new tables.
- **frontend**:
  - Fan lottery entry screen (route params, prefill).
  - Organizer lottery editor and lottery status screens.
  - Generated clients.
- **Other in-flight changes**:
  - `ticket-wallet-and-checkin` and `identity-ekyc-jpki` modify the lottery specs this change removes. They are archived first, or their deltas move onto the new specs (design.md "Sequencing").
  - `first-come-ticket-sales` is updated as described above.
  - `official-resale` renames `ResaleListing.seller` to `holder`.
- **Production data**: only test data exists. The lottery has no production users (`CLAUDE.md`, current operating state). Row counts are checked read-only before the migration.
