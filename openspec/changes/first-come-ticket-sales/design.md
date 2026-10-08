## Context

See proposal.md for motivation. The paid pipeline built for the lottery is reused where it is independent of the lottery and generalised where it is not (survey of 2026-10-08):

- **Reusable as-is:**
  - refunds (`RefundOrder`, `CommitRefund`) and the dispute webhook;
  - the payout sweeper and transfers;
  - `Settlement` and its splits;
  - Stripe Payment Element loading in the fan app.
- **Reusable once parameterised:** the manual-capture authorization port (create, verify `requires_capture`, capture, cancel). It hard-codes the lottery's brand policy (no American Express) and `lottery-*` idempotency keys (D3).
- **Coupled to the lottery:**
  - `orders.application_id` is NOT NULL, references `ticket_applications`, and its unique index is the issuance idempotency guard;
  - `IssuanceUseCase` loads the application and the lottery phase for the event, the count and the holder identity;
  - `ApplicantIdentity` and `VerificationRequirement` are declared in the lottery files;
  - the platform fee is a 5% constant.
- **Missing:**
  - Stripe calls that create a PaymentIntent carry no idempotency key or metadata;
  - no push notification type exists for a win or a purchase;
  - events are published to JetStream directly after the database commit, so an event is lost if publishing fails after the commit;
  - there is no tax-inclusive handling and no buyer fee.

Payments use separate charges and transfers with the platform as the Stripe merchant (payments-design.md). Connected accounts are transfer-only recipients. Mail goes through the Postmark account already used by Zitadel.

The design was revised on 2026-10-08 after a review found:
- a race between the expiry sweeper and placing a purchase (B1, B2);
- leaked card holds (B3);
- an ownership check after the Order lookup (B4);
- a charged-but-unissued dead end (M1);
- an unspecified event payload and email dedupe (M3, M4);
- legal gaps on the final confirmation (M7).

D2, D3, D4, D6 and D7 below carry the fixes.

## Goals / Non-Goals

**Goals:**
- A sale never oversells, and a fan is never charged for tickets they do not receive.
- No double hold, double charge or double issuance from a double tap, a retry, a reload or two open tabs.
- Every recorded purchase reliably produces its confirmation email, push and journey update, each retried on its own.
- Lottery winners get the same confirmation email and push as checkout buyers. The lottery's application and draw are unchanged.

**Non-Goals:**
- Folding `LotterySalesPhase` into `TicketSale` and renaming the scraped `SalesPhase` (planned names: `TicketSale` with method Lottery, `AnnouncedSale`). That is a later change; this one only introduces `TicketSale` with method FirstCome.
- Non-card payment methods, buyer fees, ticket types, waitlists, fan-initiated cancellation, 適格請求書 receipts, SMS phone verification, eKYC on a sale, `on_behalf_of` charges.
- A grace period or extension for lapsed holds (decided 2026-10-08: a hold is exactly 15 minutes).
- A sold-out event or analytics consumer. A sold-out signal for official resale is added when resale is built; the SoldOut state is derived from the sold count.
- A waiting room or queue for high-demand sales: pilot sales spread over days at a small venue.

## Decisions

### D1 — Names: `TicketSale` and `Reservation`

- **`TicketSale` is the first-party sale.** Industry terms for this are "on-sale", "release" and "ticket type", and schema.org has `Offer`. "Sales phase" is an internal term, and `SalesPhase` is already the scraped entity. `TicketSale` carries a sale method so that the lottery can be folded in later.
- **`Reservation` is one checkout.** Its essence is the hold on stock. `Purchase` was rejected because it overlaps with `Order`, which already means "paid".

### D2 — Authorize, commit while holding, capture

```
Start ------> Reservation Held (exactly 15 min, counted in stock) ------> Authorize (PaymentIntent, manual capture, 3DS)
(ReservationUseCase.Start)                                                (ReservationUseCase.Authorize, only while holding)
                                                                                |
Place purchase (IssuanceUseCase.IssueFromReservation)                           v
  --> Reservation.Commit: UPDATE ... WHERE status = 'held' AND hold_expire_at > now
        |-- Committed --> capture --> RecordCapture --> Order.Issue (Order + Tickets + Settlement + outbox row,
        |                                                Reservation Completed, one transaction)
        +-- NotHeld   --> fail; the expiry sweeper releases the hold and the card hold
```

- **Commit only while holding (decided 2026-10-08, option (a)).** A holding Reservation's tickets are already counted against the stock, so a commit never needs a stock check and never oversells. A lapsed hold is final; the fan starts again.
  - Rejected: a grace period after the hold. It needs a "lapsed but stock still free" commit path with a no-stock branch, a cancel-and-release flow and a sweeper threshold, and it created the sweeper race the review found.
- **Commit and the expiry sweeper are disjoint by time.** Commit requires `hold_expire_at > now`. The sweeper's `Release(Expired)` requires `status = 'held' AND hold_expire_at <= now`. Both are single conditional UPDATEs, so at most one of them can win for a Reservation, whatever the interleaving. `Release` never touches a Committed row; only `RevertCommit` does, and only when there is no `capture_at` (D7).
- **Why keep the authorization at all.** It runs 3DS before the commit and lets the commit happen before any money moves, so a commit that fails costs the fan nothing. It also reuses the lottery's port and confirm guard.
- **Options considered:**
  - Stripe Checkout with a webhook. Its minimum session expiry is 30 minutes, and the payment-intent webhooks would all be new.
  - Immediate capture. A failure after the charge becomes charge-then-refund.
- **Known pitfalls:**
  - A cancelled authorization can stay visible for days on some statements. The checkout and the email say "not charged".
  - Stripe fees apply on capture only.

### D3 — Idempotency and duplicate requests

- **Start is idempotent by its natural key.** "Get or create the holding Reservation for (user, sale)" is backed by a partial unique index on Held rows. A concurrent second insert loses and reads the winner. Starting again with another count replaces the hold only when the new one can be created; the replaced Reservation's card hold is released by the sweeper (D7). The server generates the id (UUIDv7, `entity.NewID`).
  - Considered: a client-generated id. The browser cannot generate UUIDv7 natively, the id would need validating, and its embedded clock could not be trusted.
  - Considered: an AIP-155 `request_id`. A second key adds nothing over the natural key.
- **Placing the purchase is serialised per Reservation (re-review N1).** `IssueFromReservation` takes a row lock on the Reservation (`SELECT ... FOR UPDATE` on `reservations`) for the whole call: verify, commit, capture, `RecordCapture` and `Order.Issue`. The lock is held across the Stripe capture call, which is acceptable at pilot volume and only blocks callers of the same Reservation. A concurrent fan double tap, or the stalled-checkout job, waits and then takes the idempotent path: an existing Order or a recorded `capture_at`.
- **Placing the purchase is idempotent by state.**
  - `IssueFromReservation` checks ownership first, then returns an existing Order (spec: `usecase/order/issue-from-reservation`).
  - `Commit` reports Committed again for a Committed or Completed Reservation.
  - The `capture_at` recorded by `RecordCapture` stops any second capture, so the 24-hour Stripe idempotency window never matters.
  - The unique `orders.reservation_id` turns a second `Order.Issue` into AlreadyExists, which returns the first Order.
- **Capture is classified by PaymentIntent status, not HTTP status (re-review N1).** After any capture error the port retrieves the PaymentIntent:
  - `succeeded` → success, returning the charge and card facets. This makes a repeat capture safe however late it is, beyond Stripe's 24-hour idempotency-key window.
  - `canceled`, or a `requires_capture` that the card network refuses → FailedPrecondition.
  - `processing`, 409 `idempotency_key_in_use`, network errors and 5xx → Unavailable.

  Today's port maps by HTTP status (`pkg/api/errors.go`), which would turn a canceled hold into InvalidArgument and an in-flight duplicate into AlreadyExists. The ticket-sale path uses this status-based mapping.
- **The card-hold port is parameterised per caller (review M8).**
  - The lottery passes "reject American Express" and the key prefix `lottery`.
  - The ticket sale passes "accept every brand" and the prefix `ticket-sale`.
  - Keys: `ticket-sale-authorize:<reservation_id>`, `ticket-sale-capture:<pi>`, `ticket-sale-cancel:<pi>`.

  One PaymentIntent per Reservation; a declined card retries on the same PaymentIntent, as Stripe recommends. Metadata carries `reservation_id`, `ticket_sale_id`, `event_id` and `trace_id`, and never personal data.
- **The OTel trace id is not a dedupe key.** The fan app's fetch instrumentation starts a new trace per request, so a retry has a different trace id. It is recorded on the Reservation and in the Stripe metadata only, for correlation.

### D4 — Stock and limits

- **Counts.** `ticket_sales.sold_count` holds the tickets on Committed and Completed Reservations. Held = the sum of counts of Held rows with `hold_expire_at > now`. Remaining = quantity − sold_count − held.
- **Concurrency for Start (review M9).** `GetOrCreateHeld` runs in one transaction that first locks the sale row (`SELECT ... FOR UPDATE` on `ticket_sales`). It then computes held and the user's committed tickets, checks stock and limit, expires or releases the user's previous Held row, and inserts the new one. Serialising Starts per sale is cheap at pilot volumes and makes "two fans, last ticket" exact.
- **Commit and revert.** `Commit` moves Held to Committed and adds the count to `sold_count` in the same statement batch under the sale-row lock. `RevertCommit` does the reverse for an uncharged commit.
- **Per-account limit.** Checked once at Start against Committed and Completed tickets plus the new count. A user holds at most one Reservation per sale, so Commit does not check it again.
- **Sold out.** Derived as `sold_count = quantity`. Raising the quantity reopens the sale. A refund or dispute of a first-come Order voids its tickets but does not return them to the stock; the seats are covered by official resale later.

### D5 — Order source and issuance

- **Order source.** `orders.application_id` becomes nullable, and a nullable `reservation_id` is added. A CHECK requires exactly one of the two, and each has its own unique index. Proto `Order` gets a `oneof source`. Each Order also gets `confirmation_sent_at` (D6).
- **Issuance.** The shared core is extracted: Order, N Tickets, a Held Settlement with the Organizer split at the Organizer's fee rate, and the outbox row. `IssueFromCapturedWin` and `IssueFromReservation` load their sources and call it. For a Reservation, the amount is the Reservation's amount, which `VerifyAuthorization` has already matched against the hold; the payment reference and card facets come from `RecordCapture`.
- **Identity type.** `ApplicantIdentity` becomes `HolderIdentity` in a shared file. The lottery's proto keeps a deprecated alias for one release; the frontend lottery screens switch to the new name in this change.

### D6 — Transactional outbox, two consumers

- **The outbox row is written in the issuance transaction** (`Order.Issue`: "the purchase, announced as TicketPurchased"). Its payload carries the Order id, buyer, event, ticket count, amount and source. A stable id (the Order id) lets JetStream deduplicate.
- **A relay publishes it.** The relay runs in the API process, polls with `FOR UPDATE SKIP LOCKED`, publishes with `PublishEventWithID` and marks the row sent. This is a shared mechanism that resale and check-in will reuse; existing best-effort publishers are not migrated in this change.
- **Consumers (decided 2026-10-08: only these two):**
  - **`NotificationUseCase.NotifyTicketPurchased`** sends the email, then the push.
    - The email is deduplicated by `orders.confirmation_sent_at`, set right after a successful Postmark send. Postmark has no idempotency key, so a crash between the send and the update can send twice; nothing else can.
    - The push goes through `NotificationUseCase.Deliver` (type `ticket_purchased`). A rerun after the push can push twice, which is accepted.
  - **`TicketJourneyUseCase.MarkPaid`**.

  Lottery wins produce `TicketPurchased` too, so winners get the email and push. Failed messages go back through JetStream redelivery and then to the existing poison queue, which is alerted on.
- **Considered: a confirmation sweeper instead of the outbox** (`confirmation_sent_at` IS NULL, every minute). It is simpler for two side effects, but the user chose event-driven delivery for retry isolation and per-consumer responsibility, and the outbox is needed again for resale and check-in.

### D7 — Sweepers

Two 1-minute jobs, like the existing `IssueDueWins` and payout sweepers, both driven by `Reservation.ListDue`:
- **`ReservationUseCase.ReleaseExpired`** handles two cases:
  - Held rows whose hold has expired become Expired (conditional on still being Held).
  - Every Expired or Released row with an `authorization_ref` and no `authorization_released_at` gets `CancelAuthorization` and then `RecordAuthorizationRelease`. This covers lapsed holds, holds replaced by a new Start, and commits reverted after a failed capture (review B3).
- **`IssuanceUseCase.IssueDueReservations`** reruns `IssueFromReservation` for rows Committed more than 1 minute ago: a crash between commit and capture, a capture that hit Unavailable, or an issuance failure after the charge.
- **Charged but not issued (review M1).**
  - A Committed row with `capture_at` is never charged again and can never be released (entity rule).
  - If it is still not Completed 10 minutes after `capture_at`, the job logs an error with the reservation id each run, and an alert on that log pages the operator.
  - The operator fixes the cause (for example the Organizer row), and the next run issues the Order.
  - Refunding is a manual Stripe-dashboard action recorded in the runbook, because no Order exists for `RefundOrder` to act on.
- **Capture errors.** They are classified as in D3:
  - FailedPrecondition (the hold was released or expired, or the card was closed) reverts the commit, so the stock is freed.
  - Every other error leaves the row Committed for the sweeper.
- **Money on an ended checkout (re-review N1, safety net).** If `CancelAuthorization` on an Expired or Released Reservation reports the hold was already charged, `ReleaseExpired` logs an operator error every run. The same alert as the 10-minute rule pages the operator. Both reports are spec requirements (`release-expired`, `issue-due-reservations`), so they are tested.
- **A cancelled concert stops the checkout at the last step (re-review N2).** `IssueFromReservation` checks `Event.IsEventPublished` before committing, so a hold started before a 中止 is never charged.

`payment_intent.amount_capturable_updated` is not needed for correctness, because the server confirms synchronously and the sweepers cover crashes. It is left out.

### D7b — Proto shape

The proto conventions settled in `ticket-wallet-and-checkin` (one service per package, bare-verb RPCs, AIP-142 `*_time`) apply:
- **Fan services.** `rpc.ticket_sale.v1.TicketSaleService` (Get) and `rpc.reservation.v1.ReservationService` (Start, Get, Authorize, Confirm). `ReservationService.Get` lets the checkout explain a failed step (review M2), instead of overloading error codes.
- **Organizer service.** `rpc.organizer.ticket_sale.v1.TicketSaleService` (Configure, Get). Get runs `TicketSaleUseCase.GetOwn`, which returns the counts the fan-facing Get hides.
- **Admin service.** `rpc.admin.organizer.v1.OrganizerService` gains UpdateSellerDetails and SetPlatformFeeRate.
- **Entities.**
  - `entity.v1.TicketSale` with `sale_start_time` and `sale_end_time`.
  - `entity.v1.Reservation` with `hold_expire_time`, `commit_time` and `capture_time`.
  - `Order` gets `oneof source { TicketApplicationId application_id; ReservationId reservation_id; }`.
- **Fee rate.** It is an integer in basis points with a protovalidate range of 0 to 3000.

### D8 — Fan identity and seller details

- **Fan identity.** The 本人確認 name and phone (E.164) are stored on `User` in the application database, as `User` already mirrors email and name from Zitadel. This keeps checkout and issuance in one database and transaction and works while Zitadel is degraded. It also keeps identity data for business use out of the IdP. SMS verification can later use Zitadel's phone verification or a direct SMS and mirror the verified flag. The checkout prefills from `User`, and an edit updates it. Each Ticket keeps a copy for its face.
- **Seller details.** Seller details live on `Organizer` and are entered by an admin at vetting. Omitting the address and phone number "on request" for individual sellers is not offered; the pilot Organizer is a corporation.

### D9 — Fee rate

- **Rate.** `Organizer.platform_fee_rate` is stored in basis points (the specs' "hundredths of a percent"): 0 to 3000, default 800 for new Organizers, pilot 500.
- **Split.** The Organizer's split is `amount − floor(amount × rate ÷ 10000)`, so rounding still favours the Organizer.
- **Snapshot.** The rate is copied onto the Settlement at issuance, so a later rate change never alters an issued Order's split.
- **Cancellation refunds.** On a cancellation refund, the platform keeps bearing the unreturned card fee during the pilot. Making the Organizer bear it needs a deduction mechanism, tracked under payments-legal-compliance / #996.

### D10 — Emails, receipts and legal copy

- **No Stripe `receipt_email`.** It would name the platform as the seller under separate charges and transfers, and it is not a 適格請求書. `on_behalf_of` would fix the name but needs the `card_payments` capability on connected accounts, against the transfer-only design. That is noted for the 収納代行 counsel review.
- **The confirmation email is ours.** It carries the 特商法 seller details, the resale prohibition and the no-cancellation statement.
- **Final confirmation (特商法 §12-6) and covered ticket (チケット不正転売禁止法).** The checkout's final screen lists:
  - quantity, price and total 税込;
  - the payment method and timing;
  - the delivery timing;
  - the sale period;
  - the cancellation policy, including no cooling-off;
  - the resale prohibition, shown 販売に際し;
  - the seller details.

  It offers a way back to correct the count and identity (訂正手段). The wording is reviewed by counsel under payments-legal-compliance §2.2 before the livemode gate.

### D11 — Accepted limitations for the pilot

- **One event can have both a lottery phase and a TicketSale.** Nothing stops it; the console offers only the first-come editor for the pilot, and the lottery fold-in change adds the exclusivity rule.
- **Moving the event's start time earlier after a sale exists** is not re-validated against the sale end. The runbook tells the Organizer to adjust the sale end first.
- **Apple Pay on the web** needs the payment domain registered with Stripe for the fan origin (task 6.4).

## Risks / Trade-offs

- **[Risk] A fan finishing card authentication right at 15 minutes loses the hold.** → Accepted (option (a)). The countdown is visible from the first step, and the copy says "not charged".
- **[Risk] A cancelled authorization shows on a debit card for days.** → The copy says "not charged", and the sweeper releases holds within 2 minutes of the hold ending.
- **[Risk] Charged but not issued.** → Never re-charged or released; alerted after 10 minutes; the runbook covers manual refund (D7).
- **[Risk] Outbox relay lag delays emails.** → The relay polls every second, and the outbox depth and poison queue are alerted on.
- **[Risk] The default fee changes from 5% to 8%.** → The rate is snapshotted per Settlement, existing Organizers are set explicitly in the migration, and the pilot Organizer gets 500.
- **[Risk] The lottery issuance is refactored, and winners now get an email.** → Its existing tests stay green, and a regression test is added for a lottery win producing `TicketPurchased` and one email.
- **[Trade-off] One sale per event and one ticket type.** → Enough for the pilot. Tiers come with the lottery fold-in.
- **[Risk] `public-event-page` is still in flight.** → The event route delta in this change is applied after it archives. The checkout route is self-contained.

## Migration Plan

1. specification: proto changes → Release → BSR.
2. backend: in one migration,
   - add `ticket_sales`, `reservations` and `outbox`;
   - make `orders.application_id` nullable, add `reservation_id` with the CHECK and the unique indexes, and add `confirmation_sent_at`;
   - add the organizer seller and fee columns, setting `platform_fee_rate` to 500 for existing Organizers, so nothing changes until an admin sets it;
   - add the user identity columns;
   - add `settlements.platform_fee_rate`.

   Then the relay, the consumers, the usecases and the sweepers.
3. frontend: the checkout and event ticket section, the organizer sale editor, and the admin fields.
4. Stripe stays in test mode until the payments-legal-compliance launch gate (verified by task 8.2).

Rollback:
- **Before any first-come sale has run:** the migration's down step drops the new tables and columns.
- **After a sale has run:** orders with a `reservation_id` exist, and `application_id` can no longer be made NOT NULL again. Rollback is then forward-only: disable the sale in the console and keep the schema.

## Open Questions

- The exact Postmark message stream and template ids. They are fixed at implementation.
- The outbox relay's poll interval and its alert threshold. They are tuned after the first load test.
