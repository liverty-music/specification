## Context

See proposal.md - Why. The state that this change removes is wired through four layers:

- **Schema** (`backend/k8s/atlas/base/migrations/20261011000000_unify_ticket_sales.sql:170-174`): `chk_lottery_entries_state CHECK (state BETWEEN 1 AND 5)`, `chk_lottery_entries_authorized_from_entered CHECK (… IS NOT NULL OR state IN (4, 5))` (the column is now `card_authorization_id`, renamed in `20261012000000_one_name_per_concept.sql:73`), and the partial unique index `uq_lottery_entries_active ON lottery_entries(ticket_type_id, user_id) WHERE state <> 4`.
- **Repository** (`backend/internal/infrastructure/database/rdb/lottery_entry_repo.go`): `GetOrCreateDraft` locks the user's active entry with `lotteryEntryActiveOfUserQuery … state <> 4 FOR UPDATE`, makes a Draft with another count Withdrawn with `lotteryEntryWithdrawDraftQuery`, and inserts a new Draft. `PersistDrawOutcome` sets unconfirmed Drafts to Withdrawn.
- **Usecase and RPC**: `LotteryEntryUseCase.Withdraw` (`lottery_entry_uc.go:381-397`), `LotteryEntryHandler.Withdraw` (`lottery_entry_handler.go:111`), `LotteryEntry.IsWithdrawable` / `IsActive` (`entity/lottery_entry.go:126-135`).
- **Frontend**: the withdraw action and the `withdrawn` result of `lottery-entry-status-route` and `entities/lottery-entry.ts`.

The replaced Draft keeps its `card_authorization_id`, and `ListUndrawnForTicketType` returns only Draft and Entered entries, so the draw never releases that authorization: this is the leak the proposal names.

## Goals / Non-Goals

**Goals:**
- Four states (Draft, Entered, Won, Lost) everywhere: schema, entity, proto, frontend.
- A count change keeps the Draft and gives back the card authorization it had.

**Non-Goals:**
- The redesign of the draw (draw outcome recorded before any capture, durable execution). It is the follow-up change and keeps the four states.
- The Terms of Service article for lottery entries (see proposal.md - Impact).
- Durable retry of a failed release. Until the follow-up change, a failed release is reported to an admin, as the draw does today.

## Decisions

### A count change updates the Draft in place

`GetOrCreateDraft` keeps its lock: it reads the user's entry for the TicketType with `FOR UPDATE` (the filter `state <> 4` goes), and for a Draft with another count runs, in the same transaction,

```sql
UPDATE lottery_entries
SET ticket_count = $2, card_authorization_id = NULL
WHERE id = $1 AND state = 5
RETURNING …  -- with the old card_authorization_id read under the lock
```

and returns the Draft and the old `card_authorization_id`.

- **Why in place, not replace**: a replaced Draft needs a terminal state, which is the Withdrawn this change removes, or a delete. A delete cascades the Draft's Referral (`20261015144549_create_referrals.sql:18`, `ON DELETE CASCADE`), so the fan would lose the attribution of a link they came from. The in-place update keeps the id and the Referral.
- **Why the old card authorization is removed**: its amount is the old count times the price, and `Confirm` accepts only an authorization for the current amount (entity spec "Confirmable only as a Draft with a card authorization"). Keeping it would leave a Draft that can never be confirmed.

### The release happens after the change, never before

`Start` releases the card authorization that `GetOrCreateDraft` returned, after the transaction has committed.

Rejected: release first, then change the Draft. The release is a payment provider call and cannot run inside the transaction. Between the two steps another request of the same fan (`AuthorizeCard` in a second tab) can record a new authorization on the Draft, and the later change would then remove an authorization nobody released. Removing inside the locked transaction and returning exactly the removed id leaves nothing unaccounted for: an authorization recorded after the commit belongs to the new count.

When the release fails, `Start` still returns the changed Draft and logs `LogKeyNeedsOperator` with the card authorization id, so the existing alert (`cloud-provisioning/src/gcp/components/monitoring.ts:269`) tells an admin. The fan's step does not fail for a platform-side release.

### Check-then-act and locked rows

| Write | Check | Rows locked | The paths that create or change those rows lock the same rows |
|---|---|---|---|
| `GetOrCreateDraft` count change | the entry is a Draft and its count differs | the user's entry for the TicketType, `FOR UPDATE` | `SetCardAuthorization` updates the same row (`WHERE id = $1 AND state = 5 AND (card_authorization_id IS NULL OR …)`) and waits for the lock; `UpdateState` (Confirm) updates the same row |
| `GetOrCreateDraft` create | the user has no entry for the TicketType | none to lock; the unique index on `(ticket_type_id, user_id)` rejects the second insert, and the loop re-reads the winner (`getOrCreateDraftAttempts`) | every insert goes through the same statement |

A Confirm racing a count change cannot make an Entered entry without an authorization: `chk_lottery_entries_authorized_from_entered` rejects it. A Confirm that checked the old authorization and then sets Entered after a new one was recorded leaves an Entered entry whose authorization may not be completed; its capture then fails at the draw and the entry is Lost, so the fan is never charged. This needs three requests of one fan in the same moment, and the outcome is safe, so no extra lock is added.

### The draw leaves Drafts as they are

`RunDraw` keeps releasing the card authorization of each unconfirmed Draft and no longer passes Drafts to `PersistDrawOutcome`; the Draft stays a Draft. Rejected: deleting the Drafts at the draw, for the Referral reason above and because a Draft after the window closed is inert (`Start`, `AuthorizeCard` and `Confirm` all refuse a closed window, and `ListByTicketType` callers already skip Drafts: `lottery-entry-status-route.ts:32`).

### Schema migration

One Atlas migration in backend:

1. `DELETE FROM lottery_entries WHERE state = 4;` (their Referrals cascade).
2. Drop `uq_lottery_entries_active`; create `uq_lottery_entries_ticket_type_user UNIQUE (ticket_type_id, user_id)`.
3. Replace `chk_lottery_entries_state` with `state IN (1, 2, 3, 5)` and `chk_lottery_entries_authorized_from_entered` with `card_authorization_id IS NOT NULL OR state = 5`.
4. Update the column and index comments that name Withdrawn.

The values stay as they are (Draft is 5); renumbering would touch every query for no behavior.

### Proto

`LotteryEntryService.Withdraw`, `WithdrawRequest` and `WithdrawResponse` are deleted, and `LotteryEntryState` gets `reserved 4; reserved "LOTTERY_ENTRY_STATE_WITHDRAWN";`. The comments that describe withdrawal (`lottery_entry_service.proto:31,46,108-125`, `lottery_entry.proto:23-24,60`) are rewritten. The PR carries the `buf skip breaking` label. No user is affected: the product has no users and the lottery is not used in the pilot.

## Risks / Trade-offs

- [A Withdrawn entry in prod still has an authorization held at the payment provider] → Before the migration, list `state = 4` rows with a `card_authorization_id` read-only and release each one by hand in the Stripe Dashboard if it is still uncaptured; a JPY authorization otherwise expires within 30 days.
- [A failed release on a count change leaves an authorization held] → Reported with `LogKeyNeedsOperator`; the follow-up change makes the release durable.
- [The backend ships before the frontend and the fan's withdraw button calls a removed RPC] → The button disappears in the same release train; until then the call fails with Unimplemented and nothing changes, which is safe.

## Migration Plan

1. specification PR (proto and this change's tasks), merge, Release, BSR generation.
2. backend PR: code and the Atlas migration, after the read-only prod check of `state = 4` rows. Deploy, then confirm the AtlasMigration status and the rollout.
3. frontend PR: remove the withdraw action and the `withdrawn` value.
4. Archive: apply the Purpose edits to the main specs and delete the emptied `components/usecase/lottery-entry/withdraw` spec.

Rollback: revert the backend release. The migration is not reversible for the deleted Withdrawn rows, which are test data.
