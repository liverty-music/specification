## 1. Proto and plan (specification)

- [ ] 1.1 Add `SeatType` and `TicketStock` entity messages and the organizer `SeatTypeService` (Create, Delete, ListBySeries) and `TicketStockService` (Create, Delete, ListByEvent) per the rpc-design skill; remove `TicketType`, the organizer `TicketTypeService` and every `ticket_type_id` field; add the per-account limit to the event messages of the Series RPCs; change `Order` (Pending and Void statuses, Failed removed, ticket stock, ticket count, referral code, card authorization, optional payment fields), `Checkout` (order, required sale; no amount, resale flag or referral code; no `SetReferralCode`), `ResaleListing` (ticket stock, no checkout), `LotteryEntry` (order, sale) and `TicketSale` (event IDs; fan and organizer `ListByEvent` return the event's stocks with seat type name, price, state and whether resale is open); verify `make check` (buf lint, format, forbidden words) passes
- [ ] 1.2 Open the plan PR with the `buf skip breaking` label, together with the rewritten `make-lottery-draw-durable` and `unify-order-issuance` and the new `resell-tickets-by-lottery`; merge once `CI Success` passes, cut the Release and confirm `buf-release.yml` succeeds (`gh run list --repo liverty-music/specification --workflow buf-release.yml --limit 3`)

## 2. Prod pre-check before deleting sales data (cloud-provisioning, backend)

- [ ] 2.1 Add `pannpers@pannpers.dev` to the prod ESC list `pulumiConfig.gcp.cloudSqlUsers`, apply it, run the read-only grant (cloud-provisioning `docs/runbooks/cloud-sql-access.md` "Adding a developer"); verify a read-only login succeeds and `INSERT` fails
- [ ] 2.2 Check read-only in prod, as in design "Migration Plan" step 1, that no sale of a Series with an Organizer is open, no Settlement is Held or waiting for payout, and every captured payment of an Order is settled or refunded in the Stripe dashboard (the pilot charged real money, #1074); record the result and the row counts that will be deleted in design.md, and stop the migration on any failed check

## 3. Schema (backend)

- [ ] 3.1 Add the Atlas migration of design "Migration Plan" and D1-D8, D12 (delete Organizer sales' data; delete discovered sales without an end time and name the others by method; drop `drawn_at` and `lottery_result_at`; `seat_types`, `ticket_stocks`, `ticket_sale_events`, event per-account limit, Order columns and Pending/Paid/Refunded/Void statuses, `order_id` on entries and checkouts, required `checkouts.ticket_sale_id`, `seat_types` foreign key `ON DELETE RESTRICT`, the one-entry-per-sale-and-event uniqueness, `resale_listings` on stocks without `checkout_id`, `ticket_types` dropped) and update `schema.sql`; verify `atlas migrate validate`, `make lint-schema` and a `migrationtest` that loads an Organizer's lottery and first-come sales with entries, checkouts, Orders, Tickets, Settlements and a resale listing, plus a discovered sale, applies the migration, and finds every Organizer sale record gone, the discovered sale kept and the new tables empty

## 4. Entities (backend: components/entity/seat-type, ticket-stock, event, ticket-sale, order, checkout, lottery-entry, resale-listing, card-authorization, referral)

- [ ] 4.1 Add the SeatType and TicketStock entities and their rules; verify one unit test per scenario of `entity/seat-type` and `entity/ticket-stock`
- [ ] 4.2 Add the per-account limit and the application fit rule to Event; verify one unit test per scenario of `entity/event` "Per-account limit" and "An account's application fits the event"
- [ ] 4.3 TicketSale names its events; verify the scenarios of `entity/ticket-sale` "An Organizer's sale names events, a discovered sale none"
- [ ] 4.4 Order gains Pending and Void and loses Failed, and gains the ticket stock, count, referral code and card authorization; verify one unit test per scenario of `entity/order`
- [ ] 4.5 Checkout and LotteryEntry keep only their own attributes and name their Order and sale (a Checkout always a FirstCome sale, with no resale branch); ResaleListing (no Checkout, withdrawable while open), CardAuthorization and the referral code follow; verify one unit test per scenario of `entity/checkout`, `entity/lottery-entry`, `entity/resale-listing` and `entity/card-authorization`
- [ ] 4.6 Delete the TicketType entity, its repository, mocks and tests; verify `make check` has no remaining reference

## 5. Entity operations (backend)

- [ ] 5.1 SeatType Create, Get, Delete, ListBySeries and TicketStock Create, Get, Delete (removing Void Orders with their checkouts and entries, refused while a Void Order's card authorization is not yet released), ListByEvent with counts aggregated from Orders (design D1, D5, D8); verify one contract test per scenario of each `entity/seat-type/*` and `entity/ticket-stock/*` spec
- [ ] 5.2 `Order.GetHeldForEvent` (counting only Pending Orders that still hold or may receive tickets) and the changed Order reads (`get-event-id`, `list-by-event`, `list-by-user`, `list-referral-stats-by-event`, `get-by-checkout-id`, `get-by-lottery-entry-id`, `list-lottery-entry-ids-awaiting-issuance`, `issue`); verify one contract test per scenario of each `entity/order/*` spec
- [ ] 5.3 `Checkout.GetOrCreateHeld` stores the Pending Order with the Held Checkout under the users-row then stock-row locks of design D4/D5, and `Commit`, `RevertCommit`, `Release`, `ListDue`, `ListByUser`, `SetCardAuthorization`, `RecordCardAuthorizationRelease`, `GetByCardAuthorizationID` follow; remove `SetReferralCode` and the resale hold; verify one contract test per scenario of each `entity/checkout/*` spec, plus an rdb test that runs two `GetOrCreateHeld` for one fan on two stocks of one event at once and finds at most the limit held
- [ ] 5.4 `LotteryEntry.Create` stores the Pending Order with the entry under the users-row lock; `PersistDrawOutcome` voids the Lost entries' Orders; the list, stats and lookup operations take the sale and stock; verify one contract test per scenario of each `entity/lottery-entry/*` spec
- [ ] 5.5 TicketSale operations (`create`, `get`, `list-by-event`, `list-due-for-draw`, `list-with-pending-milestones`, `set-window`, `set-verification-requirement`, `upsert-discovered`) read and write the sale's events, with no draw time or lottery result time and a name and end time on every sale (design D12); verify one contract test per scenario of each `entity/ticket-sale/*` spec
- [ ] 5.6 `CardAuthorization.Create`/`Get`, `ResaleListing.Create`/`Withdraw`, `Series.CreateDraft`/`Update`, `Concert.DeleteAndSuppress` and `Organizer.Delete` follow the new model; verify one contract test per scenario of their specs (`make test-stripe-e2e` for the card authorization)
- [ ] 5.7 Add an rdb concurrency test of design D5 on one TicketStock: run `GetOrCreateHeld` for the last tickets, `Commit` of another holding Checkout, `RevertCommit` of a third and `PersistDrawOutcome` of a lottery on the same stock at the same time, many rounds; verify the sold plus held count never exceeds the quantity, no call deadlocks, and the counts read afterwards equal the Orders' ticket counts

## 6. Usecases (backend)

- [ ] 6.1 `SeatTypeUseCase` (Create, Delete, ListBySeries) and `TicketStockUseCase` (Create, Delete, ListByEvent); verify one unit test per scenario of each `usecase/seat-type/*` and `usecase/ticket-stock/*` spec
- [ ] 6.2 `SeriesUseCase.Create`/`Update` carry the per-account limit, fixed once the event is published; verify one unit test per scenario of `usecase/series/create` and `update`
- [ ] 6.3 `TicketSaleUseCase` Create, SetWindow, ListByEvent, ListOwnByEvent, ScanDueReminders and DiscoverForArtist on events and stocks, Create refusing a missing end time, the `RESULT_DAY` stage removed with its content (`entity/ticket-sale-reminder`, `already-sent`), and `TicketSale.SearchPublishedSales` returning only named sales with an end time (verify against its integration test with real pages); verify one unit test per scenario of each `usecase/ticket-sale/*` spec
- [ ] 6.4 `CheckoutUseCase.Start` and `ReleaseExpired` (Order fit check, only an open FirstCome sale, refused while a closed lottery of the event is not drawn (design D6), voiding); verify one unit test per scenario of `usecase/checkout/start` and `release-expired`
- [ ] 6.5 `LotteryEntryUseCase` AuthorizeCard, Confirm, ListByTicketType and RunDraw (draw per stock against its remaining count); verify one unit test per scenario of each `usecase/lottery-entry/*` spec
- [ ] 6.6 `OrderUseCase.IssueFromCapturedWin` and `IssueFromCheckout` make the Pending Order Paid instead of creating it, with no resale branch; `ResaleListingUseCase.Create` accepts every ticket of a sold-out stock and `Withdraw` any open listing of the fan; verify one unit test per scenario of `usecase/order/issue-from-captured-win`, `issue-from-checkout` and `usecase/resale-listing/create` and `withdraw`
- [ ] 6.7 Delete `TicketTypeUseCase.Update` with its tests and mocks; verify `make check`

## 7. Adapters (backend)

- [ ] 7.1 Upgrade the generated package; add the organizer `SeatTypeHandler` and `TicketStockHandler`, remove `TicketTypeHandler`, and change the fan checkout, lottery entry and ticket sale handlers and the organizer ticket sale handler; verify one handler test per scenario of each `adapter/*/api/rpc/*` spec in this change

## 8. Stories (backend integration)

- [ ] 8.1 Rewrite the first-come, lottery, resale and referral story integration tests on seat types and stocks; verify against the Stripe test API (`STRIPE_INTEGRATION_TEST=1`) every scenario of `stories/buy-tickets-first-come`, `win-tickets-in-a-lottery`, `resell-a-ticket` and `attribute-a-purchase-to-a-referral-link`, including a presale winner topping up in the general sale, a fan refused a second seat type, and a first-come and a lottery-won ticket listed for resale (no purchase: it arrives with `resell-tickets-by-lottery`)
- [ ] 8.2 Add the organizer setup to the `run-an-event-from-the-organizer-console` story test (seat types, stocks, limit, sale on events); verify its scenarios

## 9. Frontend (fan)

- [ ] 9.1 Upgrade the generated package; the event page lists each sale's stocks with seat type name, price, state and resale and lets the fan pick one seat type (only the held one when the fan already holds tickets of the event); the checkout, lottery entry and tickets screens and the legal document follow; verify the component tests of `infrastructure/fan/web/route/{event,checkout,lottery-entry,tickets}` and `fan/web/global/legal-document`, and `make check`
- [ ] 9.2 Run with Playwright on a local build against stubbed RPCs: pick A席 on an event with S席 and A席, buy 2 first come, then reopen the event and see only A席 offered; enter a lottery for one date of a two-date sale and enter the other date too

## 10. Frontend (organizer console)

- [ ] 10.1 The concert page manages seat types, the concert editor sets each date's per-account limit and stocks, the sale editor picks events instead of price, quantity and limit, and the event page shows stocks and sales; guide and i18n follow; verify the component tests of `infrastructure/organizer/web/route/{concert,concert-editor,event,ticket-sale-editor,guide}` and `organizer/web/global/i18n`, and `make check`
- [ ] 10.2 Run with Playwright on a local build against stubbed RPCs: add S席 8000 yen and A席 6000 yen to a concert, give a date 100 S席 and 200 A席 with a limit of 4, create a lottery presale on that date, and see the event page list both stocks and the sale; try to delete S席 and see it refused while its stock exists, then delete the stock (only an abandoned checkout's Void Order names it) and S席

## 11. Release and production check

- [ ] 11.1 Take a Cloud SQL backup, merge the backend PR, cut the release and confirm in prod (read-only) that the AtlasMigration is applied, `ticket_types` is gone, no Organizer sale record remains and the discovered sales counted in 2.2 are still there, the fan-api rollout finished, and `gh workflow run stripe-sandbox-e2e.yml` succeeds
- [ ] 11.2 Merge the fan and organizer frontend PRs, cut the releases and confirm the rollouts

## 12. Follow-up change (specification)

- [ ] 12.1 Propose the rename of the operations still named after TicketType (design D11); verify it appears in `openspec list`
