## Why

A TicketType mixes three things: what one TicketSale offers for one event, the price and size of that offer, and the first-come stock with its resale. The per-account limit sits on it too, so a presale and a general sale can each set their own limit and the spec needs a "top up to a higher limit" rule. The model has no notion of a seat type (席種), so an event cannot sell S席 and A席 at different prices, and an organizer who wants that would have to repeat the same seat type in every sale. The rules grew around these mixes: a price that may change only while nothing is sold or held, a quantity that may be raised after a sell-out, and a resale open time that is set once and never cleared. The count of tickets an account already holds is also defined twice, differently: a first-come checkout counts its own ticket type's committed checkouts, and a lottery entry counts only issued tickets. A fan can therefore exceed the limit when a won presale entry is not yet issued as the general sale opens. This change replaces TicketType with a model that has one place for each fact.

## What Changes

- **BREAKING** New `SeatType` of a Series: a name and a price, fixed at creation. A 2-day run at one venue and a national tour share the Series' seat types; a different price is a different seat type.
- **BREAKING** New `TicketStock`: one seat type for one event, with the quantity of tickets, fixed at creation. Every sale of the event sells from the same stock. More tickets are a new seat type and stock, as 注釈付き指定席 or 機材開放席 are released.
- **BREAKING** `TicketSale` names the events it sells and sells every TicketStock of those events. It no longer offers TicketTypes. Sales of one event still never overlap.
- **BREAKING** `Event` carries the per-account limit: 1 to 10 (the most tickets one AdmissionCode presents), 4 when not given. It counts every sale, every seat type and resale of the event. The per-sale limit and the top-up rule go.
- **BREAKING** One account holds tickets of only one seat type for an event, since tickets are not bought on behalf of others.
- **BREAKING** `Order` is created when the fan applies, not after payment: it names the account, the TicketStock, the ticket count, the referral code and the card authorization, and goes Pending to Paid to Refunded, or Pending to Void when it is never paid (a Lost entry, an expired or released checkout). The unused Failed status goes. `LotteryEntry` and `Checkout` keep only what differs: the sale, their own lifecycle, the draw position, the hold expiry and the commit time. `Checkout.amount`, `Checkout.resale` and `Checkout.SetReferralCode` go; the referral code is fixed when the Order is created.
- The tickets an account holds for an event are defined once, on Order: the issued Tickets of its Paid Orders plus the ticket counts of its Pending Orders. The first-come checkout and the lottery entry both check this count.
- A fan enters a lottery sale at most once for each event, so a tour presale can still be entered for several dates.
- **BREAKING** A Checkout only buys a FirstCome sale's stock: the resale Checkout, its listing holds and its resale hold expiry go. A ResaleListing belongs to a TicketStock and can be made while the stock is sold out and the resale deadline has not passed, and withdrawn while it is open; the stored resale open time goes. Any Ticket of a sold-out stock can be listed, whether bought first come or won in a lottery. Buying a listed ticket becomes a daily lottery in the change `resell-tickets-by-lottery`; until then listings are made but not bought.
- A TicketStock can be deleted while no Order other than a Void one names it, so an abandoned checkout does not freeze a mistaken quantity; a SeatType can be deleted once no TicketStock uses it.
- `Event`'s per-account limit is set while the event is DRAFT and fixed once it is PUBLISHED.
- **BREAKING** `TicketSale` loses the draw time and the lottery result time: a closed lottery is drawn once none of its entries is Entered. The `RESULT_DAY` reminder goes with the result time; the remaining stages are `APPLY_OPEN` and `APPLY_CLOSE_24H`. Every sale, discovered ones too, has a name and an end time; discovery skips a sale whose pages state neither, such as a first-come sale "until sold out".
- A first-come checkout waits while an earlier lottery of the event has closed and is not drawn yet, so a sale opening at a lottery's close cannot take the lottery's tickets.
- Removed: TicketType and its operations, the price-change rule, the quantity-raise rule, the per-sale per-account limit.
- Existing data of Organizer sales is deleted before the new tables are created (design "Migration Plan"); discovered sales are kept, except those without an end time, and are named by method until rediscovered.
- The unstarted changes `make-lottery-draw-durable` and `unify-order-issuance` were written for TicketType and an Order that exists only after capture; they are rewritten on this model alongside this change, with `resell-tickets-by-lottery` (design D9).

## Capabilities

### New Capabilities

- `components/entity/seat-type`: a Series' seat type, its name and price.
- `components/entity/seat-type/create`, `components/entity/seat-type/delete`, `components/entity/seat-type/get`, `components/entity/seat-type/list-by-series`: create a seat type; delete one no TicketStock uses; read one; list a Series' seat types.
- `components/entity/ticket-stock`: one seat type for one event, its quantity, remaining tickets, sold-out state and whether resale listing is open.
- `components/entity/ticket-stock/create`, `components/entity/ticket-stock/delete`, `components/entity/ticket-stock/get`, `components/entity/ticket-stock/list-by-event`: create a stock; delete one no live Order names; read one with its counts at a time; list an event's stocks.
- `components/entity/order/get-held-for-event`: the tickets an account holds for an event and their seat type.
- `components/usecase/seat-type/create`, `components/usecase/seat-type/delete`, `components/usecase/seat-type/list-by-series`, `components/usecase/ticket-stock/create`, `components/usecase/ticket-stock/delete`, `components/usecase/ticket-stock/list-by-event`: the organizer's operations.
- `components/adapter/organizer/api/rpc/seat-type`, `components/adapter/organizer/api/rpc/ticket-stock`: the organizer gate of those RPCs.

### Modified Capabilities

Entities (Purpose and requirements):
- `components/entity/event`: the per-account limit.
- `components/entity/series/create-draft`, `components/entity/series/update`: store each event's per-account limit; fixed once the event is PUBLISHED.
- `components/entity/ticket-sale` and its operations `create`, `get`, `list-by-event`, `list-due-for-draw`, `list-with-pending-milestones`, `search-published-sales`, `set-window`, `set-verification-requirement`, `upsert-discovered`: the events it sells instead of TicketTypes; no draw time or lottery result time; a name and an end time on every sale.
- `components/entity/ticket-sale-reminder` and its operation `already-sent`: the `RESULT_DAY` stage is removed.
- `components/entity/order` and its operations `get-event-id`, `get-by-checkout-id`, `get-by-lottery-entry-id`, `issue`, `list-by-event`, `list-by-user`, `list-lottery-entry-ids-awaiting-issuance`, `list-referral-stats-by-event`: created at application, Pending and Void (Failed goes), the common attributes; issuance makes a Pending Order Paid; resale Orders leave with the resale Checkout.
- `components/entity/lottery-entry` and its operations `create`, `get-by-card-authorization-id`, `get-stats-by-ticket-type`, `list-by-ticket-type-and-user`, `list-by-user`, `list-undrawn-for-ticket-type`, `persist-draw-outcome`: names its Order and sale; one entry per sale and event; the Pending Order is stored with the entry and voided when it loses.
- `components/entity/checkout` and its operations `commit`, `get-by-card-authorization-id`, `get-or-create-held`, `list-by-user`, `list-due`, `record-card-authorization-release`, `release`, `revert-commit`, `set-card-authorization`: names its Order and always a FirstCome sale; no amount, resale flag, resale hold or referral code; the Pending Order is stored with the Checkout and voided when it ends unpaid.
- `components/entity/card-authorization/create`, `components/entity/card-authorization/get` and `components/entity/card-authorization` (Purpose): carry the TicketStock, the sale, the count and the referral code.
- `components/entity/resale-listing` (Purpose and requirements), `components/entity/resale-listing/create`, `components/entity/resale-listing/withdraw`: belongs to the TicketStock; any Ticket of a sold-out stock, first come or lottery; no Checkout holds a listing, so a listing is withdrawable while open.
- `components/entity/referral` (Purpose): the referral code is the Order's.
- `components/entity/concert/delete-and-suppress`, `components/entity/organizer/delete`: delete seat types and stocks instead of TicketTypes; no Failed Orders.

Usecases:
- `components/usecase/series/create`, `update`: each event's per-account limit.
- `components/usecase/ticket-sale/create`, `discover-for-artist`, `set-window`, `list-by-event`, `list-own-by-event`, `scan-due-reminders`.
- `components/usecase/checkout/start`, `release-expired`.
- `components/usecase/lottery-entry/authorize-card`, `confirm`, `list-by-ticket-type`, `run-draw`.
- `components/usecase/order/issue-from-captured-win`, `issue-from-checkout`.
- `components/usecase/resale-listing/create`, `withdraw`.

Adapters and screens:
- `components/adapter/fan/api/rpc/checkout`, `lottery-entry`, `ticket-sale`; `components/adapter/organizer/api/rpc/ticket-sale`.
- `components/infrastructure/fan/web/route/event`, `checkout`, `lottery-entry`, `tickets`; `components/infrastructure/fan/web/global/legal-document`.
- `components/infrastructure/organizer/web/route/concert`, `concert-editor`, `event`, `ticket-sale-editor`, `guide`; `components/infrastructure/organizer/web/global/i18n`.

Stories (Purpose and requirements):
- `stories/resell-a-ticket`: listing only; buying arrives with `resell-tickets-by-lottery`.
- `stories/buy-tickets-first-come`, `stories/win-tickets-in-a-lottery`, `stories/attribute-a-purchase-to-a-referral-link`, `stories/run-an-event-from-the-organizer-console`.

Removed:
- `components/entity/ticket-type`, `components/entity/ticket-type/get`, `components/entity/ticket-type/update`, `components/usecase/ticket-type/update`, `components/adapter/organizer/api/rpc/ticket-type`, `components/entity/checkout/set-referral-code`.

## Impact

- **proto**: new SeatType and TicketStock messages and organizer RPCs; TicketType, its RPCs and fields go; Order, Checkout, LotteryEntry and TicketSale messages change. A breaking schema release.
- **backend**: a migration that creates `seat_types` and `ticket_stocks`, moves the per-account limit to `events`, moves the common columns to `orders` and drops `ticket_types`; entities, repositories, usecases and handlers of ticket sales, checkouts, lottery entries, orders and resale.
- **frontend**: the organizer console gains seat types (Series) and stocks (event) and loses the per-sale limit; the fan event page, checkout and lottery entry choose a seat type.
- **analytics**: readers of `orders` must count Paid Orders only, since Pending and Void Orders now exist.
- **data**: every record of Organizer sales in prod is deleted by the migration, after a read-only pre-check that nothing is open, held for payout or unrefunded.
- **specification**: `make-lottery-draw-durable`, `unify-order-issuance` and `resell-tickets-by-lottery` are written on this model alongside this change.
