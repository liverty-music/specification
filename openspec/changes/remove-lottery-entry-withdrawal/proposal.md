## Why

A fan can withdraw a lottery entry until the draw, and the Withdrawn state that supports it adds rules to every lottery operation: what counts as an "active" entry, which entries the draw settles, and when a fan may enter again. The withdrawal also opens a race with the draw: an Entered winner can still be withdrawn while the draw captures its card authorization, because the guard reads only the entry's state. And replacing a Draft with another ticket count makes the old Draft Withdrawn without releasing its card authorization, so the amount can stay held on the fan's card until the authorization expires (up to 30 days for a JPY card). The product decision is that a confirmed entry cannot be given up, so the withdrawal and its state go, and the simpler lottery that remains is the base for the follow-up change that redesigns the draw on durable execution.

## What Changes

- **BREAKING** A fan can no longer withdraw a LotteryEntry, before or after the window closes. `LotteryEntryService.Withdraw` and `LotteryEntryUseCase.Withdraw` are removed, and the lottery entry status screen loses its withdraw action.
- **BREAKING** The LotteryEntry state Withdrawn is removed. The states are Draft, Entered, Won and Lost, and a fan has at most one entry per TicketType in any state. The proto enum value is reserved.
- Changing the ticket count of a Draft changes that Draft in place instead of replacing it. When the Draft already has a card authorization, the change removes it and `LotteryEntryUseCase.Start` then releases it, so the fan authorizes again for the new amount. This fixes the authorization that the replacement left held.
- A Draft that is still unconfirmed at the draw stays a Draft: the draw releases its card authorization, as today, and no longer changes its state. `LotteryEntry.PersistDrawOutcome` no longer takes Drafts.
- Existing Withdrawn entries are deleted by the schema migration, and the partial uniqueness of entries per account and TicketType becomes a full uniqueness.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/entity/lottery-entry` (Purpose): the state table and the state diagram lose Withdrawn. The requirements "Active entries" and "Withdrawable only before the draw" are removed, and "Confirmable only as a Draft with a card authorization" no longer names Withdrawn.
- `components/entity/lottery-entry/get-or-create-draft`: a Draft with another count is changed in place and loses its card authorization; there is no re-entry after a withdrawal.
- `components/entity/lottery-entry/get`: returns an entry in any of the four states.
- `components/entity/lottery-entry/list-by-ticket-type-and-user`: the scenario of a Withdrawn entry next to a later entry goes.
- `components/entity/lottery-entry/get-stats-by-ticket-type`: the exclusion scenario names Drafts only.
- `components/entity/lottery-entry/list-undrawn-for-ticket-type` (Purpose): the Drafts are the ones whose card authorization the draw releases, not ones it withdraws.
- `components/entity/lottery-entry/persist-draw-outcome` (Purpose): records winners and losers and the sale's draw time; Drafts are not part of the outcome.
- `components/entity/lottery-entry/update-state`: the example transition is Draft to Entered.
- `components/entity/order/list-lottery-entry-ids-awaiting-issuance`: the "not won" scenario names Entered and Lost.
- `components/usecase/lottery-entry/withdraw`: removed.
- `components/usecase/lottery-entry/start`: releases the Draft's card authorization before a count change; no re-entry after a withdrawal.
- `components/usecase/lottery-entry/run-draw`: unconfirmed Drafts keep their state.
- `components/usecase/order/issue-from-captured-win`: the "entry not won" scenario names Draft, Entered and Lost.
- `components/adapter/fan/api/rpc/lottery-entry`: the service has no Withdraw call.
- `stories/win-tickets-in-a-lottery` (Purpose): the usecase diagram loses `LotteryEntryUseCase.Withdraw`. The requirement "A fan can withdraw before the draw" is replaced by one that keeps the unconfirmed-Draft rule and adds the count change.

Unchanged and why: `components/entity/card-authorization` and its `release` operation already cover the release that Start now calls; `components/entity/referral` already limits a Referral's code changes to a Draft, and an in-place count change keeps the Draft's Referral; `components/usecase/lottery-entry/confirm` and `authorize-card` only act on a Draft and never named Withdrawn.

## Impact

- **specification**: `proto/liverty_music/rpc/lottery_entry/v1/lottery_entry_service.proto` loses the `Withdraw` RPC and its messages; `proto/liverty_music/entity/v1/lottery_entry.proto` reserves `LOTTERY_ENTRY_STATE_WITHDRAWN = 4`. Both are breaking changes and need the `buf skip breaking` label.
- **backend**: removes the Withdraw handler and usecase and `LotteryEntry.IsWithdrawable` / `IsActive`; changes `GetOrCreateDraft`, `PersistDrawOutcome`, `RunDraw` and `Start`; adds an Atlas migration that deletes Withdrawn rows and replaces `uq_lottery_entries_active` and the state checks.
- **frontend**: removes the withdraw action and the `withdrawn` result from the lottery entry status screen, its i18n keys and the `withdrawn` value of the lottery entry state.
- **Legal**: the Terms of Service article for lottery entries (that a confirmed entry cannot be withdrawn) is left to the change that brings the lottery to real money, as `payments-legal-compliance` leaves the lottery entry screen to it (liverty-music/specification#1074). The lottery is not used in the pilot.
- **Follow-up**: the redesign of the draw on durable execution (DBOS) builds on the four states.
