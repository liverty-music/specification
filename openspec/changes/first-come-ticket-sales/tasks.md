## 0. Dependency gate

- [ ] 0.1 Confirm `public-event-page` is archived, so the `components/infrastructure/fan/web/route/event` delta in this change has a main spec to apply to; verify `openspec/specs/components/infrastructure/fan/web/route/event/spec.md` exists on main
- [ ] 0.2 Confirm the proto conventions of `ticket-wallet-and-checkin` (one service per package, bare verbs, `*_time`) are released, and build on that release; verify the BSR version in use contains `rpc.organizer.reception_link.v1`

## 1. Proto (specification → BSR)

- [ ] 1.1 Add `entity.v1.TicketSale` from the `components/entity/ticket-sale` attribute table: ids as wrapper messages, `sale_start_time` / `sale_end_time`, a `TicketSaleMethod` enum with FIRST_COME, price 1-1,000,000, quantity >= 1, per-account limit 1-10, and a `TicketSaleState` enum (NOT_YET_ON_SALE, ON_SALE, ALL_HELD, SOLD_OUT, ENDED); verify `buf lint` and `buf format` pass
- [ ] 1.2 Add `entity.v1.Reservation` from `components/entity/reservation`: `ReservationId`, a status enum, `hold_expire_time`, `commit_time`, `capture_time`, amount and holder identity. Move `ApplicantIdentity` to a shared `HolderIdentity`, keeping a deprecated alias for one release; verify `buf lint` passes
- [ ] 1.3 `Order`: `oneof source { application_id; reservation_id }` (D5). `Organizer`: a seller details message and `platform_fee_rate_bps` (0-3000). `User`: holder full name and phone (E.164 pattern). `NotificationType`: gains TICKET_PURCHASED. Verify the protovalidate rules match the entity specs
- [ ] 1.4 Add the services, each with doc comments matching the adapter specs:
  - `rpc.ticket_sale.v1.TicketSaleService.Get`
  - `rpc.reservation.v1.ReservationService.Start / Get / Authorize / Confirm`
  - `rpc.organizer.ticket_sale.v1.TicketSaleService.Configure / Get`
  - `rpc.admin.organizer.v1.OrganizerService.UpdateSellerDetails / SetPlatformFeeRate`

  Verify `buf lint` passes
- [ ] 1.5 Open the specification PR from a worktree, with `buf skip breaking` if `Order.application_id` moving into a oneof is flagged; merge and cut a Release; verify `buf-release.yml` succeeds and BSR has the new version

## 2. Backend — schema and entities

- [ ] 2.1 Write the migration (D4, D5, D9, Migration Plan); verify `atlas migrate lint` passes and the prod Atlas overlay registers the file. It contains:
  - `ticket_sales` with `sold_count`;
  - `reservations`, with a partial unique index on Held rows per (user, sale) and `capture_at`, `authorization_released_at`, payment reference and card facets;
  - `outbox`;
  - `orders.application_id` made nullable, `orders.reservation_id` with the exactly-one CHECK and a unique index per source, and `orders.confirmation_sent_at`;
  - organizer seller-detail columns and `platform_fee_rate_bps`, 500 for existing rows and 800 by default;
  - user holder-identity columns;
  - `settlements.platform_fee_rate_bps`.
- [ ] 2.2 `TicketSale` entity: rules, remaining count, sale state, LowStock (rounded up) and price lock (`components/entity/ticket-sale`); verify one unit test per scenario: Usual sale, End before start, Limit over 10, Some sold some held, Before opening, Last tickets held by others, Sold out, Few left, Small sale last ticket, Closed, Price change before anyone checked out, Price change after a checkout
- [ ] 2.3 `Reservation` entity (`components/entity/reservation`): new hold, holding, a charged checkout never released, holder identity; verify unit tests for New checkout, Within the hold, Hold lapsed, Charged checkout, Domestic-format phone number
- [ ] 2.4 `Order` exactly-one-source, `Organizer` seller details and fee rate, and `User` holder identity rules (`components/entity/order`, `organizer`, `user`); verify unit tests for Order from a checkout, Two sources, Corporation with all details, Address missing, New Organizer, Rate over the bound, Saved identity, Domestic-format phone number
- [ ] 2.5 Settlement fee from the Organizer's rate, snapshotted on the Settlement (`components/entity/settlement` "Platform fee rate"); verify unit tests for Round order amount, Pilot rate, Amount that does not divide evenly, Fee rounds down to zero, Rate changed after issuance

## 3. Backend — entity operations (contract tests against Postgres and Stripe test mode)

- [ ] 3.1 `TicketSale.Create / Get / GetByEvent / Update`, with Update as one conditional statement under the sale-row lock; verify one contract test per scenario of `components/entity/ticket-sale/{create,get,get-by-event,update}`, including Fewer than sold and held under a concurrent hold
- [ ] 3.2 `Reservation` store operations, with contract tests for every scenario of `components/entity/reservation/{get-or-create-held,get,set-authorization,commit,release,revert-commit,record-capture,record-authorization-release,list-due}`. Double tap and Two fans last ticket are run concurrently, and Committed just before the sweep runs as a concurrent Commit and Release around the hold expiry. The operations are:
  - `GetOrCreateHeld`: sale-row lock, stock and limit check, replace only on success (D4);
  - `Get` and `SetAuthorization`;
  - `Commit`: conditional on Held and before the expiry;
  - `Release`: conditional on Held, and for Expired after the expiry;
  - `RevertCommit`: conditional on Committed and no `capture_at`;
  - `RecordCapture`, `RecordAuthorizationRelease` and `ListDue`.
- [ ] 3.3 `Order.Issue` writes the Order, Tickets, Settlement and the outbox row, and completes the Reservation, in one transaction; it refuses a Reservation that is not Committed and charged. Add `Order.GetByReservationID`. Verify contract tests for Order issued, Order issued from a checkout, Reservation not charged, Failure stores nothing, Second order for the application, Second order for the reservation, Paid checkout, Checkout not paid
- [ ] 3.4 `Organizer.SetSellerDetails / SetPlatformFeeRate` and `User.UpdateHolderIdentity`; verify contract tests per scenario
- [ ] 3.5 Parameterise the card-hold port per caller (D3), and classify capture outcomes by PaymentIntent status for the ticket-sale path: `succeeded` → success with facets, `canceled` → FailedPrecondition, in-flight/409/network/5xx → Unavailable. Cover Repeated a day later and Capture already in progress with a stubbed client. The lottery passes "reject American Express" and the prefix `lottery`, which is today's behaviour. The ticket sale passes "accept all" and the prefix `ticket-sale`. PaymentIntent metadata carries `reservation_id`, `ticket_sale_id`, `event_id` and `trace_id`. Verify contract tests in Stripe test mode for every scenario of `components/entity/reservation/{create,verify,capture,cancel}-authorization`, and that the lottery's port tests still pass
- [ ] 3.6 `Order.SendConfirmationEmail` through Postmark's transactional stream: it sends only when `confirmation_sent_at` is unset and then sets it. Verify contract tests for Email sent, Redelivered event and Mail unavailable against a Postmark test server token
- [ ] 3.7 Outbox relay (D6): poll with `FOR UPDATE SKIP LOCKED`, publish with `PublishEventWithID` (the Order id) and mark the row sent. Verify an integration test that a row written in a committed transaction is published once even when the first publish fails, and that a rolled-back transaction publishes nothing

## 4. Backend — usecases (unit tests with operations mocked)

- [ ] 4.1 `TicketSaleUseCase.Configure / Get / GetOwn`; verify one unit test per scenario of `components/usecase/ticket-sale/{configure,get,get-own}`, including Concert cancelled
- [ ] 4.2 `ReservationUseCase.Start / Get / Authorize / ReleaseExpired`; verify one unit test per scenario of `components/usecase/reservation/*`, including Fan reloads mid-checkout, Count changed after authorizing, Committed at the last moment, Replaced by a newer checkout and Money taken on an ended checkout
- [ ] 4.3 Extract the shared issuance core (D5) and implement `IssuanceUseCase.IssueFromReservation` and `IssueDueReservations`. The ownership check comes first, the call holds the Reservation row lock throughout (D3), the holding and published-event checks precede the card check, a charged Reservation is never captured again, and capture errors are mapped as in D3/D7. Concurrency tests cover Double tap on the action and Fan and the stalled-checkout job at once against Postgres. Move the ticket journey update out of `IssueFromCapturedWin`. Verify unit tests per scenario of `components/usecase/order/{issue-from-reservation,issue-due-reservations,issue-from-captured-win}`, and that the existing lottery issuance tests still pass
- [ ] 4.4 `NotificationUseCase.NotifyTicketPurchased` (email then push, Japanese and English copy, lottery wins included), the `Deliver` caller change and `TicketJourneyUseCase.MarkPaid`; verify unit tests per scenario of `components/usecase/notification/{notify-ticket-purchased,deliver}` and `components/usecase/ticket-journey/mark-paid`
- [ ] 4.5 `OrganizerUseCase.UpdateSellerDetails / SetPlatformFeeRate`; verify unit tests per scenario

## 5. Backend — boundaries, consumers and jobs

- [ ] 5.1 Fan handlers `TicketSaleService.Get` (no sign-in) and `ReservationService.Start / Get / Authorize / Confirm` (`components/adapter/fan/api/rpc/{ticket-sale,reservation}`); verify handler tests per scenario
- [ ] 5.2 Organizer handler `TicketSaleService.Configure / Get` (Get runs `GetOwn`), behind the organizer-console sign-in and `ResolveCaller` (`components/adapter/organizer/api/rpc/ticket-sale`); verify handler tests per scenario
- [ ] 5.3 Admin handler additions (`components/adapter/admin/api/rpc/organizer`); verify handler tests for Non-admin sets a rate, Missing OrganizerId, Missing rate, Admin reads any Organizer and Admin records seller details
- [ ] 5.4 JetStream consumers for `TicketPurchased`, one for notification and one for the ticket journey, idempotent by Order id, with the poison queue after the redelivery limit; verify consumer tests that a redelivery produces one email and leaves the journey Paid
- [ ] 5.5 1-minute jobs for `ReleaseExpired` and `IssueDueReservations`, wired like the existing issuance sweeper. Add an error log and an alert for the two operator reports — charged more than 10 minutes ago and not Completed, and a charged hold on an ended checkout (D7) — plus a runbook entry for the manual refund. Verify the jobs run in the API process, and that a test row that cannot be issued fires the alert in dev logs
- [ ] 5.6 Postmark sender identity for transactional mail: the cloud-provisioning secret and DNS are already in place; add the server token for the backend through ESO. Verify the backend pod reads the token in prod
- [ ] 5.7 `make check` passes in backend

## 6. Frontend — fan app

- [ ] 6.1 Event page ticket section (`components/infrastructure/fan/web/route/event` "Ticket section shows the sale"): content by sale state, LowStock without counts, sale start in Japan time, and guest buy returning through sign-up; verify component tests per scenario
- [ ] 6.2 Checkout route (`components/infrastructure/fan/web/route/checkout`); verify component tests per scenario and a Storybook story per step. It covers:
  - the count, with the 税込 total and a countdown that resumes on reload;
  - the prefilled identity, with the lottery-apply phone rule;
  - the card form, with Apple Pay and Google Pay through the Payment Element;
  - the 特商法 final confirmation, listing every item, with a way back to correct the details;
  - the place-purchase action, showing the amount, with a double-submit guard;
  - the outcome screens, chosen through `ReservationService.Get`.
- [ ] 6.3 Switch the lottery screens to `HolderIdentity` before the deprecated alias is removed; verify `make check`
- [ ] 6.4 Register the fan app's domain for Apple Pay with the payment provider in test and live mode; verify the Apple Pay button appears in Safari on an iPhone on the test sale
- [ ] 6.5 `make check` passes in frontend

## 7. Frontend — organizer and admin apps

- [ ] 7.1 Ticket sale editor (`components/infrastructure/organizer/web/route/ticket-sale-editor`), reached from the event in the console's concert list: defaults, times in Japan time, field errors, the price lock, the quantity floor and prerequisite messages; verify component tests per scenario
- [ ] 7.2 Admin console Organizer screen: a seller details form and a platform fee rate field (no spec yet; the follow-up spec is noted in proposal.md); verify manually in dev that an admin can set both and that Get returns them
- [ ] 7.3 `make check` passes in frontend

## 8. Release and verification

- [ ] 8.1 Release order: spec → BSR → backend (migration first) → frontend; verify the prod pin includes both releases
- [ ] 8.2 Verify that paid ticketing runs in Stripe test mode: the prod publishable and secret keys are test-mode keys, and a PaymentIntent created on prod shows `livemode=false`
- [ ] 8.3 Set the pilot Organizer's seller details and its rate to 5% through the admin console; verify Get returns them
- [ ] 8.4 Run the E2E on production in Stripe test mode with a test event (`stories/buy-tickets-first-come`): Two tickets bought, Last ticket two fans, Hold ran out, Double tap everywhere, Fan closes the tab; verify each scenario passes and the confirmation email arrives
- [ ] 8.5 Sync the delta specs to the main specs, applying the (Purpose) edits listed in proposal.md, and archive the change after `public-event-page`
