## Context

See proposal.md for why. Today `ticket_types` (migration `20261011000000_unify_ticket_sales`) holds one row per sale and event with `price`, `quantity`, `per_account_limit`, `sold_count` and `resale_open_at`. A FirstCome checkout locks that row, checks the remaining tickets and the per-account limit, and raises `sold_count` on commit. An Order is created only after the payment is captured, from a won LotteryEntry or a Committed Checkout. LotteryEntry and Checkout each carry the user, the ticket type, the ticket count, the card authorization and the referral code.

The two unstarted changes `make-lottery-draw-durable` (0/21 tasks) and `unify-order-issuance` (0/13 tasks) had no branches or PRs. Their earlier texts (specification history at c2ee7fc0 and 63ce0621) were written for TicketType and an Order created after capture; both are rewritten on this model as changes of their own (D9). Official resale is bought through a first-come resale Checkout today; this change takes resale out of Checkout and the change `resell-tickets-by-lottery` makes the purchase a lottery.

## Goals / Non-Goals

**Goals:**

- One place for each fact: price on SeatType, quantity on TicketStock, the per-account limit on Event, the fan's application on Order.
- One definition of the tickets an account holds for an event, used by every path that creates an Order.

**Non-Goals:**

- Seat maps and assigned seats (`seat-map-assignment` in the roadmap). A SeatType is a 席種 such as S席 or オールスタンディング; Tickets still name no seat.
- A cap on how many tickets one sale may sell from a stock, or a sale that sells only some seat types of its events. Neither need has been seen; both can be added to TicketSale later without changing TicketStock.
- Reusable sets of seat types, or copying seat types between events.
- Changing a price or a quantity after creation. A mistake is fixed by deleting and recreating the TicketStock (and its SeatType) while no Order other than a Void one names it (D8).
- The durable lottery draw, the single issuance path and buying listed tickets. They are changes of their own (D9).
- How many tickets each sale sold. Every sale of an event sells from the same TicketStocks, so the organizer console shows each stock's sold and held counts, not a per-sale breakdown; Orders know their sale through their LotteryEntry or Checkout, so the breakdown can be added when a need is seen.

## Decisions

### D1 — SeatType belongs to a Series, TicketStock joins it to an event

`seat_types (id, series_id, name, price)` and `ticket_stocks (id, event_id, seat_type_id, quantity)` with a unique index on `(event_id, seat_type_id)`. Creating a TicketStock checks that the event and the seat type belong to the same Series; both are fixed at creation, so the check needs no lock.

- Rejected — SeatType per event: a 2-day run at one venue would define S席 twice.
- Rejected — quantity per sale (an allocation of a stock to each sale): the reason the industry splits stock per sale is that a fan club and several playguides are different companies. Here one Organizer runs every sale on one platform, and a presale that sells out simply means no general sale.

### D2 — TicketSale names its events

`ticket_sale_events (ticket_sale_id, event_id)` replaces the events implied by `ticket_types`. A sale sells every TicketStock of its events, including a stock created while the sale runs. `TicketSale.Create` refuses an event that has no TicketStock yet, so a sale always has something to sell. A discovered sale names no events, as today it offers no TicketType. The overlap check of `TicketSale.Create` and `SetWindow` reads the sales of each named event as it reads them through TicketTypes today.

- Rejected — the sale names TicketStocks: the events would be derived from the stocks, and an organizer would pick seat types per sale with no seen need.

### D3 — Order is created when the fan applies

`orders` gains `ticket_stock_id`, `ticket_count`, `referral_code` and `card_authorization_id`, and its payment columns (`provider payment ID`, `pay time`, card details) become empty until Paid. Status becomes Pending, Paid, Refunded or Void. Today's `OrderStatusFailed` is dropped: no code path sets it (`internal/entity/order.go` declares it, `event_removal.go` and the RPC mapper only read it), because issuance retries until it succeeds instead of refunding. `lottery_entries` and `checkouts` drop `user_id`, `ticket_type_id`, `ticket_count`, `card_authorization_id` and `referral_code` and gain `order_id` (unique). `checkouts` drops `amount` and `resale`, and `ticket_sale_id` becomes required: a Checkout only buys a FirstCome sale's stock.

There is no separate `Order.Create`: the operations that already check and store an application store its Pending Order in the same transaction.

- `LotteryEntry.Create` (called by `LotteryEntryUseCase.Confirm`) stores the Pending Order and the Entered LotteryEntry. The card authorization opened by `AuthorizeCard` carries the sale, TicketStock, ticket count and referral code, so Confirm can build the Order from it before the entry exists.
- `Checkout.GetOrCreateHeld` (called by `CheckoutUseCase.Start`) stores the Pending Order and the Held Checkout, and makes the Order of the fan's replaced holding Checkout Void.
- `LotteryEntry.PersistDrawOutcome` makes the Orders of Lost entries Void; `Checkout.Release` (the expiry sweep) and `Checkout.RevertCommit` make the Checkout's Order Void, each in the same transaction as their own state change. No usecase voids an Order on its own, so there is no `Order.Void` operation.
- Issuance makes the Order Paid and fills the payment columns instead of inserting the row.

The Order's amount is the seat type's price times the ticket count, which never changes, so it is stored once on the Order when it is created.

- Rejected — keep Order post-payment and the common columns on both sources: two copies of the same five attributes and two definitions of the tickets held.

### D4 — The tickets an account holds for an event

The count is the issued Tickets of the account's Paid Orders for the event plus the ticket counts of its Pending Orders for the event. Void and Refunded Orders do not count, and a Paid Order whose Tickets were all resold counts 0 and names no SeatType. A Pending Order of an Entered lottery entry counts: sales of one event never overlap and a fan enters a sale once for each event, so a pending entry is the only way the fan can still receive tickets from another sale. The seat type rule reads the same rows: every Paid or Pending Order of the account for the event names the same SeatType. `Order.GetHeldForEvent` can leave out one Order: `CheckoutUseCase.Start` leaves out the Order of the fan's own holding Checkout, which the new application resumes or replaces.

Locking: the check is made where the Order is stored. `LotteryEntry.Create` and `Checkout.GetOrCreateHeld` first lock the fan's `users` row with `SELECT ... FOR UPDATE` inside their transaction, then read the count and the seat type, and fail with FailedPrecondition when the application no longer fits; otherwise they insert the Order. The earlier check in `AuthorizeCard`, `Confirm` and `Start` is advisory: it spares the fan a card authentication that would be released. Two applications by one fan, for example from two tabs on two stocks of one event, are serialized; applications by different fans do not wait on each other.

- Rejected — lock the `events` row: every fan buying for a popular event would wait on one row.
- Rejected — an advisory lock on (user, event): one more mechanism for the same effect as the row lock.

### D5 — Stock counts are aggregated under the stock row lock

The sold and held counts of a TicketStock are read from its Orders (`components/entity/ticket-stock`): sold is the ticket counts of Paid and Refunded Orders and of Pending Orders whose Checkout is Committed or whose LotteryEntry is Won; held is the ticket counts of Pending Orders whose Checkout is holding. Void Orders count in neither. No counter column is kept: today's `sold_count` is dropped with `ticket_types`.

Lock discipline: every path that changes a stock's tickets takes the `ticket_stocks` row lock (`SELECT ... FOR UPDATE`) first and reads the counts after it, in the same transaction:

| path | operation | changes |
|------|-----------|---------|
| hold | `Checkout.GetOrCreateHeld` | adds a holding Checkout, releases the fan's previous one |
| commit | `Checkout.Commit` | moves a hold to sold |
| revert | `Checkout.RevertCommit` | gives committed tickets back |
| draw outcome | `LotteryEntry.PersistDrawOutcome` | moves Won entries' tickets to sold, for each stock it draws |

Under READ COMMITTED each statement takes a new snapshot, so the count read after the lock is granted sees every commit of the transactions that held the lock before. Two paths therefore never both see the same last tickets as free. A hold that lapses is not a write: a Checkout past its hold expiry stops counting as held by time alone, and `ReleaseExpired` only records it later. The lock order is always the `users` row (D4) before the `ticket_stocks` row, and a draw locks its stocks in id order, so the paths cannot deadlock.

- Rejected — keep `sold_count` as a counter: every path that moves tickets (commit, revert, draw outcome, a reverted win) must also add or subtract it, and one missed path leaves it wrong for good; the held count cannot be a counter anyway because a hold lapses by time. Its one advantage, a `CHECK (sold_count <= quantity)` constraint, does not cover held tickets.

### D6 — Lottery draw against shared stock

A sale's draw runs per TicketStock of its events: the Entered entries of that stock are drawn in random order against the stock's remaining tickets at the draw, which already excludes tickets sold or won in earlier sales of the event. The draw locks each `ticket_stocks` row it draws. Entries are allocated all-or-nothing as today.

Sales of one event never overlap, but they may run back to back: a first-come sale may open at the instant a lottery closes. `RunDraw` reads the remaining count, charges the winners and only then records the outcome, so a checkout taken in between could oversell the stock. `CheckoutUseCase.Start` therefore refuses a checkout for a stock while a closed Lottery sale of the event still has Entered entries for it (`components/usecase/checkout/start`). The draw runs within 1 minute after the close, so the first-come sale waits about a minute.

- Rejected — admit entries against the remaining count read when the outcome is recorded (as `make-lottery-draw-durable` does): here the winners are charged before the outcome is recorded, so an entry refused at recording would already be charged. `make-lottery-draw-durable` records first and charges after, and adds that admission; the guard stays as a simple second line.

### D7 — Resale listing belongs to a TicketStock

`resale_listings.ticket_type_id` becomes `ticket_stock_id`, and `resale_listings.checkout_id` is dropped: a Checkout only holds a FirstCome sale's stock. A fan may list a Ticket while the stock is sold out and the resale deadline has not passed (`components/entity/ticket-stock` "Resale open at a time"); `ticket_types.resale_open_at` is not carried over. A quantity that never changes leaves `RevertCommit` as the only way a sold-out stock gains a ticket back; while it does, the primary sale sells that ticket and no listing is created. A listing can be withdrawn while it is open.

Buying a listed ticket leaves the first-come Checkout. A resale purchase through a Checkout let bots and repeated reloads race for each listing; the change `resell-tickets-by-lottery` makes it a lottery drawn every day, adding its own entry entity, the Listed → Sold transition and the refund to the listing fan. Until it ships, listings are made but not bought.

Every Ticket of a sold-out stock can be listed, whether bought first come or won in a lottery. This reverses the non-goal of the archived `official-resale` change, whose reason was that a lottery TicketType had no sold count to sell out; a shared TicketStock counts lottery winners in its sold count, so that reason is gone.

### D8 — Deletes refused while a live Order refers

`ticket_stocks.seat_type_id` references `seat_types` with `ON DELETE RESTRICT`, so `SeatType.Delete` fails with FailedPrecondition while a TicketStock uses it. `TicketStock.Delete` locks the `ticket_stocks` row, fails with FailedPrecondition when an Order that is not Void names the stock or a Void Order's card authorization is not yet released (deleting it would strand the hold on the fan's card), and otherwise deletes the stock's Void Orders with their Checkouts and LotteryEntries and then the stock, in one transaction. `orders.ticket_stock_id` references `ticket_stocks` with `ON DELETE RESTRICT`: an Order inserted by a path that does not lock the stock row (`LotteryEntry.Create`, D4) takes a key-share lock on the referenced row, so it waits for the delete and then fails on the missing row, or the delete fails on the new reference. No extra lock is needed in `LotteryEntry.Create`. Void Orders are kept off the guard because an abandoned checkout would otherwise freeze a mistaken quantity for good.

One entry per user, sale and event: `LotteryEntry.Create` refuses a second entry of the Order's user in the sale for the stock's event with AlreadyExists. It runs under the `users` row lock of D4, so the check and the insert cannot race; a uniqueness constraint over the sale, the event and the user can back it if the implementation keeps those columns where one index can cover them. Per sale and event, not per sale, so a fan can enter several dates of a tour presale.

### D9 — Changes made alongside

Three changes are written on this model at the same time and ship after it, after `publish-events-through-outbox` (which is rebased on this model and announces from entity operations, so the three never write usecase announcements):

- `make-lottery-draw-durable`: record Won and Lost for the whole sale before any card is charged, resume a stopped draw with the same outcome, charge and release each entry as a durable workflow, release lost entries' card authorizations, and tell losing fans. Until it ships, a draw stopped between the first capture and the record can charge a fan who then loses.
- `unify-order-issuance`: one `Issue` that charges a Pending Order of either source and makes it Paid, replacing the 1-minute sweeper and the notice-driven issuance.
- `resell-tickets-by-lottery`: official resale bought by a lottery drawn every day (D7).

### D10 — Screens read the new fields

The organizer console reads seat types from `SeatTypeService.ListBySeries` on the concert page, and stocks with their sold and held counts from `TicketStockService.ListByEvent` on the event's Sales tab; `TicketSaleService.ListByEvent` (organizer) returns the sales with the lottery entry stats of each stock and no stock counts. The sale editor sends the event IDs instead of a TicketType. Each event's per-account limit is entered in the concert editor and saved through the Series RPCs (`SeriesUseCase.Create` and `Update`); it can change only while the event is DRAFT. The fan event page, checkout and lottery entry read each stock's seat type name, price, state and whether its resale is open from `TicketSaleService.ListByEvent`, which returns the sale with the event's stocks. The per-account limit comes from the Event. The exact field names are fixed in the specs and the proto PR.

### D11 — Names kept for a later rename

`LotteryEntry.GetStatsByTicketType`, `ListByTicketTypeAndUser`, `ListUndrawnForTicketType` and `LotteryEntryUseCase.ListByTicketType` keep their names and spec paths although they now take a sale and a TicketStock. Renaming them (for example to `ListBySale`) is a follow-up change, because moving a spec path is not done inside a change.

### D12 — No draw time, no lottery result time, every sale named and closed

- **Drawn** follows from the entries: a closed Organizer's lottery is drawn when none of its entries is Entered (`components/entity/ticket-sale` "Drawn lottery"). `ticket_sales.drawn_at` is dropped; `ListDueForDraw` selects closed lotteries with an Entered entry; recording an outcome again changes nothing because the entries are no longer Entered.
- **Lottery result time** is dropped with its column, and so is the `RESULT_DAY` reminder stage that read it: it was due on the day a lottery closed, before any result existed (a defect that predates this change), and a fan of an Organizer's lottery is told the result directly by `make-lottery-draw-durable`. Recorded `RESULT_DAY` reminders are deleted by the migration.
- **End time** is required on every sale. Discovery skips a sale whose pages state no end, such as a first-come sale "until sold out".
- **Name** is required on every sale. Discovery reads it from the sale's page and skips a sale its pages do not name.

## Risks / Trade-offs

- [The change touches every ticketing path at once] → One breaking proto release and one backend migration and deploy; the product has no users, and availability may be traded (see the workspace operating state). Verified with unit tests, the Stripe Sandbox E2E and read-only prod checks.
- [Pending and Void Orders confuse readers that assume every Order is paid] → The specs of `order/list-by-event`, `list-referral-stats-by-event`, Settlement and the analytics export name Paid Orders explicitly; the tasks include checking every `orders` reader.
- [The `users` row lock serializes one fan's applications] → Only the same fan waits; a fan applying twice at once is not a case to optimize.
- [The durable draw fix ships after this change] → `make-lottery-draw-durable` is written alongside (D9) and deployed right after; no lottery sale should open on the new model before it ships.
- [Listed tickets cannot be bought until `resell-tickets-by-lottery` ships] → The event page says tickets can be listed and shows no action to buy; the Terms of Service already say a sale is not guaranteed.

## Migration Plan

The pilot charged real money (liverty-music/specification#1074), but the product has no users besides the owner and one tester, so the owner decided to delete every record of the Organizer sales instead of mapping it to the new model. Discovered sales are kept: they only report sales found on artists' pages. Those that break the new rules are fixed in the same migration: a discovered sale without an end time is deleted with its reminders (it was a first-come sale "until sold out" and is over or never closes), and a discovered sale is given the name 抽選 or 先着 by its method until its next discovery replaces it with the name on its page (`components/entity/ticket-sale/upsert-discovered` replaces the name on a match).

1. Read-only pre-check in prod (tasks 2.x): no sale of a Series with an Organizer is open, no Settlement is Held or waiting for payout, and every captured payment of an Order is either settled or refunded at the payment provider. A failed check stops the migration until it is resolved by hand.
2. One migration, in one transaction:
   - delete, for every Series that has an Organizer: its ticket sales, ticket types, lottery entries, checkouts, orders, tickets, settlements, resale listings and the referral and admission rows that refer to them; the payment provider keeps its own records of the payments;
   - delete each discovered sale without an end time with its reminders, name every other discovered sale 抽選 or 先着 by its method, and drop `ticket_sales.drawn_at` and `ticket_sales.lottery_result_at`, and delete the recorded `RESULT_DAY` reminders;
   - create `seat_types`, `ticket_stocks`, `ticket_sale_events` and the events' per-account limit (4 for existing events), change `orders`, `checkouts` and `lottery_entries` as in D3, change the (now empty) `resale_listings` table to refer to stocks (D7), and drop `ticket_types`; no row is moved, since every Organizer-sale row was deleted in the step above.
3. Deploy the backend and both frontends together after the proto release.
4. Rollback: restore from the Cloud SQL backup taken before the migration and redeploy the previous images.
