## Why

The pilot with an independent artist (liverty-music/specification#1074) sells tickets first come, first served, with real money, over several days at a small venue. The platform can only sell by lottery today: price and capacity live on the lottery phase, Orders can only come from a lottery application, and nothing tells a fan their purchase went through. `public-event-page` leaves the ticket section's sale, the checkout and the post-purchase prompts to this change.

## What Changes

- **First-party sale entity `TicketSale`** (sale method FirstCome for now): one per event, with a sale window that ends no later than the event's start time, a 税込 (tax-inclusive) price per ticket, a quantity and a per-account limit (1-10, default 4). It can be set up only for a published event that has a start time, by an Organizer whose 特商法 (Specified Commercial Transactions Act) seller details are complete. The price cannot change once the first checkout starts; the quantity can grow, or shrink down to what is sold and held.
- **Checkout with a 15-minute hold (`Reservation`)** and the authorize → commit → capture flow:
  1. Starting a checkout holds the chosen count for exactly 15 minutes, never extended. It returns the fan's existing holding Reservation for the same sale, so a double tap, a retry or a reload never holds twice.
  2. The fan enters their 本人確認 (identity check) name and phone number, prefilled from their account, and authorizes the card with 3D Secure.
  3. While the hold lasts, the server commits the tickets in one conditional step, charges the card once, records the charge and issues the Order and Tickets. A lapsed hold cannot be committed; the fan starts again and is not charged.
  4. Placing the order is handled one call at a time per checkout, and a cancelled concert is never charged. A charged checkout is never charged again or released. If issuing fails it is retried every minute and reported to an operator after 10 minutes. Card holds of every ended checkout are released within 2 minutes after its hold ends, and a charged hold on an ended checkout is reported.
- **Per-account limit counted cumulatively** over completed purchases and held Reservations, so splitting purchases cannot exceed it.
- **Card payments only**, including Apple Pay and Google Pay, which are card wallets. American Express is accepted, because the hold lasts seconds, not days. **No buyer fee**: the fan pays the price × count.
- **Sale states on the event page**: not yet on sale (with the start time in Japan time), on sale (with "残りわずか" at 10% or less rounded up, never an exact count), sold out (with a message while other fans hold the last tickets), sale ended. A cancelled concert's sale is neither shown nor sold.
- **特商法 final confirmation step** before the order is placed: quantity, price and total 税込, payment method and timing, delivery timing, sale period, the resale prohibition (チケット不正転売禁止法), the no-cancellation and no-cooling-off statement, the Organizer's seller details, and a way back to correct the count and identity.
- **Purchase completed notifications**: an email (new, sent through the existing mail provider, once per Order) and a push notification of a new type, both after the purchase is recorded and independent of it. Lottery winners receive them too.
- **Reliable post-purchase events**: issuing an Order records an `ORDER.paid` event in the same transaction (transactional outbox). Two consumers run from it: the confirmation email and push, and the ticket journey update to PAID, which moves out of the lottery issuance path. Analytics and a sold-out signal are left until official resale needs them.
- **Organizer seller details** (legal name, representative, address, phone, contact email), entered by an admin during vetting.
- **Per-Organizer platform fee rate**: the default becomes 8% (was 5%). An admin can set a different rate, and the pilot Organizer is set to 5%. **BREAKING** for the fee computation: the rate is read from the Organizer instead of a constant.
- **Fan identity on the account**: the 本人確認 name and phone number are kept on the User, prefilled at checkout and updated when the fan edits them. Each Ticket keeps its own copy for its face, as today.
- **Order source generalised**: an Order comes from either a lottery application or a Reservation, never both, and issuance is idempotent per source.

## Capabilities

### New Capabilities

- `components/entity/ticket-sale`: the platform's own sale of an event's tickets; window, price, quantity, per-account limit, remaining count, sale state, price lock
- `components/entity/ticket-sale/create`, `get`, `get-by-event`, `update`
- `components/entity/reservation`: one checkout's 15-minute hold; states Held, Committed, Completed, Expired, Released; a charged checkout is never released
- `components/entity/reservation/get-or-create-held`: at most one holding Reservation per fan and sale, within the stock and the per-account limit
- `components/entity/reservation/get`, `set-authorization`, `commit` (only while holding), `release` (only a Held one), `revert-commit` (only an uncharged one), `record-capture`, `record-authorization-release`, `list-due`
- `components/entity/reservation/create-authorization`, `verify-authorization`, `capture-authorization`, `cancel-authorization`: the card hold of a checkout; American Express accepted
- `components/entity/order/get-by-reservation-id`, `send-confirmation-email`
- `components/entity/organizer/set-seller-details`, `set-platform-fee-rate`
- `components/entity/user/update-holder-identity`
- `components/usecase/ticket-sale/configure`, `get`, `get-own` (the Organizer's view with quantity and sold count)
- `components/usecase/reservation/start`, `get`, `authorize`, `release-expired`
- `components/usecase/order/issue-from-reservation`: commit, charge and issue; the fan's place-order action
- `components/usecase/order/issue-due-reservations`: finishes committed checkouts whose charge or issuance did not complete
- `components/usecase/notification/send-order-confirmation`: confirmation email and push for each paid Order
- `components/usecase/ticket-journey/mark-paid`: the PAID update for each recorded purchase
- `components/usecase/organizer/update-seller-details`, `set-platform-fee-rate`
- `components/adapter/fan/api/rpc/ticket-sale`: public sale read, no sign-in
- `components/adapter/fan/api/rpc/reservation`: the signed-in fan's checkout calls (Start, Get, Authorize, Confirm)
- `components/adapter/organizer/api/rpc/ticket-sale`: configure and read the Organizer's own sale
- `components/infrastructure/fan/web/route/checkout`: the checkout screens, including the 特商法 final confirmation and the completion screen with the notification and install prompts
- `components/infrastructure/organizer/web/route/ticket-sale-editor`: the sale settings screen
- `stories/buy-tickets-first-come`

### Modified Capabilities

- `components/entity/order`: "An Order has exactly one source" (added). (Purpose) the `application` row becomes a source — a won TicketApplication or a Committed Reservation, one Order per source — a `confirmation-sent time` row is added, and the Purpose sentence no longer says "of one winning TicketApplication".
- `components/entity/order/issue`: "Order, tickets and settlement together, once per application" (renamed to "... once per source" and modified) — fee at the Organizer's rate, the purchase recorded with its content, a Reservation completed only when Committed and charged.
- `components/entity/settlement`: "Platform fee rate" (modified) — the Organizer's rate, kept on the Settlement. (Purpose) attribute table gains the fee rate applied.
- `components/entity/organizer`: "Seller details" and "Platform fee rate" (added). (Purpose) attribute table gains the five seller details and the platform fee rate.
- `components/entity/user`: "Holder identity on the account" (added). (Purpose) attribute table gains the holder full name and holder phone number.
- `components/entity/notification`: Purpose-only, no delta file — the type row gains `order_confirmation`.
- `components/usecase/notification/deliver`: "Runs for each requested notification" (modified) — NotificationUseCase.SendOrderConfirmation is a caller.
- `components/usecase/order/issue-from-captured-win`: "Issue an order and its tickets from a won application" (modified, fee at the Organizer's rate, purchase recorded); "Ticket journey becomes Paid" (removed, moved to `ticket-journey/mark-paid`). (Purpose) drops "and marks the buyer's ticket journey for the event as Paid".
- `components/adapter/admin/api/rpc/organizer`: "Only admins manage Organizers", "Requests are validated before any usecase runs" and "Each call runs one OrganizerUseCase method" (modified) — two calls added, their validation, and the Organizer returned with its seller details and rate.
- `components/infrastructure/fan/web/route/event`: "Ticket section shows the sale" (added). This capability is created by `public-event-page`; this change is archived after it.

Purpose edits are made to the main specs at archive. Capabilities with no spec yet are touched and referenced by name for follow-up specs: the admin console's Organizer screen, which gains the seller-details and fee-rate fields, and the organizer console's concert list, which gains the entry to the sale editor.

## Impact

- **specification:** new proto entities and services (`TicketSale`, `Reservation`, the fan and organizer sale services); `Order` gets a source that is not only a lottery application; `Organizer` gets seller details and a fee rate; the `ApplicantIdentity` type moves out of the lottery files.
- **backend:**
  - new tables for ticket sales, reservations and the outbox, and a nullable source on orders with a unique key per source;
  - Stripe PaymentIntents get metadata and per-operation idempotency keys;
  - the outbox relay;
  - new consumers: email and push, ticket journey;
  - sweepers for expired holds, leftover card holds and stalled commits, with an alert for charged-but-unissued checkouts;
  - the card-hold port parameterised per caller (brand policy, idempotency key prefix);
  - mail sending through the existing Postmark account.
- **frontend:** the checkout route in the fan app, the sale-settings screen in the organizer app, the seller-details and fee-rate fields in the admin app.
- **Depends on:** `public-event-page` (the ticket section's place on the page and the sign-up return), `payments-legal-compliance` (counsel review of the 特商法 copy, receipts and the livemode gate).
- **Out of scope:** convenience-store and other non-card payments; buyer fees; ticket types and tiers; waitlists; a fan's own cancellation; receipts as 適格請求書 (qualified invoices), pending the 媒介者交付特例 decision; SMS phone verification; eKYC requirements on a sale; folding the lottery into `TicketSale` and renaming the scraped `SalesPhase`, which are left to a later change.
