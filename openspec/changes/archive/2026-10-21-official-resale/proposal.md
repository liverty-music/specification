## Why

The pilot sells tickets first come, first served, with real money (liverty-music/specification#1074). A fan who bought a ticket and then cannot attend has no way to hand it on, and the checkout's 特商法 (Specified Commercial Transactions Act) final confirmation already tells every fan who buys that official resale opens if the event sells out. This change builds that official resale, in the simplified form decided for the pilot on 2026-10-07: it opens when the primary sale sells out, other fans buy first come, first served through the same checkout, and the oldest listing sells first.

## What Changes

- **Resale opens when a first-come ticket type sells out** (every primary ticket paid) and stays open after that, even if the Organizer later adds tickets. It closes when the event's admission window opens, 3 hours before the start time; the start time is required for a sale, the doors-open time is not. An event that never sells out has no resale; the checkout and the Terms of Service already say so.
- **A fan lists a ticket** they hold for such a ticket type, while it is Issued and not admitted, and can **withdraw** it until another fan holds it in a checkout. A listing that does not sell by the deadline expires and the ticket stays the fan's.
- **Another fan buys through the same checkout as the primary sale**: on a sold-out ticket type with resale open, starting a checkout holds listings instead of stock, oldest first, for 15 minutes or until the deadline, whichever is earlier. The price is the face value (券面価格). The per-account limit, card authorization, the 特商法 final confirmation, the referral code and the confirmation email work as for the primary sale; the final confirmation also says that the tickets are official resale tickets at face value.
- **On purchase, atomically:** the purchasing fan's Order and new Tickets are issued to that fan (the 本人確認 identity check details are that fan's own, so each ticket stays a 特定興行入場券 covered ticket), the listed Tickets are Voided, and the listing fan's original Order's payout to the Organizer drops by the share of the resold tickets, so the Organizer is paid once per seat.
- **The listing fan is refunded within 1 minute after the purchasing fan is charged**, to the card they paid with: the face value minus a resale fee of 10%, rounded down to the yen (a 5,000 yen ticket refunds 4,500 yen). An email tells them the ticket sold and how much is refunded. There is no hold-back period: the purchasing fan's money stays with the platform until the Organizer's payout 7 days after the event, which already covers a chargeback on that charge.
- **Cancellation (中止)** refunds the listing fan's remaining tickets at face value, ends their open listings, and refunds the purchasing fan in full, as for any Order. A resale already completed keeps its fee.
- The event page offers resale tickets when a listing is free, and the tickets screen shows each ticket's listing and the refund.
- The Terms of Service state the resale rules: when resale opens and closes, the fee, the refund and that an event that does not sell out has no resale.

Dropped from the earlier design of this change: the lottery-loser priority queue and sequential timed offers (D5), the hold-back reserve (D1), structural exclusions and the admin exception (D2, D7), the organizer cutoff setting (D3) and buyback (D6). They stay in `docs/resale-design.md` as background.

## Capabilities

### New Capabilities

- `components/entity/resale-listing`: a fan's offer of one Ticket for official resale; its price, fee and refund amount; its deadline; when it is open and when it is free to hold.
- `components/entity/resale-listing/create`: stores a new listing, at most one open listing per Ticket.
- `components/entity/resale-listing/get`: reads one listing.
- `components/entity/resale-listing/withdraw`: withdraws a Listed listing no checkout holds.
- `components/entity/resale-listing/list-by-user`: a fan's listings.
- `components/entity/resale-listing/list-sold-unrefunded`: Sold listings whose fan is not refunded yet.
- `components/entity/resale-listing/record-refund`: records the refund of a Sold listing.
- `components/entity/resale-listing/send-sold-email`: sends the "your ticket sold" email once per listing.
- `components/usecase/resale-listing/create`: a fan lists a ticket.
- `components/usecase/resale-listing/withdraw`: a fan withdraws a listing.
- `components/usecase/resale-listing/list`: a fan reads their listings.
- `components/usecase/resale-listing/refund-sold`: refunds listing fans within 1 minute after a sale and announces each refund.
- `components/usecase/notification/send-resale-sold`: emails the listing fan that their ticket sold and how much is refunded, for each announced refund.
- `components/adapter/fan/api/rpc/resale-listing`: the fan boundary of the listing calls.
- `stories/resell-a-ticket`: a fan who cannot attend lists a ticket, another fan buys it, and the first fan is refunded.

### Modified Capabilities

- `components/entity/scanner`: the admission window opens 3 hours before the start time, no longer 3 hours before the open time (owner, 2026-10-20), so the Scanner links and the resale deadline both follow the one time every sale has.
- `components/entity/ticket-type` (Purpose: `resale open time` and `free resale count` rows): resale opens when the ticket type sells out; resale open and available at a time.
- `components/entity/ticket-type/get`: returns the free resale count.
- `components/entity/ticket-sale/list-by-event`: returns each first-come TicketType's free resale count.
- `components/entity/checkout` (Purpose: `resale listings` row; Checkout `||--o{` ResaleListing in the erDiagram): a resale checkout's hold ends at the resale deadline when that is earlier than 15 minutes.
- `components/entity/checkout/get-or-create-held`: holds free listings, oldest first, when asked for resale.
- `components/entity/checkout/commit`: a resale commit leaves the sold count alone; the commit that sells a ticket type out opens its resale.
- `components/entity/checkout/revert-commit`: a resale revert leaves the sold count alone.
- `components/usecase/checkout/start`: starts a resale checkout when the ticket type is not on sale and its resale is open.
- `components/entity/order/issue`: a resale checkout's issuance sells its listings, voids their Tickets and lowers the original Orders' payouts.
- `components/entity/order/create-refund`: one refund per Order and purpose (the Order's own refund, or one listing's refund), so a resold Order can be refunded more than once.
- `components/entity/order/commit-refund`: voids only the Order's Issued Tickets and ends its Listed listings.
- `components/usecase/order/refund`: a cancellation refunds the price of the Order's Tickets that are still Issued.
- `components/entity/settlement`: the share of resold tickets taken off a Held Settlement.
- `components/usecase/ticket-sale/list-by-event`: returns whether resale is open and available.
- `components/adapter/fan/api/rpc/ticket-sale`: carries whether resale is open and available, never a count.
- `components/adapter/fan/api/rpc/checkout`: a returned Checkout says whether it is a resale checkout.
- `components/infrastructure/fan/web/route/event`: the ticket section offers resale.
- `components/infrastructure/fan/web/route/checkout`: the final confirmation of a resale checkout.
- `components/infrastructure/fan/web/route/tickets`: listing, withdrawing, and a resold ticket's refund.
- `components/infrastructure/fan/web/global/legal-document`: the Terms of Service state the resale rules.

Unchanged and relied on: `components/usecase/order/issue-from-checkout` (it builds the purchasing fan's Order, Tickets and Settlement from the Checkout as for any checkout, and `Order.Issue` does the resale part), `components/usecase/order/fulfill-payment`, `components/usecase/notification/send-order-confirmation` (the purchasing fan's email), `components/usecase/checkout/release-expired` and `components/entity/checkout/release` (a listing is free again as soon as the Checkout holding it is no longer holding or Committed), `components/entity/ticket` (its user never changes; resale voids it and issues a new one), and `components/usecase/ticket/admit` (resale closes when admission opens).

## Impact

- **specification:** the `AdmissionWindow` doc comment in `entity/v1/scanner.proto`; `entity/v1/resale_listing.proto`; `ResaleListingService` (Create, Withdraw, List) under `rpc/resale_listing/v1`; `resale_open` and `resale_available` on the fan's TicketType; `resale` on the Checkout. Additive, no breaking change.
- **backend:** an Atlas migration (`resale_listings`, `ticket_types.resale_open_time`; design D8); the entity, repository, usecase and handler code above; the 1-minute `RefundSold` job in the existing checkout sweeper (design D6); `admissionWindowLead` counted from the start time in `entity/scanner.go` (design D11).
- **frontend:** event page ticket section, checkout final confirmation, tickets screen listing flow, Terms of Service text, ja/en copy.
- **cloud-provisioning:** none expected.
- **Legal:** the counsel opinion in `payments-legal-compliance` 1.1 covers the two money legs (a refund of the fan's own payment and a new sale to the purchasing fan, so money never moves between fans). The Organizer's consent to resale is a clause of the Organizer agreement (design D10).
- **Depends on:** the shipped `first-come-ticket-sales`, `ticket-wallet-and-checkin` and `referral-attribution`. Must ship before the `payments-legal-compliance` livemode gate.
