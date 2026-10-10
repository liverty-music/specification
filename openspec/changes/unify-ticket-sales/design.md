## Context

See proposal.md - Why. The decisions behind this change were made in the organizer console exploration of 2026-10-09/10.

Current state (verified 2026-10-10):

- **Lottery in production code** (backend `main`):
  - `lottery_sales_phases` has one row per lottery on one event and no uniqueness on `event_id` (`idx_lottery_sales_phases_event_id`).
  - `ticket_applications` has `phase_id`, `applicant_id`, `applicant_full_name` and `applicant_phone_number`. `uq_ticket_applications_active` enforces one active application per phase and applicant.
  - The state enum is `WITHDRAWN = 4` in proto and `5` in Go and the DB CHECK.
  - Code: `entity/lottery_sales_phase.go`, `entity/lottery_draw.go`, `usecase/lottery_uc.go`, `usecase/issuance_uc.go`, `rdb/lottery_phase_repo.go`, `rdb/ticket_application_repo.go`, `rdb/issuance_repo.go`, `rdb/order_repo.go`, `adapter/rpc/lottery_handler.go`, `adapter/rpc/organizer_lottery_handler.go` and the mappers.
- **First-come sale** (`first-come-ticket-sales`):
  - Its entity and RPC protos are on specification `main` (v0.73.0).
  - The backend exists only on the unmerged branch `worktree-first-come-ticket-sales`. On that branch, `ticket_sales` has `UNIQUE (event_id)` and `CHECK (method IN (1))`.
  - None of it is in production.
- **Personal data copies**:
  - `ticket_applications.applicant_*` and `tickets.holder_*` exist in production.
  - `users.holder_*` and `reservations.holder_*` exist only on the first-come branch.
- **Door check**: the reception screen never shows a holder's name or phone (`ticket-wallet-and-checkin`, `route/reception` "The verdict without personal data"). The name on a Ticket is therefore not an entry control. Entry control comes from account binding, the device-signed admission code, same-time group entry and, where a sale requires it, the bound verified identity.
- **In-flight changes on the same specs**:
  - `ticket-wallet-and-checkin` modifies `entity/lottery-sales-phase`, `usecase/lottery-sales-phase/configure-lottery-phase`, `adapter/{fan,organizer}/api/rpc/lottery` and `route/lottery-phase-editor`, and adds `entity/ticket/list-by-holder-and-event`.
  - `identity-ekyc-jpki` adds requirements to `usecase/lottery-sales-phase/set-phase-verification-requirement` and `usecase/ticket-application/apply`.

## Goals / Non-Goals

**Goals:**
- One sale model that the lottery uses now, `first-come-ticket-sales` builds on, and discovered sales move into later.
- Each personal fact stored once.
- Every ticketing record names the User `user`.
- The rename and the model change ship in one migration while the data is test data only.

**Non-Goals:**
- The `FirstCome` method, `Checkout` and the first-come screens. They stay in `first-come-ticket-sales`, whose artifacts this change updates (tasks 8.x).
- Moving `SalesPhase`, `SalesPhaseReminder` and `SalesPhaseSearchLog` into `TicketSale`. That is a later change. This change only shapes `TicketSale` so that a discovered sale fits it: a Series-level sale with a method, a window and no ticket types.
- Editing a sale after it is created. Only the verification requirement can change, as today. Editing comes with the organizer console redesign.
- Seat tiers (several ticket types for one event in one sale) and a shared event capacity.
- Renaming `ReceptionLink` to `Scanner`. That is a separate change.

## Decisions

### D1 — Two entities: `TicketSale` per Series, `TicketType` per event

A `TicketSale` (受付) holds what is common to one sale opportunity: Series, name, method, window, verification requirement, drawn time. A `TicketType` holds what the sale offers for one event: price, quantity, per-account limit. A sale has at most one ticket type per event, so `(ticket_sale_id, event_id)` is unique.

- **Why:** a fan-club presale for a tour is one window and one verification rule over several dates. The fan-facing reminder and the console both show it as one sale. The quantity and price differ per venue.
- **Rejected — one `TicketSale` per event** (the shape on the first-come branch): a tour presale becomes N sales with N reminders, and nothing ties them together.
- **Rejected — one shared capacity per event** (decided with the user): each sale keeps its own quantity. The operator moves unsold tickets to the next sale by raising its quantity. A shared pool needs an event capacity field that does not exist and stock accounting across sales.

### D2 — A sale has a name

`TicketSale.name` (1–100 characters, for example "ファンクラブ先行" or "一般発売") is required.

- **Why:** an event can now have several sales, and the method alone cannot tell two lotteries apart (fan-club and official presale).
- The migration names each existing phase "抽選".

### D3 — Method-specific rules live on the sale

`method` is `Lottery` in this change. The lottery's window rule (1 to 14 days) and the drawn time apply only when the method is `Lottery`. `first-come-ticket-sales` adds `FirstCome`, with its own window rule (end no later than the event start), the price lock and the sold count, on `TicketSale` and `TicketType`.

### D4 — Two sales of one event never overlap

`TicketSaleUseCase.Create` reads the existing sales of each event with `TicketSale.ListByEvent` and fails with FailedPrecondition when any window overlaps.

- **Why the usecase:** one operator creates sales by hand, so concurrent creates for the same event are not a realistic race.
- **Rejected — a DB exclusion constraint:** it needs the window copied onto `ticket_types`. Add it if a second writer ever appears.
- **Consequence:** at most one sale of an event is open at any instant. The fan event page can show "the current sale" without a choice.

### D5 — The per-account limit counts tickets already held for the event

`LotteryUseCase.Enter` fails with FailedPrecondition when the fan's Issued tickets for the event (`Ticket.ListByUserAndEvent`) plus the requested count exceed the ticket type's per-account limit. `TicketType.per_account_limit` therefore means "tickets one account may hold for the event after this sale". An operator who wants presale winners to buy more in the general sale gives the general sale a higher limit.

- **Why Issued tickets are enough:**
  - The windows do not overlap (D4).
  - A lottery is drawn within 1 minute after it closes (`draw-due-sales`), and its winners are issued within 1 more minute (`issue-due-wins`).
  - So when the next sale opens, the earlier results are already tickets.
- **Limit:** at most 10, because one admission code presents at most 10 tickets (`ticket-wallet-and-checkin`).

### D6 — A lottery sale is drawn once, for all its ticket types

`LotteryUseCase.DrawDueSales` lists the lottery sales whose end time has passed and that are not drawn (`TicketSale.ListDueForDraw`). For each sale, `RunDraw` runs `LotteryEntry.RunLotteryDraw` per ticket type against that type's quantity. It captures the winners and releases the losers. `LotteryEntry.PersistDrawOutcome` records all outcomes of the sale and sets the sale's drawn time in one transaction.

- **Rejected — a drawn time per ticket type:** all types of a sale close at the same instant, so a per-type drawn time adds a state that no rule reads.
- A draw position is unique within a ticket type.

### D7 — `TicketApplication` → `LotteryEntry`, `Applied` → `Entered`

- **Why the names:** in English a fan "enters" a lottery or ballot. "Application" also collides with the apply window of a discovered sale.
- **Rename map:**

  | Layer | From | To |
  |---|---|---|
  | DB | `ticket_applications` | `lottery_entries` |
  | DB columns | `phase_id`, `applicant_id` | `ticket_type_id`, `user_id` |
  | proto file | `lottery_application.proto` | `lottery_entry.proto` |
  | proto messages | `TicketApplication*` | `LotteryEntry*` |
  | Go | `TicketApplication*` | `LotteryEntry*` |
  | usecase methods | `Apply`, `WithdrawApplication`, `GetMyApplication`, `DrawDuePhases` | `Enter`, `WithdrawEntry`, `GetMyEntry`, `DrawDueSales` |

- **Enum values are aligned.** The state numbers become `ENTERED = 1`, `WON = 2`, `LOST = 3`, `WITHDRAWN = 4` in proto, Go and DB. The migration rewrites stored `5` to `4`. This fixes the current proto/DB mismatch.
- `uq_ticket_applications_active` becomes `uq_lottery_entries_active` on `(ticket_type_id, user_id) WHERE state <> WITHDRAWN`.

### D8 — Full name and phone number live only on `User`

- `users.full_name` and `users.phone_number` are added. `ticket_applications.applicant_*` and `tickets.holder_*` are dropped. On the first-come side, `reservations.holder_*` and `users.holder_*` never ship.
- `LotteryUseCase.Enter` takes the name and phone, validates them by the User rule and stores them with `User.UpdatePersonalDetails` before it creates the entry. The entry screen prefills them from the User.
- The ticket face reads the User's current values. The fan can change them at any time.
- **Why no copy on the Ticket:** the door never reads the name (Context). Account binding and the admission code control entry. A copy per ticket stored the same value N times for a companion group.
- **Rejected — locking changes while tickets are valid** (discussed with the user): it blocks real corrections (a marriage name, a new phone) and protects nothing that the door checks.
- **Legal follow-up:** whether 特定興行入場券 (covered ticket) evidence needs the value confirmed at sale goes to the counsel list in `docs/payments-design.md`. If counsel says yes, an append-only history of changes is added then. A copy on each Ticket is not the answer to that.
- `HolderIdentity` and the deprecated `ApplicantIdentity` leave the protos. Name and phone become `FullName` and `PhoneNumber` value messages on `User`.

### D9 — Every ticketing record names the User `user`

- The DB columns `orders.buyer_id` and `tickets.holder_id` become `user_id`.
- The proto fields `buyer_id`, `holder_id` and `applicant_id` become `user_id`.
- Operations are renamed:
  - `Order.ListByBuyer` → `ListByUser`
  - `Order.GetByApplicationID` → `GetByLotteryEntryID`
  - `Order.ListApplicationIDsAwaitingIssuance` → `ListLotteryEntryIDsAwaitingIssuance`
  - `Ticket.ListByHolder` → `ListByUser`
  - `Ticket.ListByHolderAndEvent` → `ListByUserAndEvent`
- **Why:** each record has exactly one User. "Holder" and "buyer" are not entities (specification `CLAUDE.md`, review criteria).
- Resale stays correct. It voids the ticket and issues a new one on the buyer's new Order (`official-resale` design), so a Ticket's user never changes.

### D10 — Interfaces and realizations

- `TicketSaleRepository`:
  - `Create`: inserts the sale and its ticket types in one transaction.
  - `Get`, `ListByEvent`, `ListDueForDraw`, `UpdateVerificationRequirement`.
  - `TicketType.Get` is on the same repository, because a type is always read with its sale.
- `LotteryEntryRepository`: the old application repository, renamed and keyed by ticket type. `PersistDrawOutcome` takes the sale id and sets `ticket_sales.drawn_at` in the same transaction.
- `LotteryEntry.RunLotteryDraw` stays a pure function (`entity/lottery_draw.go`).
- The card hold operations (create, verify, capture, cancel) stay on the Stripe manual-capture port. `first-come-ticket-sales` already plans to parameterize it (its D3). This change only renames its idempotency key prefix from the phase to the sale.
- `User.UpdatePersonalDetails` is a single-row update on `users`.

### D11 — RPC surface

- **Organizer** `rpc.organizer.ticket_sale.v1.TicketSaleService`:
  - `Create`: a sale with its ticket types.
  - `List`: filtered by `event_id`; returns sales with their ticket types and, for a lottery type, its tallies.
  - `SetVerificationRequirement`: a custom method.
  - This replaces `rpc.organizer.lottery.v1.LotteryService`, and the first-come `Configure`/`Get` on that package. `first-come-ticket-sales` adds its methods back onto this service.
- **Fan** `rpc.lottery.v1.LotteryService` becomes `rpc.lottery_entry.v1.LotteryEntryService`:
  - `CreateAuthorization`, `Create` (enter), `Get` (the caller's entry for a ticket type), `Withdraw`, `GetResult`.
  - Every request names a ticket type, not a phase.
- Breaking proto changes go in with the `buf skip breaking` label (specification `CLAUDE.md`).

### D12 — Specs are replaced, not moved

The lottery specs change their subject (phase → sale and type), their attributes (no personal data) and their state names. So this change writes them as ADDED capabilities at the new paths, with REMOVED deltas on the old paths. The schema's direct "move" rule is for a pure rename without a behavior change, and it does not fit this case. Entity Purposes of existing entities (Order, Ticket, User) are edited directly in the main specs (tasks 1.x), as the schema requires.

### D13 — Sequencing with in-flight changes

1. **`ticket-wallet-and-checkin`** archives before this change syncs its specs. Its rules are already folded into the new specs:
   - at most 10 tickets per account;
   - a sale needs the event's start time;
   - the editor's start-time notice;
   - `list-by-holder-and-event` → `list-by-user-and-event`.

   After it archives, this change adds the REMOVED delta for `entity/ticket/list-by-holder-and-event` (task 1.4).
2. **`identity-ekyc-jpki`** moves its two ADDED requirements to `usecase/ticket-sale/set-verification-requirement` and `usecase/lottery-entry/enter` (task 8.3).
3. **`first-come-ticket-sales`** is updated after this change's plan merges (tasks 8.1–8.2). Its backend branch rebases onto the new tables before it is released.
4. **`official-resale`** renames `ResaleListing.seller` to `holder` (task 8.4). This is a planned change with no code yet.

## Risks / Trade-offs

- [One large breaking change across proto, DB, backend and two frontends] → There are no users and only test data. Deploy in one window in the order spec → backend (migration first) → frontend. The organizer lottery editor and the fan entry screen are down between the backend and frontend deploys.
- [Dropping the name and phone columns cannot be undone] → Before the drop, the migration copies the newest value per user into `users` (task 3.2). Before the migration, read the row counts and a sample of rows read-only (task 3.1).
- [The per-account limit uses issued tickets only (D5)] → If issuance is stuck for more than the gap between two sales, a fan could exceed the limit. `IssueDueWins` failures already alert. The gap between two sales of one event is an operator choice, and it is normally days.
- [Overlap is checked in the usecase only (D4)] → Two concurrent creates for one event could both pass. There is a single operator per Organizer today. Revisit when `organizer-rbac-subowners` adds editors.
- [The `first-come-ticket-sales` branch rebase is large] → That branch's `TicketSale` table and code are replaced by this change's, plus `FirstCome` columns. Task 8.2 lists what moves.
- [Spec conflicts with in-flight changes] → D13 fixes the order. `openspec validate --strict` runs for this change and for each updated change before their PRs.

## Migration Plan

1. Specification PR: protos and this change's plan. Then release → BSR gen.
2. Backend PR with one Atlas migration:
   1. Create `ticket_sales` and `ticket_types`.
   2. Copy each `lottery_sales_phases` row into one sale and one type:
      - sale: Series of the event, name "抽選", method Lottery, start and end times, verification requirement, drawn time;
      - type: event, price, quantity = capacity, per-account limit = max tickets per application.
   3. Rename `ticket_applications` to `lottery_entries`. Map `phase_id` to the new type id, rename `applicant_id` to `user_id`, and rewrite state `5` to `4`.
   4. Add `users.full_name` and `users.phone_number`, filled from the newest entry or ticket of each user.
   5. Drop `applicant_*` and `tickets.holder_*`.
   6. Rename `orders.buyer_id`, `orders.application_id` (→ `lottery_entry_id`) and `tickets.holder_id`.
   7. Drop `lottery_sales_phases`.
3. Frontend PR: fan entry screen, organizer lottery editor and status screen, generated clients.
4. Verify in production with the Stripe Sandbox E2E for the lottery story and read-only checks of the migrated rows.
5. Rollback: the migration is forward-only. With test data only, a failed deploy is fixed forward. If the data must return, restore with Cloud SQL point-in-time recovery to before the migration.
