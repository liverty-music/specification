## 0. Dependency gate

- [ ] 0.1 Confirm `ticket-wallet-and-checkin` is archived, so the main specs carry its lottery rules and `entity/ticket/list-by-holder-and-event` (design D13); verify `openspec/specs/components/entity/ticket/list-by-holder-and-event/spec.md` exists on main
- [ ] 0.2 Read production row counts and a sample of `lottery_sales_phases`, `ticket_applications`, `orders` and `tickets` through the db-proxy runbook (read-only), and record them in design.md "Migration Plan"; verify that only test data exists, or stop and ask the user

## 1. Specification — main specs and follow-up notes

- [ ] 1.1 Edit the main spec Purposes directly (design D12), and verify `openspec validate --specs` and `scripts/check-spec-layout.py` pass:
  - `components/entity/order`: `buyer` → `user`, `application` → `lottery entry`, and the erDiagram `LotteryEntry ||--o| Order`;
  - `components/entity/ticket`: `holder` → `user`; remove the holder full name and holder phone number rows; "verified identity … set only when the sale required verification";
  - `components/entity/user`: add the full name and phone number rows, and `User ||--o{ LotteryEntry`.
- [ ] 1.2 Once 0.1 holds, add the deltas on specs that `ticket-wallet-and-checkin` brings to main, and verify `openspec validate unify-ticket-sales --strict` passes:
  - `components/entity/ticket/list-by-holder-and-event`: REMOVED (migration to `list-by-user-and-event`);
  - `components/usecase/ticket/admit`: MODIFIED to read `Ticket.ListByUserAndEvent`;
  - the fan tickets route: MODIFIED so the ticket face shows the User's full name and phone instead of the holder full name.

  `rename-reception-to-scanner` copies its MODIFIED blocks for these specs after this change archives.
- [ ] 1.3 Add to the counsel list in `docs/payments-design.md` the question whether 特定興行入場券 evidence needs the name and phone confirmed at sale to be kept (design D8); verify the line is in the open-questions list
- [ ] 1.4 Open the plan PR from a worktree cut from origin/main (README "Branch work in this repository"), staging only `openspec/changes/unify-ticket-sales`, the main specs edited in 1.1 and `docs/payments-design.md`; verify `openspec-checks.yml` passes and the PR merges

## 2. Proto (specification → BSR)

- [ ] 2.1 Rewrite `entity/v1/ticket_sale.proto` from `components/entity/ticket-sale`:
  - fields: `TicketSaleId`, `SeriesId`, a `TicketSaleName` value message (1-100), `TicketSaleMethod` (LOTTERY now; FIRST_COME stays reserved for `first-come-ticket-sales`), `start_time`, `end_time`, `VerificationRequirement`, `drawn_time`;
  - drop the per-event fields;
  - add `entity/v1/ticket_type.proto` from `components/entity/ticket-type`: price 1-1,000,000, quantity >= 1, `per_account_limit` 1-10.

  Verify `buf lint` and `buf format -d` pass
- [ ] 2.2 Replace `entity/v1/lottery_application.proto` with `lottery_entry.proto` (design D7):
  - `LotteryEntry`, `LotteryEntryId`, `LotteryEntryState` with ENTERED=1, WON=2, LOST=3, WITHDRAWN=4;
  - fields `ticket_type_id`, `user_id`, `requested_ticket_count`, `authorization`, `state`, `draw_position`;
  - remove `LotterySalesPhase`, `LotterySalesPhaseId`, the deprecated `ApplicantIdentity` and `HolderIdentity`.

  Verify `buf lint` passes
- [ ] 2.3 `user.proto`: add `FullName` (1-200) and `PhoneNumber` (E.164 pattern) value messages and the `full_name` and `phone_number` fields; un-reserve nothing. `order.proto`: `buyer_id` → `user_id`, `application_id` → `lottery_entry_id`. `ticket.proto`: `holder_id` → `user_id`, remove `holder_identity`. `organizer.proto`: replace `seller_details` with `legal_name`, `representative_name`, `business_address`, `business_phone_number`, `contact_email`. Verify the protovalidate rules match the entity specs and `buf lint` passes
- [ ] 2.4 Services (design D11), each with doc comments matching the adapter specs:
  - `rpc/organizer/ticket_sale/v1/ticket_sale_service.proto`: `Create`, `List` (required `event_id`), `SetVerificationRequirement`;
  - remove `rpc/organizer/lottery/v1`;
  - replace `rpc/lottery/v1` with `rpc/lottery_entry/v1/lottery_entry_service.proto`: `CreateAuthorization`, `Create`, `Get`, `Withdraw`, `GetResult`, all keyed by `ticket_type_id`;
  - remove `SellerDetails` from the fan `TicketSaleService.GetResponse` in favour of the Organizer fields.

  Verify `buf lint` passes
- [ ] 2.5 Open the proto PR from a worktree with the `buf skip breaking` label, merge, and cut a Release; verify `buf-release.yml` succeeds and BSR has the new version

## 3. Backend — migration (design "Migration Plan")

- [ ] 3.1 Write one Atlas migration:
  - create `ticket_sales` and `ticket_types` with `UNIQUE (ticket_sale_id, event_id)`;
  - copy each `lottery_sales_phases` row into one sale named 抽選 and one ticket type;
  - rename `ticket_applications` to `lottery_entries` with `ticket_type_id` and `user_id`, rewrite state 5 to 4, and recreate the active-entry unique index as `uq_lottery_entries_active (ticket_type_id, user_id)`;
  - add `users.full_name` and `users.phone_number` with the E.164 CHECK, filled from the newest entry or ticket per user;
  - drop `applicant_*` and `tickets.holder_full_name` / `holder_phone_number`;
  - rename `orders.buyer_id`, `orders.application_id` and `tickets.holder_id`;
  - drop `lottery_sales_phases`.

  Verify the migration applies to a fresh database after every earlier migration, `make lint-schema` passes, and the prod Atlas overlay registers it
- [ ] 3.2 Add a migration test that loads two phases, three applications (one withdrawn with state 5), one order and two tickets, applies the migration, and checks the rows. Verify the test passes, and that each user's name and phone equal their newest application's

## 4. Backend — entities

- [ ] 4.1 `TicketSale` (`components/entity/ticket-sale`); verify one unit test per scenario: Lottery window within bounds, Lottery window shorter than 1 day, Lottery window longer than 14 days, End not after start, Named sale, Empty name, No requirement given, Verified-any or JPKI-only, Before start, Between start and end, At end, Back to back, Overlapping, Drawn time set, Drawn time absent
- [ ] 4.2 `TicketType` (`components/entity/ticket-type`); verify one unit test per scenario: Valid sizing, No limit given, Limit larger than the quantity, Limit larger than one admission code, Price out of range, Two tickets, Presale winner in a general sale with the same limit, Topping up to a higher limit
- [ ] 4.3 Rename `TicketApplication` to `LotteryEntry` (design D7) and key it by ticket type (`components/entity/lottery-entry`); verify one unit test per scenario: New entry, Count within the limit, Zero tickets requested, Count over the limit, Withdrawn entry is not active, Drawn entry is active, Entered entry, Drawn or withdrawn entry, American Express, Other or unknown brand
- [ ] 4.4 `User` personal details (`components/entity/user` "Personal details") and the Ticket face (`components/entity/ticket` "Every ticket is a covered ticket"); verify unit tests: Details complete, Domestic-format phone number, Phone number too long, Not given yet, Issued ticket face, User corrects their details, Resale flag cannot be false
- [ ] 4.5 Remove `entity/lottery_sales_phase.go`, `ApplicantIdentity` and the holder fields on `Ticket`; rename `Order.BuyerID` / `ApplicationID` and `Ticket.HolderID` to `UserID` / `LotteryEntryID`; verify `make check` passes

## 5. Backend — entity operations (contract tests against Postgres and Stripe test mode)

- [ ] 5.1 `TicketSaleRepository.Create / Get / ListByEvent / ListDueForDraw / UpdateVerificationRequirement` and `TicketType.Get` (design D10); verify one contract test per scenario of `components/entity/ticket-sale/{create,get,list-by-event,list-due-for-draw,update-verification-requirement}` and `components/entity/ticket-type/get`: Sale stored, Unknown event, Same event twice, Existing sale, Unknown id (each operation), Presale and general sale, Sale covering several events, No sale, Closed and undrawn, Still open, Already drawn, Requirement changed, Existing ticket type
- [ ] 5.2 `LotteryEntryRepository` operations; verify one contract test per scenario of `components/entity/lottery-entry/{create,get,get-by-ticket-type-and-user,list-entered-for-ticket-type,get-ticket-type-stats,persist-draw-outcome,update-state}`:
  - create: First entry, Active entry exists, Entry for another event of the same sale, Re-entry after withdrawal, Unknown ticket type
  - get: Existing entry, Unknown id
  - get-by-ticket-type-and-user: Active entry exists, Only withdrawn entries, Never entered
  - list-entered-for-ticket-type: Mixed states, No candidates
  - get-ticket-type-stats: After the draw, Withdrawn entries excluded, No entries
  - persist-draw-outcome: Outcome recorded, Failure leaves nothing recorded, Empty draw
  - update-state: State changed, Unknown id
- [ ] 5.3 `LotteryEntry.RunLotteryDraw` (pure) and the card hold operations renamed from the application; verify the existing tests pass under the new names for every scenario of `components/entity/lottery-entry/{run-lottery-draw,create-authorization,verify-authorization,capture-authorization,cancel-authorization}`, with the idempotency key prefix taken from the sale
- [ ] 5.4 `Order.GetByLotteryEntryID / ListLotteryEntryIDsAwaitingIssuance / ListByUser`, `Ticket.ListByUser / ListByUserAndEvent` and `User.UpdatePersonalDetails`; verify one contract test per scenario: Issued entry, Not yet issued, Won without order, Already issued, Not won, Paid and refunded orders, No orders, User with tickets, Voided tickets included, No tickets, Group of tickets, No tickets for the event, First details, Correction, Invalid phone number, Unknown user

- [ ] 5.5 Deletions follow the new tables (`components/entity/{concert/delete-and-suppress,organizer/delete,user/delete}`); verify the existing contract tests pass with the new names: Concert with fan journeys, Series stays, Concert with issued tickets, Unknown id, Slot already suppressed, Organizer with a published Series, Refunded purchase, Active Organizer, Paid order, Settlement, Payout account, Existing user, Purchases outlive the user, Empty id

## 6. Backend — usecases (unit tests with the operations mocked)

- [ ] 6.1 `TicketSaleUseCase.Create` (`components/usecase/ticket-sale/create`); verify unit tests: Another organizer's series, Event of another series, Event not published, Start time not yet announced, Doors-open time not announced, Invalid configuration, General sale after the presale, Overlapping sale, Other events are not affected, Tour presale
- [ ] 6.2 `TicketSaleUseCase.ListOwnByEvent` and `SetVerificationRequirement`; verify unit tests: Drawn presale and upcoming general sale, Event without a sale, Another organizer's event, Requirement tightened while open, After the draw, Unknown sale, Another Organizer's sale
- [ ] 6.3 `LotteryUseCase.Enter` and `CreateAuthorization` (`components/usecase/lottery-entry/{enter,create-authorization}`); verify unit tests:
  - enter: Fan enters within the window, Window closed, Count over the limit, Presale winner reaches the limit, Missing identity details, Second entry, Hold does not verify, Re-entry after withdrawal, No verified identity, Verification not active, Active verification
  - create-authorization: Hold opened in an open window, Window not open, Count over the limit, Card payments unavailable
- [ ] 6.4 `LotteryUseCase.DrawDueSales` and `RunDraw`, with the 1-minute job renamed; verify unit tests:
  - draw-due-sales: Window closes, Window still open, Drawn once, One sale fails
  - run-draw: Winners charged losers released, Each ticket type is drawn against its own quantity, Losers ordered for the waitlist, No entries, Winner's card was closed, Release fails for one loser, After the draw
- [ ] 6.5 `LotteryUseCase.GetMyEntry`, `GetResult` and `WithdrawEntry`; verify unit tests: Entered entry, Only withdrawn, Fan won, Fan lost, Draw not run, Withdrawn or never entered, Withdraw before the draw, Window closed but not drawn, Already drawn, Another fan's entry, Release fails
- [ ] 6.6 `IssuanceUseCase.IssueFromCapturedWin` and `IssueDueWins`, `TicketUseCase.GetOrder` and `GetMyTickets` (modified specs); verify unit tests: Won application issued, Replayed issuance, Concurrent issuance, Application not won, Payment not captured, Organizer unresolved, Phase required verification, Verified identity missing, No requirement, Journey updated, Journey update fails, Won application, Issuance fails, Own order, Another buyer's order, Unknown order, Fan with tickets, Fan without tickets, and `UserUseCase.Delete`: Existing user, Unknown user, User holding a ticket, User with only refunded purchases, Retry after the record failed

## 7. Backend — adapters and release

- [ ] 7.1 Organizer `TicketSaleService` handler (`components/adapter/organizer/api/rpc/ticket-sale`), replacing `organizer_lottery_handler.go`; verify handler tests: Active Organizer creates a sale, Tenant with no Organizer, Deactivated Organizer, Sale without ticket types, List without an event
- [ ] 7.2 Fan `LotteryEntryService` handler (`components/adapter/fan/api/rpc/lottery`); verify handler tests: Fan enters, Not signed in, Caller without an account, Withdraw own entry, No entry, Zero tickets, Domestic-format phone number, E.164 phone number
- [ ] 7.3 Upgrade the generated package to the 2.5 release, run `make check`, open the backend PR citing the change, and merge; verify the AtlasMigration applies in production and the rollout is healthy

## 8. Other changes' artifacts (specification)

- [ ] 8.1 Update `first-come-ticket-sales` to build on this model, and verify `openspec validate first-come-ticket-sales --strict` passes:
  - `FirstCome` as a second method of `TicketSale`, with the sold count, price lock and window rule on `TicketSale` / `TicketType`;
  - `Reservation` → `Checkout` in specs, design and tasks;
  - the holder name and phone removed from `Checkout`;
  - `user/update-holder-identity` replaced by this change's `user/update-personal-details`;
  - seller details replaced by the Organizer fields of task 2.3;
  - its `ticket-sale` entity and organizer RPC specs rewritten as deltas on this change's specs.
- [ ] 8.2 List in `first-come-ticket-sales/design.md` what its backend branch `worktree-first-come-ticket-sales` must change to rebase onto task 3.1's tables (`ticket_sales` shape, `ticket_types`, `reservations` → `checkouts`, no holder columns); verify the list covers every table and column the branch adds
- [ ] 8.3 Move the two ADDED requirements of `identity-ekyc-jpki` from `usecase/lottery-sales-phase/set-phase-verification-requirement` and `usecase/ticket-application/apply` to `usecase/ticket-sale/set-verification-requirement` and `usecase/lottery-entry/enter`; verify `openspec validate identity-ekyc-jpki --strict` passes
- [ ] 8.4 Rename `ResaleListing.seller` to `holder` in `official-resale` (specs, design, tasks); verify `grep -rn "seller" openspec/changes/official-resale` finds only the legal term 販売業者 (seller of record) in prose

## 9. Frontend

- [ ] 9.1 Fan lottery entry screen (`components/infrastructure/fan/web/route/lottery-apply`):
  - route parameter `ticketTypeId`;
  - shows the sale name, event, price and limit;
  - prefills the saved name and phone;
  - calls `LotteryEntryService`.

  Verify component tests: Returning fan, First entry, Presale entry, and the existing phone entry scenarios
- [ ] 9.2 Organizer lottery editor (`components/infrastructure/organizer/web/route/lottery-phase-editor`) creates a named lottery sale through `TicketSaleService.Create`, and the lottery status screen reads `TicketSaleService.List` for the event; verify component tests: Presale for one event, Missing name, Overlapping window, Blank form, Window too long, Start time not set
- [ ] 9.3 Upgrade the generated clients to the 2.5 release, run `make check`, open the frontend PR citing the change, and merge; verify the production rollout is healthy

## 10. Production verification

- [ ] 10.1 Update the lottery E2E (`stories/win-tickets-in-a-lottery`) and run it in production with the Stripe Sandbox; verify each scenario passes: Demand within capacity, Oversubscribed phase, Withdraw and re-apply, Organizer still in identity check, Presale winner at the limit, Presale winner below the limit
- [ ] 10.2 Read the migrated rows in production read-only (sales, ticket types, entries, users' name and phone); verify the counts match task 0.2
