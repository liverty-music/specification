## Why

Official resale (公式リセール) sells listings first come, first served through the primary Checkout: the moment a listing appears, every fan who wants it races to start a checkout. That race rewards bots and repeated reloads, and it puts the load of the whole race on one instant. A lottery spreads the load: fans apply at any time while resale is open, and one draw a day allocates the listings collected so far. It also keeps resale out of the Checkout, which then only sells a first-come sale's stock.

## What Changes

- **BREAKING** New `ResaleEntry`: a fan's application, through its Order, for a number of tickets of a sold-out TicketStock, paid by a card authorization placed when the fan applies, allocated all-or-nothing. It belongs to no TicketSale, so it is not a LotteryEntry. An Order's source is now a LotteryEntry, a Checkout or a ResaleEntry.
- **BREAKING** Resale is drawn every day at 12:00 Japan time. On the event's day the last draw runs at the resale deadline, now 12:00 or 3 hours before the start time if that is earlier, and resale closes with it. Resale of a cancelled (中止) concert ends at its next draw time without a ticket, and a won entry not charged by the event's start time ends without a charge. A draw allocates the listings free at that moment to the Entered entries of the stock in random order, all-or-nothing. A Won entry is charged and issued as today: the listed Tickets are voided, the fan gets new Tickets, and each listing fan is refunded the price minus the 10% resale fee. An entry not drawn stays Entered for the next draw; after the last draw every remaining entry is Lost.
- An entry whose card authorization would lapse before it could be charged after a draw ends Lapsed at that draw; its Order is Void and the fan is told by push notification and email, with a link to apply again. A Lost entry after the last draw is told the same way.
- A fan may withdraw their own entry while it waits for a draw; it becomes Withdrawn, its Order Void and its card authorization is released, with nothing charged.
- A fan has at most one Entered resale entry per event, and the event's per-account limit and one-seat-type rule count it (Order.GetHeldForEvent counts Pending Orders).
- **BREAKING** A ResaleListing is no longer held by a Checkout: it is allocated to a Won ResaleEntry by a draw. A listing can be withdrawn while no draw has allocated it.
- **BREAKING** The resale part of `CheckoutUseCase.Start` (holding listings) is gone; the event page offers 公式リセールに申し込む (apply for official resale) instead of a purchase.

## Capabilities

### New Capabilities

- `components/entity/resale-entry`: a fan's resale application, its states and the draw times of an event.
- `components/entity/resale-entry/create`, `get`, `list-by-user`, `list-entered-by-ticket-stock`, `persist-draw-outcome`, `send-ended-email`, `withdraw`: store an entry with its Pending Order; read one; list a fan's entries; list a stock's Entered entries for a draw; record a draw; send the lapse or loss email once; withdraw a waiting entry.
- `components/usecase/resale-entry/authorize-card`, `confirm`, `draw`, `list`, `withdraw`: authorize the fan's card for an application; make the entry from the authorized card authorization; run the scheduled draws; list the fan's entries; withdraw the fan's waiting entry and release its card authorization.
- `components/usecase/notification/send-resale-entry-ended`: tell a fan whose entry lapsed or lost, by email and push.
- `components/adapter/fan/api/rpc/resale-entry`: the fan gate of `ResaleEntryService`.
- `components/infrastructure/fan/web/route/resale-entry`: the screen where a fan applies for official resale and follows their entries.

### Modified Capabilities

- `components/entity/order`: an Order's source can be a ResaleEntry.
- `components/entity/resale-listing`: a listing is free for a draw instead of free to hold; the resale deadline is the event's last draw.
- `components/entity/resale-listing/withdraw`: a listing a draw has not allocated can be withdrawn.
- `components/entity/card-authorization`: a card authorization's expiry time.
- `components/infrastructure/fan/web/route/event`: the resale part of the ticket section applies instead of buying.
- `stories/resell-a-ticket`: a listed ticket goes to a fan drawn in the daily resale draw.

Entity and story Purpose edits (made directly in the main specs with this change; listed in design.md "Purpose edits"): `components/entity/resale-listing` (the `checkout` attribute becomes `resale entry`), `components/entity/card-authorization` (expiry time), `components/entity/order` (ResaleEntry in the ER diagram), `stories/resell-a-ticket` (usecase diagram).

Unchanged and relied on: `components/entity/resale-listing/create` (a fan lists a Ticket while resale is open), `components/usecase/resale-listing/refund-sold` and `components/usecase/notification/send-resale-sold` (the listing fan's refund and email), `components/entity/ticket-stock` (resale open while sold out and before the deadline).

## Impact

- **Order of changes**: written against the main specs as they will be after `remodel-ticket-sales`, then `make-lottery-draw-durable` and `unify-order-issuance` (recreated on the remodel). It is applied after all three. `remodel-ticket-sales` removes the resale Checkout; this change supplies its replacement, so the two ship in the same release or resale is off between them.
- **proto**: new `ResaleEntry` message and fan `ResaleEntryService` (AuthorizeCard, Confirm, List, Withdraw); `ResaleListing` names its entry instead of a checkout.
- **backend**: `resale_entries` table, `resale_listings.resale_entry_id`, card authorization expiry time; the `ResaleEntry` entity, repository, usecase, a per-minute draw schedule on the workflow runtime, issuance of a Won resale entry through `OrderUseCase.Issue`, card authorization release through the release workflow of `make-lottery-draw-durable`, and the lapse and loss notifications.
- **frontend**: the fan event page's resale section, the new resale entry screen, push notification texts.
- **Terms of Service and the checkout's 特商法 (Specified Commercial Transactions Act) final confirmation** for resale must say that resale tickets are allocated by a daily draw.
