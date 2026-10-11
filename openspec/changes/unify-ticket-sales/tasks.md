## 0. Dependency gate

- [x] 0.1 Confirm `ticket-wallet-and-checkin` is archived, so the main specs carry its lottery rules and `entity/ticket/list-by-holder-and-event` (design D13); verify `openspec/specs/components/entity/ticket/list-by-holder-and-event/spec.md` exists on main (archived in #1113 on 2026-10-10; the spec exists at 56186a6d)
- [ ] 0.2 Read production row counts and a sample of `lottery_sales_phases`, `ticket_applications`, `ticket_sales`, `reservations`, `orders`, `tickets` and the `users` holder columns through the db-proxy runbook (read-only), and record them in design.md "Migration Plan"; verify that only test data exists, or stop and ask the user
- [x] 0.3 Confirm `first-come-ticket-sales` is archived, so the main specs carry its `ticket-sale`, `reservation`, `user`, `organizer` and `order` specs (design D13); verify `openspec/specs/components/entity/ticket-sale/spec.md` and `openspec/specs/components/entity/reservation/spec.md` exist on main (archived in #1118 on 2026-10-11; both specs exist at 065d36ff)

## 1. Specification — main specs, follow-up deltas and notes

- [x] 1.1 Once 0.3 holds, edit the main spec Purposes directly (design D12), and verify `openspec validate --specs` and `scripts/check-spec-layout.py` pass:
  - `components/entity/order`: `buyer` → `user`, `application` → `lottery entry`, `reservation` → `checkout`, and the erDiagram `LotteryEntry ||--o| Order`;
  - `components/entity/ticket`: `holder` → `user` (including the "never changes" row); remove the holder full name and holder phone number rows; "verified identity … set only when the sale required verification";
  - `components/entity/user`: replace the holder rows with the full name and phone number rows, and `User ||--o{ LotteryEntry`;
  - `components/entity/organizer`: the seller details become the Organizer fields of task 2.3.
- [x] 1.2 Once 0.3 holds, rewrite this change's deltas onto the specs that `ticket-wallet-and-checkin` and `first-come-ticket-sales` brought to main (proposal "Capabilities of `first-come-ticket-sales`"), and verify `openspec validate unify-ticket-sales --strict` passes:
  - `components/entity/ticket/list-by-holder-and-event`: REMOVED (migration to `list-by-user-and-event`);
  - `components/usecase/ticket/admit`: MODIFIED to read `Ticket.ListByUserAndEvent`, and the personal-data requirement without "the holder's name";
  - `components/entity/ticket` "A ticket is admissible only once and only while Issued": MODIFIED, "the holder was admitted" → "the user was admitted";
  - the fan tickets route: MODIFIED so the ticket face shows the User's full name and phone instead of the holder full name;
  - `entity/ticket-sale`, `ticket-sale/create`, `ticket-sale/get`, `adapter/organizer/api/rpc/ticket-sale`: ADDED → MODIFIED/REMOVED; the first-come rules (sold count, held count, remaining count, sale state, LowStock, price lock) move to `entity/ticket-type` (design D3); `ticket-sale/get-by-event` → `list-by-event`; `ticket-sale/update` → `ticket-sale/set-window` and `ticket-type/update`; `usecase/ticket-sale/{configure,get,get-own}` → `create`, `set-window`, `list-own-by-event`, a new `usecase/ticket-type/update` and the fan `ListByEvent` read; the edit rules of design D11 (a Lottery sale until its window opens, a FirstCome sale under the price lock); the boundary of `SetWindow` in `adapter/organizer/api/rpc/ticket-sale` and a new `adapter/organizer/api/rpc/ticket-type` for `TicketTypeService.Update`;
  - `entity/user`: the holder identity requirement → the personal details requirement; `user/update-holder-identity` REMOVED;
  - `reservation/*` → `checkout/*` and the other replacements in the proposal, each REMOVED at the old path and ADDED at the new one;
  - `usecase/order/issue-from-captured-win`: one delta that keeps the removal of "Ticket journey becomes Paid" that `first-come-ticket-sales` made;
  - the first-come checkout start and the fan event page apply the per-account limit of design D5.

  `rename-reception-to-scanner` and `migrate-discovered-sales` copy their MODIFIED blocks for these specs after this change archives.
- [x] 1.3 Add to the counsel list in `docs/payments-design.md` the question whether 特定興行入場券 evidence needs the name and phone confirmed at sale to be kept (design D8); verify the line is in the open-questions list
- [x] 1.4 Once 0.3 holds, write MODIFIED deltas for the specs renamed by the RPC naming rule (proposal "Capabilities renamed by the RPC naming rule", design D11): the method names in `adapter/fan/api/rpc/{concert,artist,follow,ticket,ticket-journey,user,notification,push-notification}`, `adapter/admin/api/rpc/{concert,organizer,artist,user}`, `adapter/organizer/api/rpc/organizer` and the routes that name them, and the removal of `user_id` from their requests (design D15). Behavior is unchanged. Verify `openspec validate unify-ticket-sales --strict` passes and every old RPC name (`TicketService.GetOrder`, `FollowService.ListFollowed`, `ConcertService.ListPending`, `OrganizerService.ListArtists`, `ArtistService.CreateOfficialSite`, `ListByFollower`) appears in the change's specs only in REMOVED, RENAMED or Migration text
- [x] 1.5 Write the RPC naming rule of design D11 (rule table, entity-named services, packages, AIP-132/136 deviation and its rejected alternatives, worked examples) as a repository skill in `specification/.claude/skills/` that loads when a `.proto` file or an adapter spec is written and overrides the user-scope protobuf skill where they differ; shorten `AGENTS.md:148` to the review criteria with a pointer to the skill, and update the `agent-rules` block of `CLAUDE.md` that copies it; verify the skill's rule table matches design D11
- [ ] 1.6 Move `openspec/specs/components/entity/verified-identity` to `entity/kyc` and rename `VerifiedIdentity` to `Kyc` in every main spec that names it (design D16), as a pure rename; rename the requirement "Verified identity binding" and its scenario "Verified identity missing" of `usecase/order/issue-from-captured-win` once the move lands (a MODIFIED block cannot drop a scenario); verify `openspec validate --specs`, `scripts/check-spec-layout.py` and `openspec validate unify-ticket-sales --strict` pass and `grep -rni "verified identit" openspec/specs` finds nothing
- [x] 1.7 Open the plan follow-up PR from a worktree cut from origin/main (README "Branch work in this repository"; the plan itself merged in #1102), staging only `openspec/changes/unify-ticket-sales`, `openspec/changes/rename-reception-to-scanner` (task 8.3), the main specs edited in 1.1, `AGENTS.md`, `CLAUDE.md` and `docs/payments-design.md`; verify `openspec-checks.yml` passes and the PR merges

## 2. Proto (specification → BSR)

- [x] 2.1 Rewrite `entity/v1/ticket_sale.proto` from `components/entity/ticket-sale`, and add `entity/v1/ticket_type.proto` from `components/entity/ticket-type`:
  - `TicketSale`: `TicketSaleId`, `SeriesId`, a `TicketSaleName` value message (1-100), `TicketSaleMethod` (`FIRST_COME = 1` kept, `LOTTERY = 2` added), `sale_start_time` and `sale_end_time` (names kept), `VerificationRequirement`, `drawn_time`, and `repeated TicketType ticket_types`;
  - `TicketType`: `TicketTypeId`, `TicketSaleId`, `EventId`, price 1-1,000,000, quantity >= 1, `per_account_limit` 1-10, and OUTPUT_ONLY `sold_count`, `held_count`, `state` and `low_stock` for a first-come type;
  - reserve the per-event field numbers of the old `TicketSale`.

  Verify `buf lint` and `buf format -d` pass
- [x] 2.2 Replace `entity/v1/lottery_application.proto` with `lottery_entry.proto` and `reservation.proto` with `checkout.proto` (design D7):
  - `LotteryEntry`, `LotteryEntryId`, `LotteryEntryState` with ENTERED=1, WON=2, LOST=3, WITHDRAWN=4, DRAFT=5 (design D7, D14); fields `ticket_type_id`, `user_id`, `requested_ticket_count`, `authorization` (optional on a Draft), `state`, `draw_position`;
  - `Checkout`, `CheckoutId`, `CheckoutStatus`, keyed by `ticket_type_id`;
  - remove `LotterySalesPhase`, `LotterySalesPhaseId`, the deprecated `ApplicantIdentity` and `holder_identity.proto`.

  Verify `buf lint` passes
- [x] 2.3 Entity fields (design D8, D9), and verify the protovalidate rules match the entity specs and `buf lint` passes:
  - `user.proto`: add `FullName` (1-200) and `PhoneNumber` (E.164 pattern) value messages and the `full_name` and `phone_number` fields; remove `holder_identity = 9` and reserve 9;
  - `order.proto`: `buyer_id` → `user_id`; in the `source` oneof, `application_id` → `lottery_entry_id` and `reservation_id` → `checkout_id`;
  - `ticket.proto`: `holder_id` → `user_id`, remove `holder_identity`;
  - `organizer.proto`: replace `seller_details` with `legal_name`, `representative_name`, `business_address`, `business_phone_number`, `contact_email`; this also changes the Organizer embedded in `series.proto`.
- [x] 2.4 Services (design D11), each with doc comments matching the adapter specs:
  - `rpc/organizer/ticket_sale/v1/ticket_sale_service.proto`: `Create`, `ListByEvent`, `SetWindow`, `SetVerificationRequirement`; remove `Configure` and `Get`;
  - `rpc/organizer/ticket_type/v1/ticket_type_service.proto`: `Update` (price, quantity, per-account limit);
  - remove `rpc/organizer/lottery/v1`;
  - replace `rpc/lottery/v1` with `rpc/lottery_entry/v1/lottery_entry_service.proto` (design D14): `Start(ticket_type_id, ticket_count)`, `Authorize(lottery_entry_id, full_name, phone_number)`, `Confirm(lottery_entry_id)`, `Withdraw(lottery_entry_id)`, `ListByTicketType(ticket_type_id)`;
  - replace `rpc/reservation/v1` with `rpc/checkout/v1/checkout_service.proto`: `Start(ticket_type_id, ticket_count)`, `Get`, `Authorize` with `full_name` and `phone_number` instead of `holder_identity`, `Confirm`;
  - fan `rpc/ticket_sale/v1`: replace `Get(event_id)` with `ListByEvent(event_id)`, returning the event's sales with their ticket type for the event, ordered by start time;
  - `rpc/order/v1/order_service.proto`: `Get(order_id)`; remove `TicketService.GetOrder`;
  - admin `rpc/admin/organizer/v1`: `UpdateSellerDetails` → `SetBusinessDetails`;
  - admin `rpc/admin/order/v1`: `Get(order_id)` returning the Order with its Settlement; admin `rpc/admin/settlement/v1`: remove `Get`, keep `List`;
  - remove `rpc/issuance/v1`.

  Verify `buf lint` passes and `grep -rn -i "seller\|holder\|buyer\|applicant\|reservation" proto/` finds only reserved names, and `grep -rn "TicketApplication\|application_id" proto/` finds only reserved names
- [x] 2.5 Rename the other services' methods and remove the caller's `user_id` (design D11 "Other services", D15), each with doc comments matching the adapter specs of task 1.4:
  - `ConcertService`: `List(artist_id)` → `ListByArtist(artist_id)`, `ListByFollower` → `ListFollowed`;
  - admin `ArtistService.ListByOrganizer(organizer_id)` and organizer `ArtistService.List()`, removing both `OrganizerService.ListArtists`;
  - `FollowService.List`; `TicketJourneyService.List`;
  - `rpc/kyc/v1` `KycService` with `Start`, `Create`, `Recheck`, `Get()`, removing `rpc/identity/v1`; entity `VerifiedIdentity`/`VerifiedIdentityId` → `Kyc`/`KycId`, `VerificationLevel.IDENTITY_VERIFIED` → `KYC_VERIFIED`, the Ticket's verified identity reference → `kyc_id` (design D16);
  - `PushSubscriptionService`; `NotifyNewConcerts` on admin `NotificationService`;
  - admin `StagedConcertService`; `OfficialSiteService`;
  - `UserService.SetHome`, `SetPreferredLanguage`, and a new `UserService.Update` taking an optional `full_name` and `phone_number`, at least one (design D8); `NotificationService.Dismiss`; `SeriesService.RegenerateShareUrl`, `CreateMediaUploadUrl`;
  - no `user_id` on `UserService`, `NotificationService`, `PushSubscriptionService` or `KycService` requests.

  Verify `buf lint` passes, that no request of a per-user fan RPC has a `user_id` field, and that every service name is an entity name under `openspec/specs/components/entity/`
- [ ] 2.6 Open the proto PR from a worktree with the `buf skip breaking` label, merge, and cut a Release; verify `buf-release.yml` succeeds and BSR has the new version

## 3. Backend — migration (design "Migration Plan")

- [ ] 3.1 Write one Atlas migration, timestamped after `20261010020000` (`split-concert-from-event`), that reshapes the existing tables:
  - create `ticket_types` with `UNIQUE (ticket_sale_id, event_id)`; reshape `ticket_sales` (drop `uq_ticket_sales_event_id` and the per-event columns, add `series_id`, `name`, `verification_requirement`, `drawn_at`, methods 1 and 2);
  - move each first-come sale's per-event columns and sold count into one ticket type, and name the sale 一般発売;
  - copy each `lottery_sales_phases` row into one sale named 抽選 and one ticket type;
  - rename `ticket_applications` to `lottery_entries` with `ticket_type_id` and `user_id`, rewrite state 5 to 4, and recreate the active-entry unique index as `uq_lottery_entries_active (ticket_type_id, user_id)`;
  - rename `reservations` to `checkouts` keyed by `ticket_type_id`, with `uq_checkouts_held`;
  - rename `users.holder_*` to `full_name` / `phone_number` with their CHECKs, and fill empty ones from the newest application or ticket per user;
  - drop `applicant_*`, `tickets.holder_full_name` / `holder_phone_number`, `reservations.holder_*` and their phone CHECKs;
  - rename `orders.buyer_id`, `application_id`, `reservation_id` (with `chk_orders_one_source`), `tickets.holder_id` and `organizers.seller_*`;
  - drop `lottery_sales_phases`;
  - rename `verified_identities` to `kyc` and the tickets' verified identity reference column to `kyc_id` (design D16);
  - redo the `organizer-console-api` grants on `ticket_sales` and `ticket_types`.

  Verify the migration applies to a fresh database after every earlier migration, `make lint-schema` passes, and the prod Atlas overlay registers it
- [ ] 3.2 Add a migration test that loads two lottery phases, three applications (one withdrawn with state 5), one first-come sale with a committed and a held reservation, one order of each source, two tickets, and one user with holder values and one without; it applies the migration and checks the rows. Verify the test passes, that each user's name and phone equal their holder values or else their newest application's, and that the first-come ticket type keeps its sold count

## 4. Backend — entities

- [ ] 4.1 `TicketSale` (`components/entity/ticket-sale`); verify one unit test per scenario: Lottery window within bounds, Lottery window shorter than 1 day, Lottery window longer than 14 days, End not after start, Named sale, Empty name, No requirement given, Verified-any or JPKI-only, Before start, Between start and end, At end, Back to back, Overlapping, Drawn time set, Drawn time absent
- [ ] 4.2 `TicketType` (`components/entity/ticket-type`); verify one unit test per scenario: Valid sizing, No limit given, Limit larger than the quantity, Limit larger than one admission code, Price out of range, Two tickets, Presale winner in a general sale with the same limit, Topping up to a higher limit
- [ ] 4.3 Rename `TicketApplication` to `LotteryEntry` (design D7) and key it by ticket type (`components/entity/lottery-entry`); verify one unit test per scenario: New entry, Authorized draft, Draft without a hold, Already entered, Count within the limit, Zero tickets requested, Count over the limit, Withdrawn entry is not active, Draft or drawn entry is active, Draft or entered entry, Drawn or withdrawn entry, American Express, Other or unknown brand
- [ ] 4.4 `User` personal details (`components/entity/user` "Personal details") and the Ticket face (`components/entity/ticket` "Every ticket is a covered ticket"); verify unit tests: Details complete, Domestic-format phone number, Phone number too long, Not given yet, Issued ticket face, User corrects their details, Resale flag cannot be false
- [ ] 4.5 Remove `entity/lottery_sales_phase.go`, `ApplicantIdentity`, `User.HolderIdentity` and the holder fields on `Ticket` and `Reservation`; rename `Order.BuyerID` / `ApplicationID` / `ReservationID` and `Ticket.HolderID` to `UserID` / `LotteryEntryID` / `CheckoutID`, and the Organizer seller fields; rename `VerifiedIdentity` to `Kyc` and `IdentityVerificationUseCase` to `KycUseCase` (design D16); verify `make check` passes
- [ ] 4.6 Move the first-come rules from `TicketSale` to `TicketType` and rename `Reservation` to `Checkout` (design D3, D7); verify the existing unit tests pass under the new names for every scenario of the first-come `entity/ticket-sale` and `entity/reservation` specs as rewritten in task 1.2 (remaining count, sale state, LowStock, price lock, checkout states)

## 5. Backend — entity operations (contract tests against Postgres and Stripe test mode)

- [ ] 5.1 `TicketSaleRepository.Create / Get / ListByEvent / ListDueForDraw / SetWindow / UpdateVerificationRequirement` and `TicketType.Get / Update` (design D10); verify one contract test, marked `@spec`, per scenario of `components/entity/ticket-sale/{create,get,list-by-event,list-due-for-draw,set-window,update-verification-requirement}` and `components/entity/ticket-type/{get,update}`
- [ ] 5.2 `LotteryEntryRepository` operations; verify one contract test per scenario of `components/entity/lottery-entry/{get-or-create-draft,set-authorization,get,list-by-ticket-type-and-user,list-undrawn-for-ticket-type,get-ticket-type-stats,persist-draw-outcome,update-state}`:
  - get-or-create-draft: First start, Reload with the same count, Count changed, Double tap, Already entered, Entry for another event of the same sale, Re-entry after withdrawal, Unknown ticket type
  - set-authorization: Hold recorded, Not a draft, Unknown id
  - get: Existing entry, Unknown id
  - list-by-ticket-type-and-user: Active entry after a withdrawal, Never entered
  - list-undrawn-for-ticket-type: Mixed states, No candidates
  - get-ticket-type-stats: After the draw, Withdrawn and draft entries excluded, No entries
  - persist-draw-outcome: Outcome recorded, Failure leaves nothing recorded, Empty draw
  - update-state: State changed, Unknown id
- [ ] 5.3 `LotteryEntry.RunLotteryDraw` (pure), `LotteryEntry.GetByPaymentIntentRef` and the card hold operations renamed from the application; verify the existing tests pass under the new names for every scenario of `components/entity/lottery-entry/{run-lottery-draw,create-authorization,verify-authorization,capture-authorization,cancel-authorization,get-by-payment-intent-ref}`, with the idempotency key prefix taken from the sale
- [ ] 5.4 `Order.GetByLotteryEntryID / GetByCheckoutID / ListLotteryEntryIDsAwaitingIssuance / ListByUser`, `Ticket.ListByUser / ListByUserAndEvent` and `User.UpdatePersonalDetails`; verify one contract test per scenario: Issued entry, Not yet issued, Won without order, Already issued, Not won, Paid and refunded orders, No orders, User with tickets, Voided tickets included, No tickets, Group of tickets, No tickets for the event, First details, Correction, Invalid phone number, Unknown user, and the scenarios of `order/get-by-checkout-id`
- [ ] 5.5 Deletions follow the new tables (`components/entity/{concert/delete-and-suppress,organizer/delete,user/delete}`); verify the existing contract tests pass with the new names: Concert with fan journeys, Series stays, Concert with issued tickets, Unknown id, Slot already suppressed, Organizer with a published Series, Refunded purchase, Active Organizer, Paid order, Settlement, Payout account, Existing user, Purchases outlive the user, Empty id
- [ ] 5.6 `TicketSaleRepository.Update` (first-come, keyed by ticket type), `CheckoutRepository` (renamed from the reservation repository) and the Organizer field operations; verify the existing contract tests pass under the new names for every scenario of `components/entity/ticket-sale/update`, `components/entity/checkout/*` and the Organizer field operations as rewritten in task 1.2

## 6. Backend — usecases (unit tests with the operations mocked)

- [ ] 6.1 `TicketSaleUseCase.Create` for Lottery and FirstCome (`components/usecase/ticket-sale/create`); verify one unit test, marked `@spec`, per scenario of that spec
- [ ] 6.2 `TicketSaleUseCase.ListOwnByEvent`, `ListByEvent`, `SetWindow` and `SetVerificationRequirement`, and `TicketTypeUseCase.Update`; verify one unit test, marked `@spec`, per scenario of `components/usecase/ticket-sale/{list-own-by-event,list-by-event,set-window,set-verification-requirement}` and `components/usecase/ticket-type/update`
- [ ] 6.3 `LotteryUseCase.Start`, `Authorize` and `Confirm` (`components/usecase/lottery-entry/{start,authorize,confirm}`, design D14); verify unit tests:
  - start: Fan starts an entry within the window, Fan reloads mid-entry, Window closed, Count over the limit, Presale winner reaches the limit, Second entry, Re-entry after withdrawal, No verified identity, Verification not active, Active verification
  - authorize: Fan authorizes, Card declined fan retries, Someone else's entry, Missing identity details, Window closed, Card payments unavailable
  - confirm: Fan confirms, Confirmed twice, Hold does not verify, Draft without a hold, Window closed, Someone else's entry
- [ ] 6.4 `LotteryUseCase.DrawDueSales` and `RunDraw`, with the 1-minute job renamed; verify unit tests:
  - draw-due-sales: Window closes, Window still open, Drawn once, One sale fails
  - run-draw: Winners charged losers released, Unconfirmed draft at the draw, Each ticket type is drawn against its own quantity, Losers ordered for the waitlist, No entries, Winner's card was closed, Release fails for one loser, After the draw
- [ ] 6.5 `LotteryUseCase.ListOwnByTicketType` and `WithdrawEntry`; verify unit tests: Entered entry, Fan won, Fan lost, Never entered, Withdraw before the draw, Withdraw a draft, Window closed but not drawn, Already drawn, Another fan's entry, Release fails
- [ ] 6.6 `IssuanceUseCase.IssueFromCapturedWin` and `IssueDueWins`, `TicketUseCase.GetOrder` and `GetMyTickets` (modified specs); verify unit tests: Won application issued, Replayed issuance, Concurrent issuance, Application not won, Payment not captured, Organizer unresolved, Phase required verification, Verified identity missing, No requirement, Journey updated, Journey update fails, Won application, Issuance fails, Own order, Another buyer's order, Unknown order, Fan with tickets, Fan without tickets, and `UserUseCase.Delete`: Existing user, Unknown user, User holding a ticket, User with only refunded purchases, Retry after the record failed
- [ ] 6.7 The first-come usecases on the new model: the fan sale read, `CheckoutUseCase` (renamed from `ReservationUseCase`: start, get, authorize, release-expired), `IssueFromCheckout`, `IssueDueCheckouts`, `FulfillPayment` and the Organizer field update; verify the existing unit tests pass under the new names for every scenario of the specs rewritten in task 1.2, plus the per-account limit of design D5 at checkout start, the Kyc gate at checkout start and the Kyc binding at checkout issuance (design D3), the business-details check for both methods, `UserUseCase.Update` (`components/usecase/user/update`), and the fan read's choice of the current sale (design D11)

## 7. Backend — adapters and release

- [ ] 7.1 Organizer `TicketSaleService` handler (`components/adapter/organizer/api/rpc/ticket-sale`), reshaping the existing `organizer_ticket_sale_handler.go` and removing `organizer_lottery_handler.go` (rebase on backend #595 if it merged first, design D13), and the organizer `TicketTypeService` handler (`components/adapter/organizer/api/rpc/ticket-type`); verify one handler test, marked `@spec`, per scenario of both specs
- [ ] 7.2 Fan `LotteryEntryService` handler (`components/adapter/fan/api/rpc/lottery-entry`); verify handler tests: Fan starts an entry, Not signed in, Caller without an account, Withdraw own entry, Zero tickets, Domestic-format phone number, E.164 phone number
- [ ] 7.3 Fan `TicketSaleService`, `OrderService`, `CheckoutService` (renamed from the reservation handler), the payment-events webhook, the fan user handler, the admin `OrganizerService`, `OrderService` (with the Settlement) and `SettlementService`; verify the existing handler tests pass under the new names for every scenario of their adapter specs as rewritten in task 1.2
- [ ] 7.4 The other services' handlers renamed per task 2.5, and `RequireUserIDMatch` with its four call sites removed (design D15); verify the existing handler tests pass under the new names for every scenario of the adapter specs of task 1.4, and `git grep RequireUserIDMatch` finds nothing; remove the unserved issuance RPC types if any Go code imports them
- [ ] 7.5 Upgrade the generated package to the 2.6 release, run `make check`, open the backend PR citing the change, and merge; verify the AtlasMigration applies in production and the rollout is healthy

## 8. Other changes' artifacts (specification)

- [ ] 8.1 Move the two ADDED requirements of `identity-ekyc-jpki` from `usecase/lottery-sales-phase/set-phase-verification-requirement` and `usecase/ticket-application/apply` to `usecase/ticket-sale/set-verification-requirement` and `usecase/lottery-entry/start`, and rename `VerifiedIdentity` to `Kyc` in its artifacts (design D16); verify `openspec validate identity-ekyc-jpki --strict` passes
- [x] 8.2 Rename `ResaleListing.seller` to `user` and `matched_buyer` to `matched_user` in `official-resale`, and in its prose call the fans "the listing's user", "the matched user" and "the ticket's user" (design D9; decided with the user); verify `openspec validate official-resale --strict` passes and `grep -rni "seller\|holder\|buyer" openspec/changes/official-resale` finds only legal terms (it finds nothing)

- [x] 8.3 Rename `ScannerService.List(event_id)` to `ListByEvent` in `rename-reception-to-scanner` (proposal, design, tasks), per design D11; verify `openspec validate rename-reception-to-scanner --strict` passes and `grep -rn "List(ListRequest" openspec/changes/rename-reception-to-scanner` finds nothing

## 9. Frontend

- [ ] 9.1 Fan lottery entry screen (`components/infrastructure/fan/web/route/lottery-apply`):
  - route parameter `ticketTypeId`;
  - shows the sale name, event, price and limit;
  - prefills the saved name and phone;
  - calls `LotteryEntryService.Start`, `Authorize` and `Confirm`, and shows the entry as made only after `Confirm`;
  - the entry status screen reads `ListByTicketType`.

  Verify component tests: Returning fan, First entry, Presale entry, and the existing phone entry scenarios
- [ ] 9.2 Organizer lottery editor (`components/infrastructure/organizer/web/route/lottery-phase-editor`) creates a named lottery sale through `TicketSaleService.Create`, and the lottery status screen reads `TicketSaleService.ListByEvent` for the event; verify component tests: Presale for one event, Missing name, Overlapping window, Blank form, Window too long, Start time not set
- [ ] 9.3 First-come screens on the new model: the checkout route (`fan/web/route/checkout`, `CheckoutService`, name and phone prefilled from the User), the event page ticket section (`fan/web/route/event`, the current sale's ticket type, with the way to enter a lottery or buy first-come tickets), the settings screen's name and phone fields (`fan/web/route/settings`, `UserService.Update`), the organizer ticket sale editor (`organizer/web/route/ticket-sale-editor`, `TicketSaleService.Create` / `SetWindow` / `ListByEvent` and `TicketTypeService.Update`), and the admin Organizer screen (the Organizer fields); remove the `HolderIdentity` entity; verify the existing component tests pass under the new names for every scenario of these routes as rewritten in task 1.2
- [ ] 9.4 Every frontend client of a method renamed in task 2.5 (fan, organizer and admin apps), including the KYC screens on `KycService`; stop sending `user_id`; clear all client state on sign-out and account switch (design D15), and remove the internal user id cache when nothing else reads it; verify `make check` passes and a component test shows the state cleared after sign-out
- [ ] 9.5 Upgrade the generated clients to the 2.6 release, run `make check`, open the frontend PR citing the change, and merge; verify the production rollout is healthy

## 10. Production verification

- [ ] 10.1 Update the lottery E2E (`stories/win-tickets-in-a-lottery`) and the first-come E2E (`stories/buy-tickets-first-come`), and run both in production with the Stripe Sandbox; verify each scenario passes: Demand within capacity, Oversubscribed phase, Withdraw and re-apply, Entry left unconfirmed, Organizer still in identity check, Presale winner at the limit, Presale winner below the limit, and every scenario of `stories/buy-tickets-first-come`
- [ ] 10.2 Read the migrated rows in production read-only (sales, ticket types, entries, checkouts, users' name and phone); verify the counts match task 0.2
