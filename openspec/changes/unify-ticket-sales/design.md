## Context

See proposal.md - Why. The decisions behind this change were made in the organizer console exploration of 2026-10-09/10. The plan merged in specification #1102 on 2026-10-10; it was then re-checked against the code and the other changes that merged the same day.

Current state (verified 2026-10-11; backend `main` 47fee37, frontend `main` 888f637, specification `main` 56186a6d):

- **Lottery in production code** (backend `main`):
  - `lottery_sales_phases` has one row per lottery on one event and no uniqueness on `event_id` (`idx_lottery_sales_phases_event_id`).
  - `ticket_applications` has `phase_id`, `applicant_id`, `applicant_full_name` and `applicant_phone_number`. `uq_ticket_applications_active` enforces one active application per phase and applicant. `chk_ticket_applications_applicant_phone_e164` checks the phone.
  - The state enum is `WITHDRAWN = 4` in proto and `5` in Go and the DB CHECK.
  - Code: `entity/lottery_sales_phase.go`, `entity/lottery_draw.go`, `usecase/lottery_uc.go`, `usecase/issuance_uc.go`, `rdb/lottery_phase_repo.go`, `rdb/ticket_application_repo.go`, `rdb/issuance_repo.go`, `rdb/order_repo.go`, `adapter/rpc/lottery_handler.go`, `adapter/rpc/organizer_lottery_handler.go` and the mappers.
- **First-come sale** (`first-come-ticket-sales`, 33 of 54 tasks done):
  - Merged in backend #593 and frontend #720 on 2026-10-10. Its protos are on specification `main` at v0.75.0. Backend and frontend pin v0.75.0. No fan has bought through it.
  - `ticket_sales` is one row per event (`uq_ticket_sales_event_id`, `chk_ticket_sales_method` = 1) and holds the window, price, quantity, per-account limit and sold count. `organizer-console-api` has column grants on it.
  - `reservations` holds a fan's checkout. `orders` has `reservation_id` beside `application_id`, with `chk_orders_one_source`.
  - Proto: `TicketSaleMethod.FIRST_COME = 1`; `sale_start_time` / `sale_end_time`; OUTPUT_ONLY `held_count`, `state` and `low_stock`; `Order.source` is a oneof of `application_id` and `reservation_id`.
  - Organizer `TicketSaleService.Configure` creates or changes an event's sale; `Get` reads it. Fan `TicketSaleService.Get` reads an event's sale; `ReservationService` runs the checkout.
  - `organizers.seller_*` and `Organizer.seller_details`, also inside the Organizer that `Series` embeds; admin `OrganizerService.UpdateSellerDetails`.
- **Personal data copies** (all on backend `main`):
  - `ticket_applications.applicant_*` and `tickets.holder_*`.
  - `users.holder_full_name` / `holder_phone_number` (`User.HolderIdentity`, `UserRepository.UpdateHolderIdentity`; proto `User.holder_identity = 9`).
  - `reservations.holder_*`, set from the fan-side `ReservationService.Authorize` request.
- **Door check**: the reception screen never shows a holder's name or phone (`route/reception` "The verdict without personal data"). The name on a Ticket is therefore not an entry control. Entry control comes from account binding, the device-signed admission code, same-time group entry and, where a sale requires it, the bound verified identity.
- **Events and Concerts**: `split-concert-from-event` (proto v0.76.0; backend #595 open) keeps the generic Event and `event_id`. Sales and tickets still attach to the Event. Its backend migration is `20261010020000`.

## Goals / Non-Goals

**Goals:**
- One sale model for the lottery and the shipped first-come sale, which discovered sales move into later.
- Each personal fact stored once.
- Every ticketing record names the User `user`.
- The rename and the model change ship in one migration while the data is test data only.

**Non-Goals:**
- New first-come behavior. This change moves what `first-come-ticket-sales` shipped onto the new model and keeps its rules.
- Moving `SalesPhase`, `SalesPhaseReminder` and `SalesPhaseSearchLog` into `TicketSale`. That is a later change (`migrate-discovered-sales`). This change only shapes `TicketSale` so that a discovered sale fits it: a Series-level sale with a method, a window and no ticket types.
- Editing a lottery sale after its window opens. Before that, its window and ticket types can change (D11). A first-come sale keeps the edits it has today.
- Seat tiers (several ticket types for one event in one sale) and a shared event capacity.
- Renaming `ReceptionLink` to `Scanner`. That is `rename-reception-to-scanner`.

## Decisions

### D1 — Two entities: `TicketSale` per Series, `TicketType` per event

A `TicketSale` (受付) holds what is common to one sale opportunity: Series, name, method, window, verification requirement, drawn time. A `TicketType` holds what the sale offers for one event: price, quantity, per-account limit, and for a first-come sale its sold and held counts. A sale has at most one ticket type per event, so `(ticket_sale_id, event_id)` is unique.

- **Why:** a fan-club presale for a tour is one window and one verification rule over several dates. The fan-facing reminder and the console both show it as one sale. The quantity and price differ per venue.
- **Rejected — one `TicketSale` per event** (the shape `first-come-ticket-sales` shipped): a tour presale becomes N sales with N reminders, and nothing ties them together.
- **Rejected — one shared capacity per event** (decided with the user): each sale keeps its own quantity. The operator moves unsold tickets to the next sale by raising its quantity. A shared pool needs an event capacity field that does not exist and stock accounting across sales.

### D2 — A sale has a name

`TicketSale.name` (1–100 characters, for example "ファンクラブ先行" or "一般発売") is required.

- **Why:** an event can now have several sales, and the method alone cannot tell two lotteries apart (fan-club and official presale).
- The migration names each existing lottery phase "抽選" and each existing first-come sale "一般発売" (decided with the user).

### D3 — Method-specific rules

- **Both methods:** the sale ends before the start of every event it covers (`usecase/ticket-sale/create`), so a lottery is drawn and issued, and a first-come sale is closed, before the doors open. The overlap rule (D4), the per-account limit (D5), the Organizer's complete business details for the 特商法 disclosure, and the verification requirement apply to both (decided with the user): a first-come checkout checks the fan's Kyc at `Start` and binds the Tickets to it at issuance, as a lottery does.
- **The event page** shows the event's current sale whatever its method, with the way to enter a lottery or buy first-come tickets (decided with the user).
- **Lottery:** the window lasts 1 to 14 days, and the sale has a drawn time.
- **FirstCome:** the rules that `first-come-ticket-sales` shipped on its per-event sale move to the `TicketType`, because each one counts one event's stock: the sold count, the held count, the remaining count, the sale state (NotYetOnSale, OnSale, AllHeld, SoldOut, Ended), LowStock and the price lock. The state is read per ticket type; NotYetOnSale and Ended come from the sale's window.
- The `entity/ticket-sale` and `entity/ticket-type` deltas carry these rules once `first-come-ticket-sales` has archived its specs (task 1.2).

### D4 — Two sales of one event never overlap

`TicketSaleUseCase.Create` reads the existing sales of each event with `TicketSale.ListByEvent` and fails with FailedPrecondition when any window overlaps. `SetWindow` checks the same rule.

- **Why the usecase:** one operator creates sales by hand, so concurrent creates for the same event are not a realistic race.
- **Rejected — a DB exclusion constraint:** it needs the window copied onto `ticket_types`. Add it if a second writer ever appears.
- **Consequence:** at most one sale of an event is open at any instant. The fan event page can show "the current sale" without a choice.

### D5 — The per-account limit counts tickets already held for the event

`LotteryUseCase.Start` fails with FailedPrecondition when the fan's Issued tickets for the event (`Ticket.ListByUserAndEvent`) plus the requested count exceed the ticket type's per-account limit. The first-come checkout start applies the same rule. `TicketType.per_account_limit` therefore means "tickets one account may hold for the event after this sale". An operator who wants presale winners to buy more in the general sale gives the general sale a higher limit.

- **Why Issued tickets are enough:**
  - The windows do not overlap (D4).
  - A lottery is drawn within 1 minute after it closes (`draw-due-sales`), and its winners are issued within 1 more minute (`issue-due-wins`).
  - So when the next sale opens, the earlier results are already tickets.
- **Limit:** at most 10, because one admission code presents at most 10 tickets (`usecase/ticket/admit`).

### D6 — A lottery sale is drawn once, for all its ticket types

`LotteryUseCase.DrawDueSales` lists the lottery sales whose end time has passed and that are not drawn (`TicketSale.ListDueForDraw`). For each sale, `RunDraw` runs `LotteryEntry.RunLotteryDraw` per ticket type against that type's quantity. It captures the winners and releases the losers. `LotteryEntry.PersistDrawOutcome` records all outcomes of the sale and sets the sale's drawn time in one transaction.

- **Rejected — a drawn time per ticket type:** all types of a sale close at the same instant, so a per-type drawn time adds a state that no rule reads.
- A draw position is unique within a ticket type.

### D7 — `TicketApplication` → `LotteryEntry`, `Applied` → `Entered`; `Reservation` → `Checkout`

- **Why the names:** in English a fan "enters" a lottery or ballot. "Application" also collides with the apply window of a discovered sale. A first-come purchase in progress is a checkout; "reservation" reads as a seat booking.
- **Rename map:**

  | Layer | From | To |
  |---|---|---|
  | DB | `ticket_applications`, `reservations` | `lottery_entries`, `checkouts` |
  | DB columns | `phase_id`, `applicant_id`; `reservations.ticket_sale_id` | `ticket_type_id`, `user_id`; `checkouts.ticket_type_id` |
  | proto file | `lottery_application.proto`, `reservation.proto` | `lottery_entry.proto`, `checkout.proto` |
  | proto messages | `TicketApplication*`, `Reservation*` | `LotteryEntry*`, `Checkout*` |
  | Go | `TicketApplication*`, `Reservation*` | `LotteryEntry*`, `Checkout*` |
  | usecase methods | `CreateAuthorization`, `Apply`, `WithdrawApplication`, `GetMyApplication`, `GetResult`, `DrawDuePhases` | `Start`, `Authorize`, `Confirm`, `WithdrawEntry`, `ListOwnByTicketType`, `DrawDueSales` (D14) |

- **Enum values are aligned.** The lottery state numbers become `ENTERED = 1`, `WON = 2`, `LOST = 3`, `WITHDRAWN = 4`, `DRAFT = 5` in proto, Go and DB. The migration rewrites stored `5` (today's Withdrawn) to `4` before `DRAFT` takes 5. This fixes the current proto/DB mismatch.
- `uq_ticket_applications_active` becomes `uq_lottery_entries_active` on `(ticket_type_id, user_id) WHERE state <> WITHDRAWN`. `uq_reservations_held` becomes `uq_checkouts_held` on the ticket type.

### D8 — Full name and phone number live only on `User`

- `users.holder_full_name` / `holder_phone_number` are renamed `full_name` / `phone_number`, with their CHECKs. A user without values gets them from their newest lottery application or ticket. `ticket_applications.applicant_*`, `tickets.holder_*` and `reservations.holder_*` are dropped.
- `LotteryUseCase.Authorize` and the first-come checkout's `Authorize` take the name and phone, validate them by the User rule and store them with `User.UpdatePersonalDetails` before they open the hold. The entry and checkout screens prefill them from the User.
- The ticket face reads the User's current values. The fan can change them at any time on the settings screen with `UserService.Update` (a new full name, phone number or both; decided with the user), as well as at lottery entry and checkout.
- **Why no copy on the Ticket:** the door never reads the name (Context). Account binding and the admission code control entry. A copy per ticket stored the same value N times for a companion group.
- **Rejected — locking changes while tickets are valid** (discussed with the user): it blocks real corrections (a marriage name, a new phone) and protects nothing that the door checks.
- **Legal follow-up:** whether 特定興行入場券 (covered ticket) evidence needs the value confirmed at sale goes to the counsel list in `docs/payments-design.md`. If counsel says yes, an append-only history of changes is added then. A copy on each Ticket is not the answer to that.
- Proto: `HolderIdentity` and the deprecated `ApplicantIdentity` leave. `User.holder_identity = 9` is removed and field 9 reserved. Name and phone become `FullName` and `PhoneNumber` value messages on `User`. The checkout authorize request carries `full_name` and `phone_number` instead of `holder_identity`.

### D9 — Every ticketing record names the User `user`

- The DB columns `orders.buyer_id` and `tickets.holder_id` become `user_id`. `orders.application_id` and `reservation_id` become `lottery_entry_id` and `checkout_id`, and `chk_orders_one_source` follows.
- The proto fields `buyer_id`, `holder_id` and `applicant_id` become `user_id`. Inside the `Order.source` oneof, `application_id` and `reservation_id` become `lottery_entry_id` and `checkout_id`.
- Operations are renamed:
  - `Order.ListByBuyer` → `ListByUser`
  - `Order.GetByApplicationID` → `GetByLotteryEntryID`
  - `Order.GetByReservationID` → `GetByCheckoutID`
  - `Order.ListApplicationIDsAwaitingIssuance` → `ListLotteryEntryIDsAwaitingIssuance` (realized on `IssuanceRepository`, as today)
  - `Ticket.ListByHolder` → `ListByUser`
  - `Ticket.ListByHolderAndEvent` → `ListByUserAndEvent`
- **Why:** each record has exactly one User. "Holder" and "buyer" are not entities (specification `CLAUDE.md`, review criteria).
- Resale stays correct. It voids the ticket and issues a new one on the buyer's new Order (`official-resale` design), so a Ticket's user never changes.

### D10 — Interfaces and realizations

- `TicketSaleRepository` (exists for first-come with `Create`, `Get`, `GetByEvent`, `Update`; reshaped):
  - `Create`: inserts the sale and its ticket types in one transaction.
  - `Get`, `ListByEvent` (replaces `GetByEvent`), `ListDueForDraw`, `UpdateVerificationRequirement`.
  - `SetWindow` and `UpdateTicketType`: change the window, and one ticket type's price, quantity and limit. For a first-come type the update is one conditional statement, so a checkout created meanwhile is counted (the shipped rule).
  - `TicketType.Get` is on the same repository, because a type is always read with its sale.
- `LotteryEntryRepository`: the old application repository, renamed and keyed by ticket type. `GetOrCreateDraft` relies on `uq_lottery_entries_active` and one conditional statement, as the checkout's `GetOrCreateHeld` does. `PersistDrawOutcome` takes the sale id, withdraws the sale's Drafts and sets `ticket_sales.drawn_at` in the same transaction.
- `CheckoutRepository`: the reservation repository, renamed and keyed by ticket type; the sold count it commits lives on `ticket_types`.
- `LotteryEntry.RunLotteryDraw` stays a pure function (`entity/lottery_draw.go`).
- The card hold operations (create, verify, capture, cancel) stay on the Stripe manual-capture port, parameterized by `CardHoldPolicy` (`payment/stripe_authorization.go`). This change only renames the lottery's idempotency key prefix from the phase to the sale.
- `User.UpdatePersonalDetails` is a single-row update on `users`, replacing `UpdateHolderIdentity`.

### D11 — RPC naming rule and surface

**Rule** (decided with the user, and checked by a devil's advocate review; it moves to a repository skill and `AGENTS.md:148` in task 1.5):

| Form | Use |
|---|---|
| `Get(<own id or natural key>)` | read one resource. A natural key identifies the resource outside this system (a push subscription's endpoint); another entity's id is not one |
| `Get()` | read the one resource the caller has (`OrganizerService.Get`, `WalletPublicKeyService.Get`) |
| `List()` | every resource the caller can see; optional narrowing (state, period) is a field |
| `ListBy<Key>` | narrowed by one required request field. Key is an entity (singular, or plural for several ids) or a value object (`ListByLocation`). A Key in the name is always a field in the request. The singular and the plural of one Key are separate methods and may return different shapes (`ListByArtist` a flat list, `ListByArtists` grouped by date and proximity to a given home) |
| `List<Qualifier>` | a computed set that no request field selects (`ListTop`, `ListSimilar`, `ListFollowed`) |
| `Create`, `Delete` | a resource's own create and delete |
| `Update` | the whole resource, or the fields named by a field mask |
| `Set<Attribute>` | one attribute replaced (`SetHome`, `SetVerificationRequirement`) |
| domain verb | a state change (`Publish`, `Withdraw`, `Dismiss`, `Confirm`), a relation made or ended (`Follow`/`Unfollow`, `AssociateArtist`/`DisassociateArtist`), an idempotent registration (`Register`), or an operation that is not a standard method (`Search`, `Start`) |

- A service is named after an entity (`entity/*`). A service with no entity behind it is not kept.
- A service's standard methods take and return only its own resource. A read of another resource goes to that resource's service as `ListBy<Entity>`. A read may carry related resources as side lists (`ConcertService` returns `series` and `artists`), and a create may carry child resources created with the parent (`TicketSaleService.Create` with its ticket types).
- `Get<Noun>` and `Update<Field>` are not used.
- When the caller owns the resource, neither the method name nor the request names the caller (D15). A request names a user or an Organizer only when an admin acts on another one.
- **Packages:** the top-level `rpc.<entity>.v1` is the fan API; `rpc.admin.`, `rpc.organizer.` and `rpc.scanner.` name the caller. The same method name in two packages narrows by the same Key; the payload may differ.
- **Deviation from AIP:** AIP-132 narrows a `List` with `parent` and `filter`, and AIP-136 forbids standard verbs in custom methods. `ListBy<Key>` and `List<Qualifier>` break both. They are kept because the name then states the filter, and the repository already uses them (`ConcertService.ListBySeries`). Rejected — `List(parent)` plus typed filter fields: `List(series_id, event_id?)` does not say what it narrows by.
- **Rejected — the caller's relation as a `ListBy` Key** (`ListByFollower`, organizer `ListByOrganizer()`): the same name would take an id on the admin API and nothing on the organizer API, so the name would not predict the request.

**Ticketing services:**

- **Organizer** `rpc.organizer.ticket_sale.v1.TicketSaleService`:
  - `Create`: a sale with its ticket types, method Lottery or FirstCome.
  - `ListByEvent`: the event's sales with their ticket types and, for a lottery type, its tallies, for a first-come type its sold and held counts. `ListBySeries` can be added later without a breaking change.
  - `SetWindow`: the sale's start and end times.
  - `SetVerificationRequirement`.
  - This replaces `rpc.organizer.lottery.v1.LotteryService` and the shipped `Configure`/`Get`.
- **Organizer** `rpc.organizer.ticket_type.v1.TicketTypeService.Update`: a ticket type's price, quantity and per-account limit.
- Edit rules (decided with the user): a Lottery sale and its ticket types can be changed until its window opens; a FirstCome sale keeps the shipped rules (price lock while tickets are held or sold, quantity not below sold plus held). The usecase specs carry them (task 1.2).
- **Fan** `rpc.ticket_sale.v1.TicketSaleService.ListByEvent`: the event's sales, each with its ticket type for the event, ordered by start time. Which sale the event page shows is the page's rule (`route/event`): the open one, otherwise the next to open, otherwise the last that ended. D4 keeps it to one open sale.
- **Fan** `rpc.lottery_entry.v1.LotteryEntryService` replaces `rpc.lottery.v1.LotteryService`: `Start(ticket_type_id, ticket_count)`, `Authorize`, `Confirm`, `Withdraw` (these three take the `lottery_entry_id`) and `ListByTicketType`, which returns the caller's entries for the ticket type, withdrawn ones included, newest first (D14).
- **Fan** `rpc.checkout.v1.CheckoutService` replaces `rpc.reservation.v1.ReservationService`: `Start(ticket_type_id, ticket_count)`, `Get`, `Authorize`, `Confirm`.
- **Fan** `rpc.order.v1.OrderService.Get(order_id)` replaces `TicketService.GetOrder`.
- **Admin** `OrganizerService.UpdateSellerDetails` becomes `SetBusinessDetails` (legal name, representative name, business address, business phone number, contact email).
- **Admin** `OrderService.Get(order_id)` returns the Order with its Settlement; `SettlementService.Get(order_id)` goes, and `SettlementService` keeps `List` by status (decided with the user).
- `rpc.issuance.v1.IssuanceService` is removed: no entity is behind it and no server serves it (backend `main` has no reference to `rpc/issuance`). Issuance runs in the `IssueDueWins` job.

**Other services** (behavior unchanged unless stated; task 1.4 writes their deltas):

| Today | After |
|---|---|
| `ConcertService.List(artist_id)` | `ListByArtist(artist_id)`, the flat list it returns today (backend `ConcertUseCase.ListByArtist`); the discovery screen calls it after a follow to tell whether the artist has concerts |
| `ConcertService.ListByFollower` | `ListFollowed` |
| admin `OrganizerService.ListArtists(organizer_id)` | admin `ArtistService.ListByOrganizer(organizer_id)` |
| organizer `OrganizerService.ListArtists` | organizer `ArtistService.List()` (the caller's Organizer's artists) |
| `FollowService.ListFollowed` | `FollowService.List` (the caller's Follows with their Artists) |
| `TicketJourneyService.ListByUser` | `List` |
| `IdentityVerificationService.Start`/`Complete`/`ReCheck`/`GetStatus` | `KycService.Start`/`Create`/`Recheck`/`Get()` (D16). `Get()` fails with NotFound for a fan who never passed KYC; the account's verification level is read from `UserService.Get` |
| push subscription `Create`/`Get`/`Delete` on `PushNotificationService` | `PushSubscriptionService`; `Get(endpoint)` keeps the endpoint as the natural key |
| `PushNotificationService.NotifyNewConcerts` | admin `NotificationService.NotifyNewConcerts` (a test hook) |
| admin `ConcertService.ListPending`/`Approve`/`Reject` | `StagedConcertService.List`/`Approve`/`Reject` |
| `ArtistService.CreateOfficialSite`/`DeleteOfficialSite` | `OfficialSiteService.Create`/`Delete` |
| `UserService.UpdateHome`/`UpdatePreferredLanguage` | `SetHome`/`SetPreferredLanguage`; new `UserService.Update` (full name, phone number or both, D8) |
| `NotificationService.MarkDismissed` | `Dismiss` (`MarkRead` stays: "read" is not a good imperative) |
| `SeriesService.RegenerateToken`, `CreateMediaUploadURL` | `RegenerateShareUrl`, `CreateMediaUploadUrl` |
| `user_id` on `UserService`, `NotificationService`, push subscription and KYC requests | removed (D15) |

Kept as they are, because the rule allows them: `FollowService.Follow`/`Unfollow`/`SetHype`, `TicketJourneyService.SetStatus`, admin `OrganizerService.AssociateArtist`/`DisassociateArtist`/`SetPlatformFeeRate`/`Deactivate`, `WalletPublicKeyService.Register`, `ArtistService.Search`/`ListTop`/`ListSimilar`, `ConcertService.Get(event_id)` (a Concert's id is its Event's id), `ListBySeries`, `ListByArtists`, `ListByLocation`, `SeriesService.Publish`/`Cancel`/`AttachMedia`, `OrderService.Refund`, `UserService.ResendEmailVerification`.

`ReceptionLinkService.List(event_id)` becomes `ScannerService.ListByEvent` in `rename-reception-to-scanner`.

Breaking proto changes go in with the `buf skip breaking` label (specification `CLAUDE.md`).

### D12 — Specs are replaced, not moved

The lottery and checkout specs change their subject (phase → sale and type), their attributes (no personal data) and their state names. So this change writes them as ADDED capabilities at the new paths, with REMOVED deltas on the old paths. The schema's direct "move" rule is for a pure rename without a behavior change, and it does not fit this case. Entity Purposes of existing entities (Order, Ticket, User, Organizer) are edited directly in the main specs (tasks 1.1 and 1.2), as the schema requires.

### D13 — Sequencing with in-flight changes

Upstream (before this change syncs its specs):

1. **`ticket-wallet-and-checkin`**: archived on 2026-10-10 (#1113). Its rules are folded into the new specs (at most 10 tickets per account; a sale needs the event's start time; the editor's start-time notice; `list-by-holder-and-event` → `list-by-user-and-event`). Task 1.2 adds the deltas on the specs it brought to main.
2. **`first-come-ticket-sales`**: finishes and archives first, as shipped (decided with the user). Then task 1.2 rewrites this change's ticket-sale, user and organizer deltas onto its main specs, and resolves the one collision: `first-come-ticket-sales` removes "Ticket journey becomes Paid" from `usecase/order/issue-from-captured-win`, which this change modifies.
3. **`identity-ekyc-jpki`** moves its two ADDED requirements to `usecase/ticket-sale/set-verification-requirement` and `usecase/lottery-entry/start` (task 8.1).
4. **`split-concert-from-event`** rewrites this change's artifacts to its names (its task 11.1). Its backend #595 also edits `organizer_lottery_handler.go`, which task 7.1 removes; whichever merges second rebases.
5. **`official-resale`** renames `ResaleListing.seller` to `user` (task 8.2). This is a planned change with no code yet.
6. **`rename-reception-to-scanner`** renames `ScannerService.List` to `ListByEvent` (task 8.3) and stays a separate change, released after this one.

Downstream (they wait for this change and copy its text when it archives): `rename-reception-to-scanner` (`entity/organizer/delete`, `usecase/ticket/admit`), `redesign-organizer-console` (`TicketSaleService`, `route/lottery-phase-editor`), `restructure-event-publishing` (`TicketSale.ListByEvent`; it changes `Event.IsEventPublished` to answer per Event) and `migrate-discovered-sales` (`entity/ticket-sale`, the delete specs).

### D14 — A lottery entry is started, authorized and confirmed, like a checkout

The fan builds the entry as a resource before the card hold opens, as a first-come checkout does (decided with the user):

| Step | Checkout | Lottery entry |
|---|---|---|
| start | `Start(ticket_type_id, ticket_count)` → Held checkout | `Start(ticket_type_id, ticket_count)` → Draft entry (`GetOrCreateDraft`) |
| hold | `Authorize(checkout_id, name, phone)` → client secret | `Authorize(lottery_entry_id, name, phone)` → client secret |
| confirm | `Confirm(checkout_id)` → Order | `Confirm(lottery_entry_id)` → Entered entry |

- **Why:** `CreateAuthorization` opened a hold that no record named, so it had no resource and its name read badly. The hold is now an attribute of the entry. Both purchase flows use the same verbs.
- **Draft:** a new state before Entered. A Draft is active (one per account and ticket type, D7), takes no part in the draw and is not tallied. A Draft with another count is withdrawn and replaced, as a checkout with another count is.
- **Abandoned Drafts:** `RunDraw` releases the hold of every Draft of the sale and records it Withdrawn with the outcome. Today a hold opened without `Apply` stays on the card until the card network expires it; this closes that gap.
- **Where the checks run:** the window on every step; the count, the verification gate and the per-account limit (D5) on `Start`; the hold amount on `Confirm`.
- **Cost:** three calls instead of two, and one more state.
- **Rejected — `Create` returns the Draft and the client secret together:** two calls, but its verbs differ from the checkout's.
- **Rejected — `LotteryService.Enter`:** "Lottery" is not an entity here (it is a TicketSale method), so the service would have no resource and the request no id to enter.

### D15 — A request never names the calling user

- Every per-user RPC takes the user from the signed-in caller (`User.GetByExternalID`), as the newer adapter specs already state ("the request never names a User", `adapter/fan/api/rpc/{ticket,lottery,wallet-public-key}`).
- This reverses `rpc-auth-scoping` (archived `2026-04-20-standardize-user-scoped-rpc-auth`), which required a `user_id` checked against the JWT as defense in depth. Its spec was dropped when the spec tree moved (`a2267bee`) without a recorded decision; this records it.
- **Why:** with the user taken from the token, a client bug can only act on the signed-in user's own data. The check stopped one case: a client that kept a previous account's id after an account switch. Clearing client state on sign-out and account switch covers that case (task 9.4). The field is not an authorization control, because the caller chooses both values. It cost a client-side id cache and a mismatch error on every call.
- Backend: `RequireUserIDMatch` and its four call sites (`identity_verification_handler.go`, `mapper/user.go`, `notification_handler.go`, `push_notification_handler.go`) go.
- Admin RPCs that act on another user (`admin.UserService.Delete(user_id)`) keep the id.

### D16 — 本人確認 is `Kyc`; "identity" means the identity provider account

- The result of a 本人確認 (identity check) is the entity `Kyc`, renamed from `VerifiedIdentity` (decided with the user). "Identity" then means only the account at the identity provider (Zitadel), as backend `IdentityRemover` and `usecase/user/delete` ("the User's sign-in identity") already use it, and as identity providers use it (Auth0 `user.identities`).
- **Why:** before, "identity" named both the sign-in account and the 本人確認 result, plus `HolderIdentity` and `ApplicantIdentity`. eKYC is already the project's word for a fan's online 本人確認 (`identity-ekyc-jpki`), and the RPCs read as English: `KycService.Start`, `Recheck`, `Get()`.
- **Scope of the word (decided with the user):** `Kyc` is only a fan's 本人確認 result. `docs/payments-design.md` also used "KYC" for the payment provider's check of an Organizer's payout account and for 犯収法 AML duties. The first is renamed "payout account verification" there (task 1.3); the second stays as the legal term "AML-KYC".
- **Rejected — `Identity`:** collides with the identity provider account. **Rejected — `VerifiedIdentity`:** keeps the collision, and `VerifiedIdentityService.Start` reads as "start a verified identity".
- Renames: spec `entity/verified-identity` → `entity/kyc` (a pure rename, the schema's direct move); proto `VerifiedIdentity`/`VerifiedIdentityId` → `Kyc`/`KycId`, `rpc.identity.v1.IdentityVerificationService` → `rpc.kyc.v1.KycService`, `VerificationLevel.IDENTITY_VERIFIED` → `KYC_VERIFIED`, the Ticket's verified identity reference → `kyc_id`; DB `verified_identities` → `kyc` (a mass noun, like `media` and `series`).
- Fan-facing text stays 本人確認. The `VerificationRequirement` values (Verified-any, JPKI-only) are not renamed here.

## Risks / Trade-offs

- [One large breaking change across proto, DB, backend and three frontends] → There are no users and only test data. Deploy in one window in the order spec → backend (migration first) → frontend. The lottery editor, the first-come editor, the fan entry screen and the checkout are down between the backend and frontend deploys.
- [Dropping the name and phone columns cannot be undone] → Before the drop, the migration fills `users` from the newest value per user (task 3.2). Before the migration, read the row counts and a sample of rows read-only (task 0.2).
- [The per-account limit uses issued tickets only (D5)] → If issuance is stuck for more than the gap between two sales, a fan could exceed the limit. `IssueDueWins` failures already alert. The gap between two sales of one event is an operator choice, and it is normally days.
- [Overlap is checked in the usecase only (D4)] → Two concurrent creates for one event could both pass. There is a single operator per Organizer today. Revisit when `organizer-rbac-subowners` adds editors.
- [Moving the shipped first-come code is large] → Its rules and tests move unchanged; each moved test keeps its scenario name (tasks 4.6, 5.6, 6.7). The `buy-tickets-first-come` E2E is rerun in production (task 10.1).
- [Spec conflicts with in-flight changes] → D13 fixes the order. `openspec validate --strict` runs for this change and for each updated change before their PRs.

## Migration Plan

1. Specification: the plan follow-up PR (tasks 1.x), then the proto PR and release → BSR gen.
2. Backend PR with one Atlas migration, timestamped after `20261010020000`:
   1. Create `ticket_types`. Reshape `ticket_sales`: drop `uq_ticket_sales_event_id`, add `series_id`, `name`, `verification_requirement` and `drawn_at`, allow methods FirstCome (1) and Lottery (2).
   2. Move each existing first-come sale's event, price, quantity, per-account limit and sold count into one ticket type; set its Series and the name "一般発売".
   3. Copy each `lottery_sales_phases` row into one sale and one type:
      - sale: Series of the event, name "抽選", method Lottery, start and end times, verification requirement, drawn time;
      - type: event, price, quantity = capacity, per-account limit = max tickets per application.
   4. Rename `ticket_applications` to `lottery_entries`. Map `phase_id` to the new type id, rename `applicant_id` to `user_id`, and rewrite state `5` to `4`.
   5. Rename `reservations` to `checkouts`, mapping `ticket_sale_id` to the new type id.
   6. Rename `users.holder_*` to `full_name` / `phone_number`; fill empty ones from the newest application or ticket of each user.
   7. Drop `applicant_*`, `tickets.holder_full_name` / `holder_phone_number`, `reservations.holder_*` and their CHECKs.
   8. Rename `orders.buyer_id`, `application_id`, `reservation_id`, `tickets.holder_id` and `organizers.seller_*`.
   9. Drop `lottery_sales_phases`. Redo the `organizer-console-api` grants on `ticket_sales` and `ticket_types`.
3. Frontend PR: fan entry screen, checkout and event page; organizer lottery editor, status screen and first-come editor; admin Organizer screen; generated clients.
4. Verify in production with the Stripe Sandbox E2E for the lottery and first-come stories and read-only checks of the migrated rows.
5. Rollback: the migration is forward-only. With test data only, a failed deploy is fixed forward. If the data must return, restore with Cloud SQL point-in-time recovery to before the migration.
