## Context

See proposal.md for why. This design replaces the August 2026 draft of this change, which was written before the lottery, the first-come sale and the venue entry existed and assumed a lottery-loser priority queue with timed offers. The pilot decisions of 2026-10-07 (liverty-music/specification#1074, "Official resale, simplified") and the owner's answers of 2026-10-20 (resale fee 10%; refund right after the purchasing fan is charged) fix the shape below. `docs/resale-design.md` keeps the legal and competitor research; its D1, D2, D3, D5, D6 and D7 are superseded here for the pilot.

What already exists and is reused:

- **First-come sale** (`first-come-ticket-sales`, archived 2026-10-11): a TicketType with a price, quantity, sold count and per-account limit; a Checkout that holds tickets for 15 minutes, authorizes the card, commits, captures and issues an Order with account-bound Tickets and a Held Settlement; the 1-minute sweepers `ReleaseExpired` and `IssueDueCheckouts` (`internal/di/checkout_sweeper_job.go`); `ORDER.paid` and the confirmation email and push.
- **Refunds** (`OrderUseCase.Refund`): a full refund of one Order for 中止 or a dispute, through `StripeOrderPayments.CreateRefund` with the idempotency key `order-refund:<order id>`.
- **Settlement:** the Organizer's split of each Order is Held until 7 days after the event and then paid out (`ReleaseDueSettlements`).
- **Venue entry:** a Scanner admits only inside the event's admission window, which opens 3 hours before the open time (or the start time) (`components/entity/scanner`).
- **Covered ticket:** a Ticket's user never changes; official resale voids it and issues a new Ticket (`components/entity/ticket`).

## Goals / Non-Goals

**Goals:**

- Resale reuses the first-come checkout end to end: the same screens, card authorization, commit, capture, issuance, `ORDER.paid`, confirmation email, referral recording and sweepers. The only new money movement is one partial refund per sold listing.
- The Organizer is paid once per seat, and no fan is ever charged for a ticket they do not receive.

**Non-Goals:**

- Resale of tickets from a Lottery sale. The pilot sells first come, first served; a won lottery ticket cannot be listed (its TicketType has no sold count to sell out). Lottery resale returns with the loser priority question in a later change.
- A priority order other than first come, first served; buyback of unsold listings; an Organizer setting to switch resale off or close it earlier; structural exclusions (free, comp, goods-bundled, name-locked tickets): the pilot has one paid ticket type and no such tickets.
- Notifying fans when a resale ticket becomes available. Fans see it on the event page.
- Resale figures in the organizer console. The Sales tab keeps counting primary sales.
- Listing several tickets in one call. The tickets screen lists one ticket at a time.

## Decisions

### D1 — Resale belongs to a TicketType and opens when it sells out

A ResaleListing is for a Ticket whose Order came from a Checkout of a FirstCome TicketType. Resale opens for that TicketType the moment its sold count reaches its quantity, and the instant is stored as `ticket_types.resale_open_time`. `Checkout.Commit` sets it in the same statement that raises the sold count, so it is set exactly once and never cleared. Raising the quantity afterwards reopens the primary sale but does not close resale ("once open, it stays open", #1074).

- Rejected — derive "sold out" on every read: the sold count can fall again (`RevertCommit`) and the quantity can grow, so a derived flag would close resale that fans already listed into.
- Rejected — open resale per event across all its TicketTypes: a presale and a general sale of one event can have different prices, and the purchasing fan must pay exactly the face value of the ticket they get.

### D2 — Resale closes when admission opens

A listing's deadline is the opening of its event's admission window (3 hours before the open time, or before the start time when there is no open time), read from the event's current times. Before that instant no Scanner admits anyone, so a listed Ticket cannot be used for entry while it can still be sold. After it, nothing can be listed or bought, and an unsold listing is simply over: its Ticket was never touched and works at the door.

Every resale Checkout's hold ends at the deadline at the latest (`hold expiry = min(start + 15 min, deadline)`), so no resale commit can happen after admission opens.

Remaining gap: a Checkout committed just before the deadline whose issuance stalls is issued by `IssueDueCheckouts` within about 1 minute. During that minute the listed Ticket is still Issued and could be admitted if its user is at the door the moment admission opens. Accepted for the pilot: it needs a stalled issuance and a fan at the door in the first minute of a 3-hour window; the admission record would show it, and an admin would refund the purchasing fan. A Ticket.Admit guard for listed tickets would close it at the cost of a new rejection reason on the scanner screen.

- Rejected — the earlier draft's `start_time − 1h`: the admission window opens 3 hours before doors, so a listed Ticket could be scanned while still for sale.

### D3 — A resale purchase is a Checkout that holds listings

`resale_listings.checkout_id` points at the Checkout that last held the listing. A listing is **free** when it is Listed, before its deadline, and its Checkout is absent or neither holding nor Committed. Nothing has to be released when a hold lapses: `ReleaseExpired` makes the Checkout Expired and the listing is free again; `RevertCommit` makes it Released and the listing is free again.

`CheckoutUseCase.Start` decides the kind from the TicketType: when it is OnSale or AllHeld, the Checkout holds primary stock as today; otherwise, when its resale is open at that time, it holds listings (`resale = true`). A TicketType that is both on sale again (quantity raised) and has listings sells primary stock first; the Organizer raised the quantity on purpose, and listings sell once the primary stock is gone again.

`Checkout.GetOrCreateHeld` for resale locks the TicketType row as it does now, then picks the `count` free listings of that TicketType with the oldest `create_time`, skipping the calling fan's own listings, and points them at the new Checkout in the same transaction. Fewer than `count` free listings → ResourceExhausted, as for primary stock. The per-account limit counts the fan's Issued Tickets as today, so a fan who holds 4 of 4 cannot buy resale tickets either.

- Rejected — a separate resale checkout entity and screens: it would duplicate the card authorization, capture, sweepers and failure handling that the pilot already verified in production.
- Rejected — mixing primary stock and listings in one Checkout: two prices of origin and two settlement paths in one Order for a rare case.

### D4 — Issuance sells the listings in the same transaction

`OrderUseCase.IssueFromCheckout` is unchanged: it captures the card and builds the purchasing fan's Paid Order, `count` new Tickets bound to that fan and a Held Settlement at the Organizer's rate. `Order.Issue` (the `rdb` issuance repository) additionally, in the same transaction, when the Checkout is a resale Checkout:

1. sets each listing held by the Checkout to Sold with `sold_time`;
2. sets each listing's Ticket to Voided;
3. for each original Order involved, lowers its Held Settlement's split by `floor(split × k ÷ m)`, where `k` is the number of its Tickets sold in this Checkout and `m` the number of its Tickets that were Issued before; when `k = m` the Settlement becomes Reversed instead (nothing is left to pay out for that Order).

Example (rate 5%): a fan bought 2 tickets at 5,000 yen (Order 10,000 yen, split 9,500 yen) and resells one. The new Order is 5,000 yen with a split of 4,750 yen; the original split falls by `floor(9,500 × 1 ÷ 2) = 4,750` to 4,750 yen. The Organizer receives 9,500 yen for the two seats, as before the resale. Of the original 10,000 yen, 4,500 yen is refunded, 4,750 yen is paid out and 750 yen stays with the platform (250 yen fee on the kept ticket and the 500 yen resale fee).

The original Settlement is always Held at that point: settlements are released 7 days after the event, and resale ends before admission opens.

- Rejected — refund and void in a later step: between capture and void, two fans would hold valid Tickets for one seat.

### D5 — Fee and refund amount

The resale fee is 10% of the listing's price, rounded down to the yen; the refund is the price minus the fee (owner, 2026-10-20). The price is the TicketType's price, which cannot change once anything is sold, so it equals what the listing fan paid per ticket and what the purchasing fan pays. The rate is a constant in the entity layer; changing it is a spec change, because the Terms of Service and the listing screen state it.

The fee covers the card fee that the payment provider does not return on a refund (3.6% in Japan) and the work of the resale, in line with ぴあ and ローチケ (about 10%). It is a 税込 amount and is framed as the price of the resale service (役務の対価), which counsel reviews under `payments-legal-compliance` 1.1.

### D6 — Refund right after the purchasing fan is charged, by a 1-minute job

`ResaleListingUseCase.RefundSold` runs every minute in the checkout sweeper goroutine (`startCheckoutSweepers`, a third call after `IssueDueCheckouts`). For each Sold listing without a refund it resolves the original Order's charge (`Order.GetProviderChargeID`), refunds the refund amount with `Order.CreateRefund` under the idempotency key `resale-listing-refund:<listing id>`, records the refund ID and time on the listing, and sends the sold email (Postmark, `send_time` set once like `orders.confirmation_send_time`).

No hold-back period (owner, 2026-10-20). The incumbents' hold-back protects them against a chargeback on the purchasing fan's charge after they paid out. Here the purchasing fan's money stays with the platform in a Held Settlement until 7 days after the event, so a dispute on that charge is covered by money the platform still holds; the listing fan's refund comes from their own charge, which the platform also still holds.

A job rather than an `ORDER.paid` consumer: the sweeper already runs every minute in every backend pod with idempotent steps, and a listing must be refunded even if the announcement is lost.

Stripe keeps idempotency keys for 24 hours. A refund created but not recorded is retried within a minute, well inside that window. If recording keeps failing for longer, the job reports the listing as needing an admin after 10 minutes, as `IssueDueCheckouts` does for unissued charges.

### D7 — An Order can be refunded more than once

`Order.CreateRefund` becomes "once per Order and purpose". The purposes are the Order's own refund (中止 or dispute; key `order-refund:<order id>` as now) and the refund of one ResaleListing (key `resale-listing-refund:<listing id>`). The Order's own refund stays on `orders.provider_refund_id`; a listing's refund is stored on the listing.

`OrderUseCase.Refund` for 中止 refunds the price of the Order's Tickets that are still Issued (`amount ÷ ticket count × issued count`), not the whole amount, and skips the payment call when no Ticket is Issued. `Order.CommitRefund` voids only the Issued Tickets and sets the Order's Listed listings to Cancelled. A Sold listing keeps its fee: the resale was completed before the concert was cancelled, and the purchasing fan is refunded in full by their own Order's refund.

A dispute on the original Order after a resale is handled as today; the charge's disputable amount is what remains after the listing refunds.

### D8 — Data model

New table `resale_listings`:

| column | type | note |
|---|---|---|
| id | uuid (v7) | |
| ticket_id | uuid FK tickets | partial unique index `WHERE status = 1` (one Listed listing per Ticket) |
| user_id | uuid FK users | the Ticket's user at listing |
| ticket_type_id | uuid FK ticket_types | resolved at listing from Order → Checkout → TicketType; index `(ticket_type_id, create_time) WHERE status = 1` for the oldest-first pick |
| price | integer | yen, copied from the TicketType |
| status | smallint | 1 Listed, 2 Sold, 3 Withdrawn, 4 Cancelled |
| checkout_id | uuid FK checkouts, nullable | the Checkout that last held it |
| create_time, sold_time, withdraw_time | timestamptz | |
| provider_refund_id, refund_time | text, timestamptz | set together by RecordRefund |
| sold_email_send_time | timestamptz | |

The fee and refund amount are derived from `price` (D5) and not stored. `ticket_types.resale_open_time timestamptz NULL` is added. Grants follow the existing pattern: full CRUD for `fan-api`, SELECT for `organizer-console-api`, none for `reception-api`.

### D9 — Proto and RPC

- `entity/v1/resale_listing.proto`: `ResaleListingId`, `ResaleListing { id, ticket_id, price, fee, refund_amount, status (LISTED, SOLD, WITHDRAWN, CANCELLED, EXPIRED), create_time, deadline_time, sold_time, refund_time }`. EXPIRED is what the fan boundary returns for a Listed listing past its deadline; it is never stored.
- `rpc/resale_listing/v1/resale_listing_service.proto`: `ResaleListingService.Create(ticket_id)`, `Withdraw(resale_listing_id)`, `List()`; caller is the signed-in fan (rpc-design skill: standard verbs, the caller never named).
- `TicketType` on the fan boundary: `bool resale_open`, `bool resale_available`; no count.
- `Checkout`: `bool resale`.

All additive.

### D10 — The Organizer's consent

A covered ticket's face says resale without the Organizer's consent is prohibited. Official resale is resale with that consent: the Organizer agreement (outside the product, signed before an admin creates the Organizer) gains a clause consenting to official resale at face value on the platform for every first-come sale. Tracked as task 1.2; the pilot Organizer signs it before the pilot sale opens.

## Risks / Trade-offs

- [The listing fan is refunded and the purchasing fan then disputes their charge] → The purchasing fan's Order is refunded with the reason Dispute as today; its Held Settlement is Reversed, so the Organizer is not paid for that seat, and the platform bears the refunded listing (at most the face value minus the fee). Same exposure as any disputed Order.
- [A listing never sells] → It expires at admission opening and the fan keeps a working Ticket; the listing screen says resale is not guaranteed.
- [A fan lists, sells, and the concert is then cancelled] → The fan keeps 90% for the resold ticket, not 100%. Stated in the Terms of Service; accepted because the resale was completed.
- [Stalled issuance across the deadline] → D2's one-minute gap; accepted, recorded in the admission records.
- [Counsel finds the two money legs or the fee framing insufficient] → `payments-legal-compliance` 1.1 runs before the livemode gate; resale ships in Stripe test mode first and the gate is not lifted until counsel signs off.

## Migration Plan

1. Plan PR (this change) → proto PR and Release → backend (migration, entity, repository, usecases, handler, job) → frontend. The migration is additive; existing rows need no backfill (`resale_open_time` stays NULL for ticket types that sold out before the release; for the pilot none has).
2. Verify in production in Stripe test mode with the Stripe Sandbox E2E and a production E2E of `stories/resell-a-ticket` on a test event.
3. Rollback: hide the listing action in the frontend; the backend changes are inert while no listing exists.
