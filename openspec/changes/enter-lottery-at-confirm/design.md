## Context

See proposal.md - Why. Today a Draft row is written at `Start`, `AuthorizeCard` records the PaymentIntent on it (`lottery_entry_uc.go:344`) and `Confirm` flips it to Entered. The Stripe idempotency key of the authorization is `lottery-authorize:<entry id>` (`stripe_card_authorization.go:129`). The Referral is its own table (`referrals`, one row per Checkout or LotteryEntry, `chk_referrals_one_source`). The payment provider webhook already fulfils Orders from `payment_intent.succeeded` (`stripe_webhook_uc.go:185`) with a processed-event table for at-most-once handling (`stripe_webhook_uc.go:144`). Prod held 0 lottery entries on 2026-10-27 (read-only check, `db-proxy` runbook).

## Goals / Non-Goals

**Goals:**
- One rule settles every card authorization: once Authorized, it becomes an entry or is released, without a timer or a new engine.
- Fewer concepts: no Draft, no Start, no Referral entity.

**Non-Goals:**
- Durable retries of a failed release or capture: `make-lottery-draw-durable`.
- Reworking the first-come Checkout flow beyond its referral code.

## Decisions

### Money is held only after the secret, and every Authorized card authorization is settled by the webhook

3D Secure needs the card authorization secret, which `AuthorizeCard` returns only after the PaymentIntent exists. A PaymentIntent the fan never authenticated (`requires_payment_method`) holds nothing, so `AuthorizeCard` stores nothing and needs no cleanup. Once the fan authenticates, Stripe sends `payment_intent.amount_capturable_updated`. The webhook runs `LotteryEntryUseCase.Confirm` for it, and the fan's own `Confirm` RPC is the fast path to the same idempotent step.

- Rejected: a 30-minute durable release timer per card authorization. It needs the workflow engine, a cancel race with a late `Confirm`, and a draw delay, all to cover what the webhook covers with infrastructure in place.
- Rejected: keeping the Draft as the local record. It is the source of the count-change and withdrawal rules this change removes.
- Stripe retries a webhook for up to 3 days in live mode; the processed-event table keeps a redelivery at most once.

### The PaymentIntent carries the purchase

`CardAuthorization.Create` for a lottery entry writes the metadata `user_id`, `ticket_type_id`, `ticket_count`, `event_id` and `referral_code` (when given). It sends no idempotency key: each call is a new attempt, and the attempt the fan does not authenticate holds nothing. A Checkout's PaymentIntent keeps `checkout_id` and its key `ticket-sale-authorize:<checkout id>` (`CheckoutCardAuthorizationPolicy`, unchanged), and gains `user_id`, `ticket_type_id` and `ticket_count`. `CardAuthorization.Get` maps the metadata back; the purchase is a Checkout when `checkout_id` is present, a lottery entry otherwise. Prod holds no lottery PaymentIntent (the lottery is not used in the pilot), so no PaymentIntent without the new metadata reaches `Confirm`. The `lottery_entry_id` metadata goes away, because the entry does not exist when the PaymentIntent is created. `Confirm` reads the PaymentIntent, never the request, for the TicketType, count and code.

### Confirm in one place, for two callers

`LotteryEntryUseCase.Confirm(ctx, cardAuthorizationID, caller *UserID)`; `caller` is nil on the webhook path.

1. `CardAuthorization.Get`. NotFound, a Checkout's card authorization, or a `user_id` other than the caller → PermissionDenied; on the webhook path a Checkout's card authorization returns success without effect. `Get`'s InvalidArgument for a non-JPY PaymentIntent cannot occur for one the platform opened and is returned unchanged.
2. `LotteryEntry.GetByCardAuthorizationID`: when found, return it.
3. Pending, Captured or Released → FailedPrecondition, nothing released.
4. `TicketType.Get` (NotFound → reject), then `authorization.Confirm(purchase, price × count)`, the existing amount and card-brand rule.
5. `LotteryEntry.Create`, which returns the entry that already holds the card authorization.
6. A rejection of an Authorized card authorization calls `CardAuthorization.Release`, then returns the error; a failed release returns its Unavailable instead.

Because `Create` returns the holder's entry under its per-card-authorization lock (below), a release follows only a `Create` that saw no entry holding the card authorization, so a card authorization an entry holds is never released.

The payment provider notice is routed by the webhook adapter straight to `LotteryEntryUseCase.Confirm`, not through `stripeWebhookService`, so no usecase calls another usecase (schema "usecase" rule; `PaymentFulfiller` inside `stripeWebhookService` is an existing deviation this change does not extend). The notice keeps the endpoint's processed-event row ("Each notice is applied at most once"): the adapter checks and records it around the `Confirm` call as it does around `stripeWebhookService`, so a failed `Confirm` is not recorded and is redelivered. The adapter acknowledges PermissionDenied, FailedPrecondition and InvalidArgument (already released or not releasable) and answers Internal otherwise.

### Check-then-act and locked rows

| Write | Check | Rows locked | Paths that create the same rows |
|---|---|---|---|
| `LotteryEntry.Create` | no entry holds the card authorization; no entry of the user for the TicketType; the sale's end time not passed | one transaction: `pg_advisory_xact_lock(hashtext(card_authorization_id))`, then a read of the entry holding the card authorization (returned when found), then `INSERT … SELECT … FROM ticket_types JOIN ticket_sales WHERE clock_timestamp() < end_at`; unique indexes on `(ticket_type_id, user_id)` and on `card_authorization_id` reject a second insert; `SET LOCAL lock_timeout = '10s'` and `statement_timeout = '10s'` bound the wait | every entry is inserted by this transaction, and every caller for one card authorization takes the same advisory lock |
| `LotteryEntry.Create` against `DeleteAndSuppress` | the TicketType still exists | the insert's foreign-key check takes FOR KEY SHARE on the `ticket_types` row; `eventRemovalLockQueries` locks it FOR UPDATE (`event_removal.go:41`) | the insert waits for the delete and then fails on the foreign key → FailedPrecondition → release |
| `Checkout.SetReferralCode` | the Checkout is Held | one statement, `UPDATE checkouts SET referral_code = $2 WHERE id = $1 AND status = Held`; a zero row count is followed by an existence read | Commit, Expire and Release change the status of the same row |
| Draw against a late `Confirm` | an entry is drawn only if inserted before the draw reads | none; the insert refuses after `end_at` by the database clock, and `ListDueForDraw` returns a sale only 1 minute after `end_at`, longer than one insert transaction, whose waits are bounded to 10 seconds | — |

`AuthorizeCard`'s "already entered" check is advisory: it spares the fan a card authentication that `Create` would refuse, and `Create` stays the guard.

### Referral code as two columns

`checkouts.referral_code` and `lottery_entries.referral_code` (`TEXT`, NULL when none, `CHECK (referral_code ~ '^[a-z0-9-]{1,32}$')`). `Order.ListReferralStatsByEvent` groups Paid Orders by `COALESCE(c.referral_code, le.referral_code)` through `orders.checkout_id` or `orders.lottery_entry_id`. The `create time` of a Referral is dropped: no requirement reads it (`referral/record` spec sets it, nothing reads it).

### Schema migration

One Atlas migration in backend:

1. `ALTER TABLE checkouts ADD COLUMN referral_code`, `ALTER TABLE lottery_entries ADD COLUMN referral_code`; copy `referrals.code` onto each source; `DROP TABLE referrals`.
2. `DELETE FROM lottery_entries WHERE state IN (4, 5)` (Withdrawn and Draft; prod holds none).
3. `card_authorization_id SET NOT NULL`; replace `chk_lottery_entries_state` with `state IN (1, 2, 3)`; drop `chk_lottery_entries_authorized_from_entered`; replace `uq_lottery_entries_active` with `uq_lottery_entries_ticket_type_user (ticket_type_id, user_id)`; add `uq_lottery_entries_card_authorization_id`; drop `idx_lottery_entries_ticket_type_id`, which the new unique index covers.
4. Update the table and column comments.

### Proto

- `LotteryEntryService`: `Start`, `StartRequest` and `StartResponse` are deleted.
  - `AuthorizeCardRequest` reserves field 1 (`lottery_entry_id`) and adds `ticket_type_id = 4`, `ticket_count = 5` (`gte: 1`, `lte: 10`, as `StartRequest` had) and `optional ReferralCode referral_code = 6`.
  - `AuthorizeCardResponse` adds `card_authorization_id = 3`.
  - `ConfirmRequest` reserves field 1 and adds `card_authorization_id = 2`.
  - `ConfirmResponse` is unchanged.
- `LotteryEntryState` reserves 5 and `LOTTERY_ENTRY_STATE_DRAFT`.
- `LotteryEntry.card_authorization_id` becomes required, and the CEL rule `lottery_entry.card_authorization_from_entered` is removed.
- No `referral_code` field is added to `LotteryEntry` or `Checkout`: no screen reads it (the organizer stats read `referral_code_stats`, which is unchanged).
- The `ReferralCode` comment drops its sentence about the Referral.
- The `rpc-design` skill line "A multi-step purchase uses the same verbs everywhere…" (`.claude/skills/rpc-design/SKILL.md:41`) is rewritten:
  - A Checkout uses `Start`, `AuthorizeCard` and `Confirm`.
  - A lottery entry uses `AuthorizeCard`, which opens the CardAuthorization for a TicketType and count, and `Confirm`, which makes the entry from it.
- The PR carries `buf skip breaking`.

### Screens

- The lottery entry screen calls `AuthorizeCard` with the chosen count, the details and the kept code, and keeps `card_authorization_id` and `card_authorization_secret`.
- After 3D Secure it calls `Confirm(card_authorization_id)` and shows the returned `lottery_entry`.
- A count change calls `AuthorizeCard` again.
- The status screen reads `ListByTicketType` as today; its `draft` handling is removed.

### Main-spec Purposes, edited at archive

The Purpose edits listed in proposal.md are applied at archive, as `remove-lottery-entry-withdrawal` planned. The story diagram check (`check-story-diagrams.py`) compares a story's Purpose with its requirement text, and the requirement text changes only at archive.

- **`components/entity/lottery-entry`**
  - The text says the entry is made when the fan confirms after authorizing the card.
  - Table rows: card authorization is required and set at creation; referral code is optional, set at creation and never changed; state is Entered, Won or Lost.
  - erDiagram: `CardAuthorization ||--o| LotteryEntry : "pays for"`; the Referral line is removed.
  - stateDiagram: `[*] --> Entered --> Won | Lost`.
- **`components/entity/card-authorization`**
  - New rows, all fixed at creation: purchase (a Checkout or a lottery entry), user, ticket type, ticket count, and referral code (optional, lottery entry only).
  - erDiagram adds User, TicketType and `CardAuthorization ||--o| LotteryEntry`.
- **`components/entity/checkout`**
  - New row: referral code (optional; changeable only while Held).
  - The Referral line leaves the erDiagram.
- **`components/entity/referral`**
  - The Purpose describes only the ReferralCode value and that a Checkout or LotteryEntry keeps it as its referral code.
  - The table and the erDiagram go.
- **`stories/win-tickets-in-a-lottery`**
  - The first sentence becomes "A fan authorizes their card for a number of tickets and confirms the entry…".
  - The usecase diagram loses `LotteryEntryUseCase.Start` and `LotteryEntryUseCase.Withdraw`.
- Specs left without requirements are deleted: `lottery-entry/get-or-create-draft`, `set-card-authorization`, `update-state`, `usecase/lottery-entry/start`, `withdraw`, `referral/record`, `referral/list-stats-by-event`.

## Risks / Trade-offs

- [The webhook is down for more than 3 days] → An Authorized card authorization without a `Confirm` call stays held until it lapses. This is the same dependency as Order fulfilment today. No alert watches the webhook endpoint yet (`monitoring.ts` has none); the gap is shared with fulfilment and tracked in liverty-music/cloud-provisioning#704.
- [A release after a rejection fails] → `Confirm` returns Unavailable and the webhook redelivery retries the release. A durable retry comes with `make-lottery-draw-durable`.
- [A fan's browser closes after 3D Secure] → The entry is made by the webhook without the fan seeing the done screen. The status screen shows it Entered.
- [A notice delayed past the end time, during a deploy for example] → The fan who authenticated just before the end is released, as the story states ("Entry made only after the window closed"): only an entry made before the end time counts.
- [The draw starts 1 minute later than today] → The story's timing becomes "within 2 minutes after the window closes".

## Migration Plan

1. specification PR: proto, the `rpc-design` rule, this change, and the deletion of `remove-lottery-entry-withdrawal`. Merge, then Release and BSR generation.
2. cloud-provisioning PR: subscribe the webhook endpoint to `payment_intent.amount_capturable_updated`. The backend ignores the notice until step 3 deploys, which is safe.
3. backend PR: code and the Atlas migration. Deploy, then confirm the AtlasMigration, the rollout and the Stripe sandbox E2E.
4. frontend PR: the entry screen and the status screen.
5. Archive: apply the Purposes above and delete the emptied specs.

Rollback: revert the backend release. The migration is not reversible for the deleted Draft rows and the dropped `referrals` table; the codes stay in the new columns.
