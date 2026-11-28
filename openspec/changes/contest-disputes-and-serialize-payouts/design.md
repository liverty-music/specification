## Context

See proposal.md for why. The state of the code the design starts from (backend `main`, 2026-11-28):

- `usecase/settlement_release_workflow.go` registers `release-due-settlements` on the schedule `0 */5 * * * *` and runs the whole sweep as one step. Inside it, `settlement_uc.go` `releaseOne` goes through, for each Held Settlement:
  - `CreatePayout` per split: a Stripe Transfer with idempotency key `settlement-transfer:<settlement>:<payee account>` and `source_transaction`;
  - then `MarkReleased` (`UPDATE ... WHERE status = 1`). A FailedPrecondition there is logged as "concurrent sweep" and ignored.
- `usecase/order_refund_uc.go` `Refund`:
  - reads the Settlement;
  - reverses the splits only when it read Released;
  - commits with `refund_repo.go` `markReversedTxQuery` (`UPDATE settlements SET status = 3 WHERE id = $1 AND status IN (1, 2)`).

  The webhook `handleDisputeCreated` calls it with the reason Dispute; the admin `RefundOrder` RPC calls it with either reason.
- Nothing handles `charge.dispute.closed`, although the endpoint is subscribed to it (cloud-provisioning `src/index.ts`).
- `stripe_card_authorization.go` creates manual-capture PaymentIntents with automatic payment methods and no `request_three_d_secure`. 3D Secure therefore runs only when Stripe or the issuer asks for it. Stripe's Japan exemptions skip it for debit and prepaid cards and for wallets ("日本の 3D セキュア必須化の例外": an exempted payment gets no liability shift unless `request_three_d_secure: any` is set).
- Resale closes at the event day's last draw (`components/entity/resale-listing`, "Close time": 12:00 on the event day at the latest). Resale therefore never runs alongside a payout, which starts 7 days after the event. The only writers that can meet a payout on the same Settlement are the dispute paths this change adds.
- The legal frame is in `components/entity/settlement` (Purpose): 収納代行 with the Organizer as 販売業者, the platform bearing a negative balance on an Organizer's payout account. `payments-legal-compliance` adds the 返品特約 (no returns except 中止) and the EMV 3DS attestation.

What Stripe does with a dispute (docs.stripe.com, read 2026-11-28):

| Fact | Source |
|---|---|
| On `charge.dispute.created` Stripe debits the disputed amount and the dispute fee from the platform balance, for destination charges and separate charges and transfers alike | `connect/disputes`, `disputes/how-disputes-work` |
| A Japanese business pays the dispute received fee, which is never returned, and no dispute countered fee, so contesting costs nothing extra | `disputes/how-disputes-work` ("dispute fees") |
| A platform that contests waits for the outcome before reversing the transfer: if it wins, the transfer is not reversed; if it loses, it is reversed. If it accepts, it may reverse at once | `connect/disputes` |
| The issuer decides within up to 3 months; the funds return on a win | `disputes/how-disputes-work` |
| "Product not received" is overturned by showing the product was delivered or the expected delivery date has not passed. For offline services (event tickets), the refund or cancellation policy shown before purchase is the main evidence | `disputes/categories` |
| A fraud claim on a payment authenticated with 3D Secure usually shifts liability to the issuer, but successful authentication does not guarantee it; Stripe adds the 3DS data to the evidence. Wallet cryptograms (Apple Pay, Google Pay) may carry the same shift. A fraud claim without either is rarely won, and Stripe advises accepting it when the payment was fraudulent | `payments/3d-secure/authentication-flow`, `disputes/categories` |
| An inquiry (`warning_*` statuses) withdraws no funds; it is resolved without a dispute fee by satisfactory evidence or by a full refund. An unanswered inquiry escalates to a chargeback, and `charge.dispute.funds_withdrawn` reports the withdrawal | `disputes/how-disputes-work` (inquiries), `connect/disputes` ("照会では Stripe が資金を引き落とさない"), `api/events/types` |
| A transfer that is fully reversed cannot be reversed again; the call returns an error. An idempotency key reused after it was pruned (24 hours) makes a new request | `api/transfer_reversals/create`, `api/idempotent_requests` |
| `refund_policy` is a file upload ID; the text fields share a limit of 150000 characters | `api/disputes/update` |

## Goals / Non-Goals

**Goals:**

- The money rule of the proposal ("each yen ends with the party entitled to it") decides every branch below. Where a branch could be argued either way, this document names the entitlement it follows.
- No payout is ever unrecorded, and no claw-back is ever skipped because of a race.
- A contested dispute changes nothing for the fan or the Organizer until its outcome.

**Non-Goals:**

- **Passing the dispute fee to the Organizer.** The owner decided (2026-11-28) that the Organizer bears the dispute received fee when a dispute is lost or accepted, and the platform bears it when it is won, as Universe does and as Peatix's payout terms allow ("チャージバックその他当社に対して支払われるべき金額" deducted from the payout). It needs a term in the Organizer agreement and a deduction from a later payout, since a lost dispute after the payout leaves nothing on that transfer; both are a change of their own (liverty-music/specification#1504). Until it ships, the platform bears the fee.
- **Refunding on early fraud warnings** (`radar.early_fraud_warning.created`). With 3D Secure asked on every card authorization (Decision 6), most fraud claims can be contested on the cardholder's verification, though authentication does not guarantee the liability shift. Every dispute already pages an admin (Decision 10), which is the monitoring this volume needs; a refund rule on warnings is added when the dispute count makes the network monitoring programs a concern (`disputes/measuring`).
- **An admin screen for disputes.** Disputes and their evidence are visible in the Stripe Dashboard, and a stuck workflow pages an admin.
- **Recording the fan's consent at the 特商法 final confirmation.** The evidence states the refund rule that the confirmation screen shows (`components/infrastructure/fan/web/route/checkout`). A stored per-Order consent would be stronger; that belongs to `payments-legal-compliance`.

## Decisions

### 1. The dispute response follows entitlement, not timing or winnability

The question for each dispute is: under the sale, is the cardholder entitled to this money? That is decided by who authorized the payment and whether the service was, or still is, available as sold. The rule is `components/entity/dispute` "Response to a dispute"; the first row that applies wins:

| # | Situation | Entitled | Response | Why |
|---|---|---|---|---|
| 1 | No evidence due time (the provider accepts no evidence) | — | Accept | It cannot be contested |
| 2 | The Order's own refund was made: recorded on the Order, or found at the provider (`Order.GetProviderOwnRefund`) | The fan already has the money | Contest, with the refund as evidence | Accepting would pay the fan twice. Reading the provider closes the race in which `Refund` refunded the card but had not committed when the dispute arrived |
| 3 | Event CANCELLED | Fan | Accept | 中止 entitles the fan to the money |
| 4 | The Event's cancellation limit (24 hours after its start) passed and no Ticket of the Event was admitted (`Admission.CountByEvent` = 0), any reason | Unknown | Review | It may be an Organizer that does not scan tickets, or a concert that did not happen and was never cancelled (an Organizer no-show); contesting the latter, even a verified fraud claim, would pay the Organizer for a performance it did not give |
| 5 | Fraud claim, cardholder verified the payment (3DS `authenticated`, or a wallet cryptogram) | Organizer | Contest | The verification shows the cardholder authorized it. `attempt_acknowledged` means no one authenticated the cardholder, so it is no evidence of authorization, whatever the liability shift |
| 5 | Fraud claim, not verified | Probably the cardholder | Accept | Nothing shows the cardholder authorized it; keeping the ticket valid would let someone who paid with another person's card enter |
| 6 | Duplicate, not as described, card-network compliance | Unknown | Review | A double tap, a misdescribed sale or a broken network rule is a fact the records do not hold |
| 7 | Any other reason (not received, not recognized, cancelled, refund not processed, other) | Organizer | Contest | The cardholder authorized it, the Ticket was delivered to their account, and the sale has no returns except 中止 (返品特約). Before the event the service is still available; after it the fan entered or did not come |

**Review** pages an admin (Decision 10), who answers in the Stripe Dashboard. Without an answer by 48 hours before the due time, the dispute is contested.

**Inquiries** follow the same rule:
- Accepting an inquiry means `Respond` refunds the disputed amount first, at most the fan's remaining claim (`Order.CreateRefund` for the Dispute, key `dispute-refund:<dispute>`, skipped when nothing is left), then records it Accepted. The provider took nothing back, and a full refund resolves an inquiry without a dispute fee.
- When the refund fails because the inquiry escalated meanwhile (the provider refuses a refund on a charged-back payment), `Respond` syncs the dispute and answers the chargeback.
- Accepting a chargeback is `POST /v1/disputes/{id}/close`.

The decision is taken again when the evidence is due (Decision 3), so an Event cancelled after the dispute opened turns a contest into an accept.

Alternatives rejected:

- **Accept every dispute before the event** (the earlier `dispute-representment`). It ignores who authorized the payment and refunds a fan who changed their mind instead of using official resale, which the no-returns term exists for. Stripe's own category guidance says the expected delivery date not having passed overturns a "not received" claim.
- **Contest only with an Admission.** It concedes every no-show, but a no-show is not entitled to a refund under the sale.
- **Contest everything.** It keeps a defrauded cardholder's money from them until the issuer rules, keeps a ticket bought with a stolen card valid, and pays an Organizer that did not perform.

Whether 割賦販売法's 抗弁の接続 (the cardholder's right to withhold payment from the card company for a defence against the seller) applies to any card arrangement used here is a question for counsel under `payments-legal-compliance` (liverty-music/specification#778). It would only strengthen the cardholder's side where the Organizer did not perform, which rows 3 and 4 already cover.

### 2. A disputed Order is held still until the dispute is settled

An Order is disputed while it has an open Dispute (Open, Contested) or an unsettled one (Lost or Accepted, with no settle time). While disputed:

- **The Tickets stay Issued.** Voiding them would take away the service the evidence says is available, and would be wrong if the platform wins.
- **Nothing of it is resold.**
  - No Ticket can be listed.
  - Listed ones are Cancelled, unless a draw allocated them to a Won entry whose charge is under way.
  - Draws skip its listings.

  A resale refunds the seller from the same charge, so the fan could get money from both the resale and the dispute.
- **No payout** (Decision 4) and **no 中止 refund** (Decision 8).

Implementation:

- **Where the checks live**:
  - `ResaleListing.Create`, the entity operation, checks inside its own transaction, so the check and the insert are atomic;
  - the draw's free-listing query excludes disputed Orders in SQL (`resaleEntryFreeListingsQuery`);
  - `DisputeUseCase.Respond` calls `ResaleListing.CancelListedByOrder` after `Dispute.Sync` has committed.
- **Lock order**: `Dispute.Sync` takes the Order row `FOR UPDATE` in the transaction that inserts or updates the dispute. `ResaleListing.Create` takes the Order row `FOR SHARE` before its existing Ticket lock, then checks and inserts. Listings among themselves still do not block each other.
- **Deadlock**: `Order.CommitRefund` today locks Tickets, then Settlement, then updates the Order (`refund_repo.go`). With Create taking Order and then Ticket, the two would deadlock. This change makes `CommitRefund` take the Order row `FOR UPDATE` first. Every path that writes an Order's rows is then audited to lock in the order Order → Tickets → listings → Settlement: issuance (`issuance_repo.go` `lockSettlement`), resale sold, event removal. A two-connection test of Create against CommitRefund proves it (tasks 6.1, 6.7).

### 3. Evidence is submitted when it is strongest, and before the deadline

For a contest or a review, `Respond` starts `DisputeUseCase.SubmitEvidence` as a delayed workflow (`usecase.WithDelay`). Its id is `dispute-evidence:<provider dispute id>:<evidence due time>`, so a repeated `Respond` schedules nothing new, while an escalation, which brings a new due time, schedules its own.

The submission time is the earlier of:
- the Event's cancellation limit, 24 hours after its start (Decision 5): by then every Admission exists, and a cancellation can no longer come. An Event with no start time has no such moment, so only the next point applies;
- the evidence due time minus 48 hours.

When that moment has passed, it runs at once. A review found at that time, earlier than 48 hours before the due time, reschedules once for that later time (`...:<due time>:review`).

The evidence (`Dispute.SubmitEvidence`, `POST /v1/disputes/{id}` with `submit=true`), text fields only:

| Item | Field |
|---|---|
| The purchase: Order id, pay time, amount, ticket count; the event name, date and Venue | `product_description`, `service_date` |
| The account the Tickets are bound to and its email, when the account still exists | `customer_email_address`, `customer_name` |
| The Tickets issued to that account and their issue times | `uncategorized_text` |
| Each Admission's admit time and Scanner | `access_activity_log` |
| The 返品特約 and where the purchase flow shows it | `refund_policy_disclosure`, `refund_refusal_explanation`. `refund_policy` takes a file upload, so no file is sent. The text is the current published terms with their effective date; the terms are not versioned per Order (Risks) |
| Every refund already made from the payment: the Order's own refund and each resale refund (`ResaleListing.ListByOrder`), with amount and time | `refund_refusal_explanation` / `uncategorized_text` |
| For a cancelled or refunded Order, the cancellation and refund | `cancellation_rebuttal` |

The text stays within the provider's 150000-character limit; an Order has at most the event's per-account limit of Tickets. Stripe adds the 3DS data itself.

Before submitting, the port retrieves the dispute:
- `under_review` or `warning_under_review`: the evidence was already taken (a lost response, or an admin answered in the Dashboard), so the Dispute is recorded Contested.
- Closed or escalated: FailedPrecondition. `SubmitEvidence` then syncs the Dispute; a closure or escalation stops it (an escalation has its own `Respond`), and a Dispute still Open means the provider refused evidence, so it is accepted.

### 4. Releases are serialized by a release claim

This replaces the one-step sweep (fixes #922). `release-due-settlements` keeps its schedule and its single step. Inside that step it does two things, each through `usecase.Workflows.Start`, which starts nothing for an id that exists:

1. **Finish unstarted claims.** It lists the Releasing Settlements (`Settlement.ListReleasing`) and starts `release:<release claim>` for each one's Order. This finishes a claim made by a run that stopped before starting its Release.
2. **Claim and start.** It lists the Held Settlements and checks each one's eligibility: event, start time, payout account, the Order not disputed. Each eligible one is claimed under a new release claim (a UUIDv7) and its `release:<release claim>` started (`SettlementUseCase.Release`, deadline 12 hours).

The step sequence of the registered workflow does not change, so no `f.Patched` branch is needed. A run recorded before the deploy that had completed its step replays the recorded result; one that had not re-executes the step with the code now deployed, which is the new body. Either way, nothing pays without a claim.

**`Settlement.Claim`**:

```sql
UPDATE settlements SET status = 4, release_claim = $2
WHERE id = $1 AND status = 1
  AND NOT EXISTS (
    SELECT 1 FROM disputes d
    WHERE d.order_id = settlements.order_id
      AND (d.status IN (1, 2)                                   -- open
           OR (d.status IN (3, 5) AND d.settle_time IS NULL)))  -- unsettled
```

0 rows: FailedPrecondition, and the Settlement is skipped.

The claim is made in the sweep, not inside the Release workflow. If the claim were the Release's first step, a crash between the database commit and DBOS recording the step would replay the claim, get FailedPrecondition and end with the Settlement stuck Releasing. A fixed `release:<settlement>` id would also never run again after a hand-back. Keying the Release by the claim gives each claim exactly one Release, and the next sweep starts it if the claiming run stopped first.

`SettlementUseCase.Release(order, claim)`:

1. `Order.Get`, `Settlement.GetByOrderID`, `PayoutAccount.GetByOrganizerID`. A Settlement no longer Releasing under the claim ends the Release.
2. `Order.GetProviderChargeID`.
3. One step per split, `Settlement.CreatePayout`. DBOS records each step's Transfer ID, so a resumed run never pays twice. The idempotency key stays per Settlement and payee; the 12-hour deadline keeps every retry inside Stripe's 24-hour key retention.
4. `Settlement.MarkReleased`: `UPDATE ... SET status = 2, ... WHERE id = $1 AND status = 4 AND release_claim = $2`. When the Settlement is already Released under that claim with the same payout IDs (the commit landed and the step result was lost), it succeeds without change.

**Error classes**, decided by what each tells about the money:

| Error | What it tells | What happens |
|---|---|---|
| Stripe `invalid_request_error`, or an account that cannot receive transfers (FailedPrecondition, InvalidArgument, PermissionDenied), on `GetProviderChargeID` or on the first payout before any split is paid | Nothing was created | `Settlement.Unclaim` (Releasing → Held, `release_claim` cleared); a later sweep claims it again |
| Stripe `api_error` (5xx) | The outcome is unknown ("Treat the outcome of a request that returns 500 as indeterminate", `error-low-level`). Stripe also stores a 500 under its key, so a retry with the same key returns the same 500 | The port maps it to Internal. The workflow ends with an error and pages an admin, and the Settlement stays Releasing, so no sweep retries it. The runbook checks in the Dashboard whether the transfer exists, then records it or unclaims |
| Network errors, 429 and 503 | Not processed | The settlement and dispute ports map these to Unavailable (today 429 maps to ResourceExhausted, which `isTransient` does not retry), and they are retried |
| A failure after a split was paid | Money moved | Ends with an error, the Settlement stays Releasing, and an admin is paged |

**Lock analysis**:

| Write | Rows locked | Held for | Who else writes the row |
|---|---|---|---|
| Claim | the Settlement row (implicit `FOR NO KEY UPDATE` of the UPDATE); `disputes` only read | one statement | Settle's Held → Reversed or split lowering; all compare-and-set on `status = 1`, so READ COMMITTED makes the second re-check `WHERE` after the first commits and match 0 rows |
| MarkReleased, Unclaim | the Settlement row | one statement | nobody: Releasing is owned by its claim |
| Settle's Reversed / GiveUpDisputedShare | Order, then the Settlement, inside one transaction (Decision 2's order) | one transaction, no external call inside | Claim (above) |

No lock is held across a Stripe call. The dispute check in Claim is not protected by a lock, by design. A dispute that commits after the Claim lets that payout go ahead, and Settle claws it back if the dispute is lost (Decision 7). The check only avoids paying what is likely to come back; correctness does not depend on it.

Alternatives rejected:

- **`SELECT ... FOR UPDATE` held across the Stripe calls**: holds a pool connection (10 per pod) for up to the 30-second Stripe timeout per split, and blocks refunds and issuance behind it.
- **An advisory lock per Settlement**: still has to survive a crashed process, which the claim plus DBOS already does.
- **Finding a lost Transfer afterwards by its `transfer_group`**: the List Transfers API cannot filter by metadata, and the automatic group of `source_transaction` transfers is not documented in English.

### 5. Cancellation ends 24 hours after the start

`Event` gains a cancellation limit, its current start time plus 24 hours, and the guard "cancellable at an instant": PUBLISHED, and the instant before the limit or no start time known. The owner chose this over "until the end of the event day" (2026-11-28):
- it reuses the start time the payout already uses (`Event.GetEventStartTime`, the base of "7 days after the start") instead of adding a date boundary;
- it gives an Organizer whose concert stopped late at night until the next evening to record the cancellation, which the date boundary did not, so no admin cancellation path is needed;
- it leaves 6 days before the payout, so no cancellation can race a payout.

An Event with no start time has no limit and stays cancellable. Its payout is withheld until a start time is known anyway ("Release eligibility").

- **Computing the start instant**: the start instant is computed as `GetEventStartTime` computes it, from the local date, the local start time and the Venue's time zone (`entity.EventStart`). `SeriesRepository.CancelEvents` locks the events with `lockSeriesEventsQuery`, which today reads no Venue; it is extended to join `venues` for `time_zone`, as `getEventStartTimeQuery` does.
- **Where the rule is applied**: `SeriesUseCase.Cancel` already chooses the Events of an unnamed cancel, so it leaves out the ones past their limit there. `entity.PlanCancel` takes the instant and fails a named Event past its limit with FailedPrecondition.

The two release scenarios about a cancellation stored after the run read the event are removed, not rewritten.

### 6. 3D Secure on every card authorization

`CardAuthorization.Create` sets `payment_method_options.card.request_three_d_secure = any`.

- **Gain**: the cardholder's verification on every card that supports 3DS, debit and prepaid included, usually with the liability shift. This is the evidence Decision 1 needs to contest a fraud claim.
- **Cost**: a second authentication screen for the cards that Stripe would otherwise exempt.
- **Wallets**: Apple Pay and Google Pay are not challenged.

`Order.IsCardholderAuthenticated` reads the Charge's `payment_method_details.card`. These count as verified:
- `three_d_secure.result` = `authenticated`;
- a wallet payment made with a network-token cryptogram: Apple Pay always is; Google Pay only when the device tokenized the card, which Stripe reports through the card's network token use.

`attempt_acknowledged` and a Google Pay payment of a card saved in the Google account (no device authentication) do not count. Which Charge field shows the Google Pay token is verified in the sandbox (task 4.3); until it is, only Apple Pay counts among wallets. The operation answers "did the cardholder verify this payment", the evidence of authorization; it does not claim the liability shift, which the issuer decides.

### 7. Syncing and settling a dispute

**Every dispute notice reads the provider.** Stripe does not guarantee event order (`webhooks` "event ordering"). Each dispute notice therefore carries only the provider dispute ID into a workflow, and that workflow's first step is `Dispute.Sync`. Sync retrieves the dispute and upserts it monotonically: an inquiry can become a chargeback, never back; an outcome closes an open Dispute; Accepted stays Accepted.

Webhook mapping:

| Notice | Workflow started |
|---|---|
| `charge.dispute.created` | `dispute:<id>` (Respond) |
| `charge.dispute.funds_withdrawn` | `dispute:<id>:escalated` (Respond), whether or not the dispute is stored yet. Stripe sends it for every chargeback, not only an escalated inquiry, so this run answers only when its `Dispute.Sync` recorded an escalation of a stored inquiry; otherwise the run for `created` answers, and each stage is answered (and alerted) once |
| `charge.dispute.closed` | `dispute-settle:<id>:won` for `won` and `warning_closed`; `dispute-settle:<id>:lost` for `lost` and `prevented` |

The accept paths of `Respond` and `SubmitEvidence` start `dispute-settle:<id>:lost` themselves, so the later closed notice of an accepted dispute starts nothing new. A late `won` (a late win, or an accepted inquiry's `warning_closed`) starts its own run:
- Sync keeps an Accepted Dispute Accepted, and the run ends quietly;
- Sync refuses a Lost Dispute reported Won with FailedPrecondition, and the run pages an admin.

Settle has a 14-day deadline, after which it ends with an error and pages an admin.

**Settle, step by step:**

1. `Dispute.Sync`.
2. **Won**: when the Order is Paid and its Event became CANCELLED while the dispute was open, the fan is owed a 中止 refund that `Refund` refused during the dispute. Settle ends with FailedPrecondition so an admin runs it; `DisputeUseCase` does not call `OrderUseCase` (schema rule). Otherwise Won ends here.
3. **Lost or Accepted**: read the Order, its own refund at the provider (`Order.GetProviderOwnRefund`), and the Settlement. A Releasing Settlement is read again every 10 minutes, at most 72 times (12 hours, the release's deadline), using `f.Recv` on an unused topic with a 10-minute timeout as the durable sleep. `Workflows.Await` is not available inside a workflow (`usecase.Flow` has Step, Start, Recv and the patch calls), and a loop of steps with a bounded count replays deterministically.
4. **Whole Order** (the amount covers the fan's remaining claim: the price of the Tickets not resold, less the amounts of settled partial Disputes): `Order.CommitRefund` with the reason Dispute and the Dispute, which records its settle time in the same transaction:
   - **Held**: the Settlement is given as Held, so it becomes Reversed.
   - **Released**: one step per paid split, `Settlement.ReversePayout` for the Order's refund of what is left of the split (its amount less the claw-backs already made for partial Disputes); then `CommitRefund` with the reversal IDs and the Settlement given as Released.
   - **Reversed**: `CommitRefund` without a Settlement.
5. **Partial**: the Order keeps its Tickets and stays Paid. Only the Organizer's share is taken back: the amount × the Organizer's remaining share (splits less earlier partial claw-backs) ÷ the fan's remaining claim, rounded down, so a split already lowered by a resale or an earlier partial dispute is weighed against what the fan can still claim:
   - **Held**: `Settlement.GiveUpDisputedShare`, which lowers the splits and records the settle time together, and makes the Settlement Reversed when nothing is left.
   - **Released**: `Settlement.ReversePayout` for this Dispute, for the share spread over the paid splits, then `Dispute.MarkSettled` with the reversal IDs.
   - **Reversed** (a 中止 refund or full resale already reversed it): nothing is left to take back; `Dispute.MarkSettled` alone, and the fan-paid-twice check below pages an admin when the Order's own refund was made.
6. **Status moved**: a FailedPrecondition from a compare-and-set means the Settlement's status changed; the workflow reads it again and takes the new branch.
7. **Fan paid twice**: when the Order's own refund had been made and the Dispute was not an accepted inquiry, the fan got the money twice. Settle still settles the Organizer's share, then pages an admin.
8. **Rest of a 中止 refund owed**: a partial Dispute settled while the Event is CANCELLED leaves the Order Paid with its Tickets Issued; `Refund` was refused during the dispute, so Settle pages an admin to refund the rest, as the Won branch does.

**`ReversePayout` once per claw-back.** It is keyed by the claw-back it is for: `settlement-reversal:<settlement>:<transfer>` for the Order's refund, as today, and `dispute-reversal:<dispute>:<transfer>` for a partial Dispute. The create request now also writes that key into the reversal's `metadata`. Before creating, it lists the transfer's reversals (`GET /v1/transfers/{id}/reversals`, all pages) and returns the one whose metadata carries the key. A retry days later, after the idempotency key was pruned, then neither errors on a fully reversed transfer nor reverses twice.

`Order.CommitRefund` changes from `status IN (1, 2)` to the status the caller read (`WHERE status = $expected`), and takes the Dispute it settles.

**The money**: for a chargeback the provider already returned the disputed amount; for an accepted inquiry `Respond` refunded it. The platform recovers the Organizer's share and bears its own fee and any dispute fee.

### 8. OrderUseCase.Refund keeps only 中止

- Disputes no longer pass through `Refund`. Its Dispute branch and the webhook's call to it go away, and the admin `RefundOrder` RPC answers InvalidArgument for `REFUND_REASON_DISPUTE` (the enum value stays, since `Order.refund reason` uses the same values).
- `Refund` refuses a disputed Order (open or unsettled Dispute) with FailedPrecondition, inquiries included. The dispute's answer decides the money, and for a cancelled Event that answer is to accept, which refunds the fan. For a chargeback, Stripe would answer `charge_disputed` anyway.
- `Order.CreateRefund` writes each refund's purpose into its metadata next to its key: the Order's own refund (`order-refund:<order>`, `purpose: order_refund`), a listing's (as today), and an accepted inquiry's (`dispute-refund:<dispute>`, `purpose: dispute_refund`). The keys differ, so an inquiry refund and a later 中止 refund of the rest are separate refunds. `Order.GetProviderOwnRefund` finds the `order_refund` one among the Charge's refunds. Refunds made before this change carry no marker, but no Order has a Dispute yet.
- The 中止 refund is the price of the Tickets still Issued less the amounts of settled partial Disputes, which the fan already got back, so it never asks for more than is left on the charge.
- A Cancellation refund can only meet a Held or Reversed Settlement: a CANCELLED Event is never eligible for release, and since Decision 5 it cannot become CANCELLED after its payout is due. A Releasing or Released Settlement there is reported as Internal.

### 9. Data

- **`disputes`**:

  | column | type and constraint |
  |---|---|
  | `id` | UUIDv7 |
  | `order_id` | FK to `orders`, not unique |
  | `provider_dispute_id` | unique |
  | `inquiry` | boolean |
  | `reason` | smallint: 1 Fraud, 2 NotReceived, 3 Unrecognized, 4 CreditNotProcessed, 5 Duplicate, 6 Other, 7 NotAsDescribed, 8 Compliance |
  | `amount` | the disputed amount |
  | `status` | smallint: 1 Open, 2 Contested, 3 Accepted, 4 Won, 5 Lost |
  | `evidence_due_time` | `TIMESTAMPTZ`, null when the provider accepts no evidence (`evidence_details.due_by` absent) |
  | `evidence_submit_time` | `TIMESTAMPTZ`, null until submitted |
  | `open_time` | `TIMESTAMPTZ` |
  | `close_time` | `TIMESTAMPTZ`, null until closed |
  | `settle_time` | `TIMESTAMPTZ`, null until settled; CHECK only on status 3 or 5 |
  | `provider_payout_reversal_ids` | `TEXT[]`, empty unless a partial Dispute was clawed back after the payout |

  Column names follow backend AGENTS.md "Timestamps" (`*_time`; `scripts/lint-schema.sh` rejects `*_at`).

  Stripe reasons map to `reason`:
  - `fraudulent` and `debit_not_authorized` → Fraud;
  - `noncompliant` → Compliance (a compliance dispute carries a separate network fee and needs a person);
  - `product_not_received` → NotReceived;
  - `unrecognized` → Unrecognized;
  - `credit_not_processed` and `subscription_canceled` → CreditNotProcessed;
  - `duplicate` → Duplicate;
  - `product_unacceptable` → NotAsDescribed;
  - anything else → Other.

  `inquiry` is true when the first status Sync sees starts with `warning_`. A charge can carry more than one dispute ("In rare cases, you might receive more than one dispute per payment ... Handle each dispute separately", `disputes/how-disputes-work`), so `order_id` is not unique and every rule is per dispute.
- **Event removal** (`Concert.Delete`, `Organizer.Delete`, `event_removal.go`): refused while an Order has an open or unsettled Dispute; removes the Disputes of the Orders it removes.
- **`settlements.status`** CHECK gains 4 (Releasing). `settlements.release_claim` (UUID) is set by Claim, kept when Released (MarkReleased matches it on replay), and cleared by Unclaim. Proto `SettlementStatus` gains `SETTLEMENT_STATUS_RELEASING = 4`; the Go enum mirrors it.
- **No announcement for Dispute.** The Order's refund is announced as today (`Order.Refunded`) when a whole-order dispute is settled.

### 10. Every dispute is seen by a person

- **Every dispute**: `Respond` logs each opened dispute at Warn with the Order, the Organizer, the reason and the answer it chose. A log-based alert in cloud-provisioning, next to the one on `workflow.needs_admin`, notifies the admin of each.
- **Admin pages**: a page must come from a workflow that ends in error, because the `needs_admin` reporter selects workflows by their terminal status, not failed steps (`internal/infrastructure/workflow/admin.go`).
  - A Review answer starts a child workflow `dispute-review:<id>:<due time>`, whose only step ends with FailedPrecondition carrying the dispute, while `Respond` or `SubmitEvidence` carries on.
  - A late win, a cancellation refund owed after a win, a fan paid twice, and an evidence submission that misses its deadline end their own workflow with an error.

At the pilot's volume, one notice per dispute is the monitoring: it shows a concentration on one Organizer or one sale before a network program would (`disputes/measuring`).

## Risks / Trade-offs

- **[Risk] A fraudster who bought with a stolen card holds a valid Ticket while a 3DS-authenticated fraud claim is contested.** → An authenticated payment means the cardholder passed the issuer's challenge, so the "stolen card" story is unlikely; and the issuer, not the platform, carries that loss.
- **[Risk] A lost dispute for more than the Tickets not resold pays the fan twice for the resold part.** → The resale refunds are part of the evidence. If the platform still loses, it bears the difference; the Settlement split was already lowered by the resale, so the Organizer is not charged for it.
- **[Risk] A release ends with a payout's outcome unknown, or after a split was paid**: the Settlement stays Releasing, and a lost dispute's Settle waits up to 12 hours and then fails. → Both page an admin. The runbook gets a section on reconciling a Releasing Settlement against the Dashboard. Each sweep restarts `release:<claim>` for every Releasing Settlement, which is a no-op for an ended run; to stop it for good, the runbook unclaims or records the Settlement before deleting a failed run.
- **[Trade-off] `request_three_d_secure: any` adds a challenge** for cards Stripe would exempt, at some cost to conversion. It is accepted: ticket fraud is a known pattern, and an unauthenticated fraud claim can only be accepted.
- **[Risk] An evidence submission fails at the provider until the deadline passes, and the dispute is lost by default.** → Retries on Unavailable up to the due time minus 1 hour (or 1 hour from now when that is sooner, since a deadline in the past cannot be set), then an admin page.
- **[Risk] A resale allocated before the dispute completes during it**: the seller refund is refused on the disputed charge, and `RefundSold` pages an admin. → Rare (the allocation must fall between the listing and the dispute); the admin refunds the seller after the outcome, or not at all when the dispute is lost and the seller got the money back that way.
- **[Risk] The evidence quotes the refund terms as published now, with their effective date, not as shown at the purchase.** → The terms have not changed since paid sales started. A stored per-Order consent with the terms version would close this; it belongs to `payments-legal-compliance`.
- **[Risk] An inquiry's escalation arrives as a new dispute object instead of `funds_withdrawn` on the same one.** → Stripe's documentation does not say which. Both are handled: a new object is a `charge.dispute.created` and gets its own Respond, and `funds_withdrawn` on any dispute starts a Respond that syncs from the provider. Verify which happens in the sandbox E2E (inquiry card `4000000000001976`) and keep the other path tested.
- **[Risk] A Google Pay payment counts as verified only once the network-token field is confirmed.** → Until then only Apple Pay counts, so a Google Pay fraud claim is accepted: the Organizer loses a sale it may be entitled to, the safe side for the cardholder.

## Migration Plan

1. **Proto**: `SETTLEMENT_STATUS_RELEASING`, Release, BSR generation.
2. **Backend**, one PR:
   - the migration (`disputes`, settlements CHECK and `release_claim`);
   - the new workflows, registered in `cmd/worker`;
   - the new body of the single `release-due-settlements` step (no patch, Decision 4);
   - the lock order of `Order.CommitRefund` and the paths audited with it (Decision 2);
   - the webhook handlers, `Refund`, event removal, the Event guard and the 3DS option.

   Before it, a cloud-provisioning PR adds `charge.dispute.funds_withdrawn` to the webhook endpoint's `enabledEvents` (`src/index.ts`) and the log-based alert of Decision 10. Merging runs the dev `pulumi up`; the prod `pulumi up` is the owner's step.

   Merging applies the migration to prod.
3. **Prod check**: the AtlasMigration status, the worker rollout, and one `release-due-settlements` run in the logs starting zero or more `release:` workflows. Then the Stripe Sandbox E2E (`stripe-sandbox-e2e.yml`) with these test disputes:
   - `4000000000002685` (product not received): contested and evidence submitted; the evidence test value `winning_evidence` wins it.
   - `4000000000000259` (fraud): with `request_three_d_secure: any` the sandbox challenge authenticates it, so it is contested.
   - `4000000000001976` (inquiry).
   - `4000000404000079` (multiple disputes on one payment).

Rollback: revert the backend PR after no Settlement is Releasing (`SELECT count(*) FROM settlements WHERE status = 4`, read-only). A Dispute row is ignored by the old code, which concedes disputes again; the `disputes` FK then blocks event removal for those Orders until the rows are dropped.

## Open Questions

None. The owner decided both questions the reviews left open on 2026-11-28: the cancellation limit of Decision 5, and the dispute received fee (Non-Goals).
