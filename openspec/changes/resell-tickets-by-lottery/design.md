## Context

See proposal.md for why. This change is applied after `remodel-ticket-sales` (Pending Orders at application, TicketStock, Event per-account limit, `Order.GetHeldForEvent`, the users-row lock of its D4, a Checkout only for a first-come sale's stock), and after the recreated `make-lottery-draw-durable` (draw outcome recorded before any charge, `OrderUseCase.Issue` charging a Won entry with retries for up to 24 hours, a card authorization release workflow with retries) and `unify-order-issuance` (one `OrderUseCase.Issue` for every source). It reuses the workflow runtime of `introduce-durable-workflows` (DBOS: queues, cron schedules with a seconds field, exactly-once runs per scheduled time, recovery of pending workflows in `cmd/worker`).

Today's resale (`2026-10-21-official-resale`): a Checkout with `resale = true` holds the oldest free listings; issuance voids the listed Tickets, issues new ones, makes the listings Sold, and `ResaleListingUseCase.RefundSold` refunds each listing fan the price minus the 10% fee. The refund, the sold email, the fee, the deadline (3 hours before the start time) and the Settlement handling stay as they are.

## Goals / Non-Goals

**Goals:**

- No race at the moment a listing appears: applications are accepted at any time while resale is open, and allocation happens in one scheduled draw per stock.
- Nobody is charged without receiving tickets, and no card authorization is left to lapse silently.

**Non-Goals:**

- Priority for presale losers, preference orders, or several seat types in one application.
- Resale figures in the organizer console.

## Decisions

### D1 — ResaleEntry is its own entity, sourced by an Order

`resale_entries (id, order_id unique, state, create_time, draw_time, ended_email_send_time)`. A LotteryEntry belongs to a Lottery TicketSale and draws a stock's quantity once; a ResaleEntry belongs to no sale and draws listings at every daily draw, so not every rule of one holds for the other. The Order carries the user, stock, count, referral code and card authorization (remodel D3).

- Rejected — reuse LotteryEntry with a resale flag: every lottery rule would gain a resale branch, the mix the remodel removed from Checkout.
- Rejected — a "resale sale" (TicketSale with listings as supply): a sale has a window and verification that resale does not have.

### D2 — One Entered entry per fan and event, checked under the users-row lock

`ResaleEntry.Create` takes the users-row lock of remodel D4, reads `Order.GetHeldForEvent` (which counts Pending Orders, so an Entered resale entry counts), checks the Event's fit rule and that no Entered resale entry of the user exists for the event, then inserts the Order and the entry. A partial unique index on `resale_entries` cannot see the event (it is on the stock), so the check runs under the lock rather than as an index; every path creating an Order takes the same lock, so nothing created after the check is missed.

### D3 — Draw schedule

One DBOS scheduled workflow `draw-resale` with the cron `0 * * * * *` (every minute, Asia/Tokyo). For its scheduled time `T` it selects the TicketStocks with Entered entries whose event has a draw at `T`: `T` is 12:00 on a day before the event's day, or the event's resale deadline `min(12:00, start − 3h)` on its day, which is also the last draw and the time resale closes (spec `entity/resale-listing` "Resale deadline"; one rule, so no listing or entry stays open between the last draw and admission). DBOS runs each scheduled time once and recovers a stopped run, so a draw is neither skipped nor doubled; no draw record and no "already recorded" check are kept for that.

- Rejected — one 12:00 cron plus per-event timers for matinees: two mechanisms for one rule.
- Rejected — a sweeper that draws "whatever is due": it needs a stored last-draw time per stock to avoid drawing twice.

### D4 — One draw of one stock

Per stock, in one workflow step: lock the `ticket_stocks` row (the lock `ResaleListing.Withdraw` and `Create` take first, as they take the ticket type row today), read the Entered entries with their card authorization expiry, read the listings free for a draw oldest first, shuffle the candidates with a cryptographic random source, allocate all-or-nothing, and call `PersistDrawOutcome` in the same transaction. Withdraw, listing withdrawal and the draw are therefore serialized on the stock row, so nothing the draw read can change before it records; there is no redraw. When the stock's event is no longer PUBLISHED (中止), the step allocates nothing and records every candidate Lost. After commit, the workflow enqueues `OrderUseCase.Issue` for each winner (unify-order-issuance), the card authorization release workflow (make-lottery-draw-durable) for each lapsed or lost Order, and `NotificationUseCase.SendResaleEntryEnded` for each lapsed or lost entry.

A Won entry whose capture fails permanently is made Lost by `Issue` (spec "A won entry that cannot be charged"); its listings become free for the next draw. A capture that fails because the provider is unreachable is retried by `Issue` for up to 24 hours (make-lottery-draw-durable), which is why D5 needs 24 hours of validity, but never past the event's start time: at the start time `Issue` makes the entry Lost and its Order Void, releases the card authorization and tells the fan, so nobody is charged for a show that has begun.

### D5 — Card authorization expiry and lapse

The card authorization's expiry is the charge's `payment_method_details.card.capture_before`, stored as `card_authorizations.expire_time` when the PaymentIntent reaches `requires_capture` (the `payment_intent.amount_capturable_updated` notice and `Confirm` both read it). Stripe's validity windows (docs.stripe.com/payments/place-a-hold-on-a-payment-method, read 2026-10-28): for a Japan-based account, JPY transactions of Visa, Mastercard, JCB, Diners Club and Discover can be held up to 30 days; American Express follows the standard 7 days; when an authorization expires the PaymentIntent becomes `canceled`. The platform account is Japan-based and charges JPY, so most entries last up to 30 days and Amex entries about a week. `request_extended_authorization` is not used: Stripe's extended-authorization page says it does not apply to transactions with businesses in Japan, and the 30-day window above applies to them by default. Task 3.1 still reads `capture_before` from the Stripe test API to confirm the stored expiry.

An entry lapses at the first draw at which its expiry is less than 24 hours after the draw time. Lapsing at a draw, not at the expiry instant, needs no extra timer: the draw already reads every candidate.

### D6 — Notifications

`NotificationUseCase.SendResaleEntryEnded` follows `SendResaleSold`: an event-consumer job, email through Postmark with `ended_email_send_time` set once, and a push through the existing Web Push delivery with types `resale_entry_lapsed` and `resale_entry_lost`. The winner is told by the existing purchase confirmation email and push of `OrderUseCase.Issue`.

### D7 — Screens read

The event page reads stocks, state and resale openness from `TicketSaleService.ListByEvent` (remodel) and the fan's Entered entry from `ResaleEntryService.List`. The resale entry screen reads the fan's entries and each next draw time from `ResaleEntryService.List`, the per-account limit and held count from the event fields of `TicketSaleService.ListByEvent` (remodel D10), and the seat type and price from the stock.

### D8 — The fan withdraws a waiting entry

`ResaleEntry.Withdraw` locks the entry's `ticket_stocks` row, the same row the draw of D4 locks before it reads the Entered entries, then checks the entry is still Entered and sets it Withdrawn and its Order Void in the same transaction. A withdrawal and a draw of the stock are therefore serialized: when the draw commits first, Withdraw finds the entry Won, Lost or Lapsed and fails with FailedPrecondition; when Withdraw commits first, the draw no longer lists the entry. After commit, `ResaleEntryUseCase.Withdraw` enqueues the card authorization release workflow of make-lottery-draw-durable for the Order, which retries while the provider is unreachable, so the fan's response does not wait on the payment provider. No ended email is sent: the fan acted themselves.

- Rejected — let the fan withdraw only outside a window around 12:00: a time rule the fan would have to learn, when the row lock already settles the race.

### Purpose edits

Applied directly to the main specs with this change, as `remodel-ticket-sales` does:
- `components/entity/resale-listing`: a new attribute `resale entry` ("the ResaleEntry a draw allocated it to; absent until allocated") and the ER line `ResaleEntry |o--o{ ResaleListing : "is allocated"` (`remodel-ticket-sales` already removed the `checkout` attribute); the Purpose sentence says another fan buys it through a daily resale draw.
- `components/entity/card-authorization`: an `expire time` row ("when the authorized amount can no longer be charged; absent until authorized").
- `components/entity/order`: `Order ||--o| ResaleEntry : "is applied for as"` in the ER diagram; the source attribute lists ResaleEntry.
- `stories/resell-a-ticket`: the usecase diagram includes ResaleEntryUseCase.AuthorizeCard, Confirm and Draw and OrderUseCase.Issue instead of CheckoutUseCase.Start and AuthorizeCard.

### D9 — Verification required when any sale of the event requires it

A ResaleEntry belongs to no TicketSale, so no sale's verification requirement applies to it directly. `ResaleEntryUseCase.AuthorizeCard` requires an Active IdentityVerification when any sale of the event requires verification. Verified-any and JPKI-only both require an Active IdentityVerification today (`entity/ticket-sale` "Verification requirement"), so ranking them would add a rule with no effect. This decision moved here from `remodel-ticket-sales`, which no longer has a resale purchase.

- Rejected — no requirement for resale: a fan refused by a sale that requires verification could buy the same seat through resale.

## Risks / Trade-offs

- [A fan waits up to a day for a result] → Accepted: the trade for removing the race. The screen shows the next draw time.
- [American Express applications lapse after about 6 days] → The fan is told and can apply again; the lapse is shown as 期限切れ, not as a failure.
- [Listed tickets cannot be bought between `remodel-ticket-sales` and this change] → Accepted: remodel removed the resale Checkout and its event page shows no action to buy; with no users, the gap is acceptable.

## Migration Plan

`remodel-ticket-sales` deletes the existing ticket data before its migration, so no resale row exists to migrate. The backend migration adds `resale_entries`, `resale_listings.resale_entry_id` (`remodel-ticket-sales` already dropped `checkout_id`) and `card_authorizations.expire_time`. Deploy backend then frontend; rollback is the previous images with the migration's down step (the new table is empty when nothing was drawn).
