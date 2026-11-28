## 1. specification: Releasing status in proto (design Decision 9)

- [ ] 1.1 Add `SETTLEMENT_STATUS_RELEASING = 4` to `proto/liverty_music/entity/v1/settlement.proto`, with a comment saying a release has claimed the Settlement and is paying it out. Open the proto PR with the `buf skip breaking` label only if `buf breaking` flags the new value, merge it, cut the Release, and verify `buf-release.yml` succeeds (`gh run list --repo liverty-music/specification --workflow buf-release.yml --limit 3`).
- [ ] 1.2 In the plan PR worktree, remove `openspec/changes/dispute-representment/`, which this change supersedes (proposal "What Changes"). Verify: `openspec list --json` no longer lists it, and `openspec validate --specs` passes.

## 2. cloud-provisioning: dispute events and the dispute alert (design Decisions 1 and 10)

- [ ] 2.1 Add `charge.dispute.funds_withdrawn` to the Stripe webhook endpoint's `enabledEvents` in `src/index.ts`. Add a log-based alert, next to the one on `workflow.needs_admin`, that notifies the admin of each "dispute opened" log line of design Decision 10. Verify with the Pulumi unit tests for both and a clean `pulumi preview`. Merging runs the dev `pulumi up`; ask the owner for the prod `pulumi up`, then confirm read-only that the endpoint lists the event (Stripe API `GET /v1/webhook_endpoints/{id}`) and the alert policy exists (`gcloud alpha monitoring policies list --configuration=liverty-music`).
- [ ] 2.2 Add a section to `docs/runbooks/workflow-needs-admin.md` for each new admin case, with the read-only commands to inspect it and the `workflow` subcommand or Stripe Dashboard action that finishes it:
  - a Review dispute (duplicate or not as described): answer it in the Stripe Dashboard;
  - a partial dispute after a 中止 refund, where the fan was paid twice and nothing is left to take back (partial disputes are otherwise settled automatically by `DisputeUseCase.Settle`; never reverse a transfer in the Dashboard for one, since a Dashboard reversal carries no claw-back key and would be taken twice);
  - a late win;
  - a cancellation refund owed after a win: run the admin refund;
  - an evidence submission that missed its deadline;
  - a Releasing Settlement whose release failed after a payout;
  - a resale seller refund refused on a disputed charge.

  Verify by following the Review section against a sandbox dispute in task 8.2.

## 3. backend: Event cancellation ends 24 hours after the start (components/entity/event, components/entity/series/cancel-events, components/usecase/series/cancel; design Decision 5)

- [ ] 3.1 Add the cancellation limit (the start instant from `entity.EventStart` plus 24 hours; none without a start time) and the cancellable-at-an-instant guard to `entity.Event`, and make `entity.PlanCancel` take the instant, so a PUBLISHED Event past its limit fails a named cancel. Extend `lockSeriesEventsQuery` to join `venues` for `time_zone`, as `getEventStartTimeQuery` does (design Decision 5). Verify with unit tests annotated `@spec` for "Publish state of an event" (all four scenarios), "Cancellable until 24 hours after its start" (Stopped midway, recorded the next morning; 24 hours after the start; Start time not known; Draft) and "Only cancellable events of the series" (Already cancelled, Concert already held, Unknown series).
- [ ] 3.2 Make `SeriesUseCase.Cancel`, which already chooses the Events of an unnamed cancel, leave out the PUBLISHED ones past their cancellation limit, and pass the current time into `Series.CancelEvents`. Verify with usecase tests annotated `@spec` for every scenario of "Draft or published can be cancelled once", including Rest of a tour and Held concert named.

## 4. backend: Dispute entity and storage (components/entity/dispute and its operations; design Decisions 1, 2, 7 and 9)

- [ ] 4.1 Add the `disputes` table to `schema.sql` as design Decision 9 describes:
  - `order_id` not unique, `provider_dispute_id` unique, `inquiry`;
  - `settle_time` and `provider_payout_reversal_ids`;
  - CHECKs on `reason`, `status` and `settle_time`;
  - a `COMMENT ON` for the table and every column.

  Generate the migration with `atlas migrate diff`, and add `entity.Dispute` with its reason and status enums. Verify: `make lint-schema` passes, and unit tests annotated `@spec` cover:
  - "Open until an outcome";
  - "Unsettled outcome";
  - "Response to a dispute" (all thirteen scenarios);
  - "Whole or partial dispute";
  - "Organizer's share of a partial dispute";
  - "Amount and provider dispute ID".
- [ ] 4.2 Add the dispute port on the payment provider (`internal/infrastructure/payment`), with these operations:
  - `Dispute.Sync`: retrieve the dispute and upsert it monotonically in `rdb`, taking the Order row `FOR UPDATE` first (design Decisions 2 and 7);
  - `Dispute.Accept`: `POST /v1/disputes/{id}/close` for a chargeback; nothing for an inquiry; a dispute the provider already shows as conceded is recorded Accepted;
  - `Dispute.SubmitEvidence`:
    - retrieve the dispute first; `under_review` / `warning_under_review` records Contested, and a closed or escalated dispute returns FailedPrecondition;
    - otherwise send the text evidence of design Decision 3 with `submit=true`, with no `refund_policy` file and within 150000 characters;
  - `Order.IsCardholderAuthenticated` (design Decision 6);
  - `Order.GetProviderOwnRefund`: the Charge's refund carrying the `order_refund` metadata marker.

  Map Stripe errors as design Decision 4's table says: 429 and 503 to Unavailable, 5xx to Internal.

  In the sandbox, find which Charge field shows that a Google Pay payment used a network token, and record it in design Decision 6. Until that is confirmed, count only Apple Pay.

  Verify:
  - unit tests over a stubbed Stripe client, annotated `@spec` for every scenario of `dispute/sync`, `dispute/accept`, `dispute/submit-evidence`, `order/is-cardholder-authenticated` and `order/get-provider-own-refund`;
  - one sandbox integration test that syncs and submits evidence for a `4000000000002685` dispute.
- [ ] 4.3 Implement the remaining store operations in `rdb`:
  - `Dispute.Get`, `Dispute.ListByOrder` and `Dispute.MarkSettled`;
  - `Ticket.ListByOrder` and `Admission.CountByEvent`;
  - `ResaleListing.ListByOrder` and `ResaleListing.CancelListedByOrder` (which leaves only a listing allocated to a Won entry alone).

  Make `Order.CreateRefund` take the Dispute purpose (key `dispute-refund:<dispute>`) and write each purpose into the refund's metadata. Verify with the scenarios of "Refund once per order", including Inquiry refund, then the cancellation refund. Verify with DB integration tests annotated `@spec` for every scenario of `dispute/get`, `dispute/list-by-order`, `dispute/mark-settled`, `ticket/list-by-order`, `admission/count-by-event`, `resale-listing/list-by-order` and `resale-listing/cancel-listed-by-order`.
- [ ] 4.4 Make event removal (`event_removal.go`) refuse while an Order of the events has an open or unsettled Dispute, and delete the Disputes of the Orders it removes. Verify with DB integration tests annotated `@spec` for the modified requirements of `concert/delete` and `organizer/delete` (Concert with a contested dispute, Refunded order with a settled dispute, Settled dispute, Contested dispute, and the unchanged scenarios).

## 5. backend: Settlement claim and serialized release (components/entity/settlement, claim, unclaim, list-releasing, give-up-disputed-share, mark-released, reverse-payout, components/usecase/settlement/release, release-due-settlements; design Decision 4)

- [ ] 5.1 Add the Releasing status and the release claim to `entity.Settlement`, to the `settlements` table (status CHECK and `release_claim` with its comment) and to the proto mapping in `internal/adapter/pb`, after task 1.1's BSR generation (consume-proto-release skill). Change the Release eligibility rule to take the Order's Disputes. Verify with unit tests annotated `@spec` for "Release eligibility" (all six scenarios) and "Released only from Held" (Reversed settlement, Releasing settlement).
- [ ] 5.2 Implement the store side:
  - `Settlement.Claim`: the compare-and-set of design Decision 4;
  - `Settlement.Unclaim` and `Settlement.ListReleasing`;
  - `Settlement.GiveUpDisputedShare`, which locks the Order row first;
  - `Settlement.MarkReleased` changed to require Releasing under the claim, and to succeed unchanged when it is already Released under the same claim and payout IDs.

  Verify with DB integration tests annotated `@spec` for every scenario of `settlement/claim`, `settlement/unclaim`, `settlement/list-releasing`, `settlement/give-up-disputed-share` and "Release recorded once, from Releasing". Add one test that runs `Claim` and `Order.CommitRefund`, with a Settlement read as Held, concurrently on two connections, and shows exactly one of them succeeds.
- [ ] 5.3 Map Stripe 429 and 503 to Unavailable and 5xx to Internal in the settlement port (`CreatePayout`, `ReversePayout`, `CreateRefund`; design Decision 4), and verify with a unit test per status. Change `Settlement.ReversePayout` (design Decision 7):
  - take the claw-back it is for, which keys it as `settlement-reversal:...` or `dispute-reversal:...`;
  - write that key into the reversal's `metadata` on create;
  - before creating, list the transfer's reversals (all pages) and return the one with that key.

  Verify:
  - unit tests annotated `@spec` for "Reverse a payout once" (all five scenarios), asserting the captured create request carries the metadata;
  - the existing sandbox reversal test extended to look up a reversal it created.
- [ ] 5.4 Add `SettlementUseCase.Release(order, claim)` as the workflow `release:<claim>` with a 12-hour deadline:
  - read the Order, the Settlement and the payout account, and end when the Settlement is no longer Releasing under the claim;
  - `GetProviderChargeID`;
  - one step per split for `CreatePayout`;
  - `MarkReleased`;
  - `Unclaim` only on a refusal before any payout;
  - Internal leaves it Releasing.

  Register it in `cmd/worker`. Verify with usecase tests run through the `usecase.Flow` runners (replay included), annotated `@spec` for every scenario of `usecase/settlement/release`.
- [ ] 5.5 Change the single step of `ReleaseDueSettlements` (no patch, design Decision 4):
  - start `release:<claim>` through `usecase.Workflows` for every Releasing Settlement;
  - check eligibility per Held Settlement, claim it under a new UUIDv7 claim and start its Release.

  Verify with usecase tests annotated `@spec` for:
  - "Pay out and mark Released" (Settlement released, Invalid splits, Released concurrently, Claimed but not started);
  - "One failure does not block the others";
  - every scenario of "Release 7 days after the event's current start, not while disputed";
  - the unchanged scenarios of "Payout waits for the Organizer's payout account".

## 6. backend: Dispute response and settlement (components/usecase/dispute/respond, submit-evidence, settle; design Decisions 1, 2, 3, 7, 8 and 10)

- [ ] 6.1 Change `Order.CommitRefund`:
  - take the Order row `FOR UPDATE` first, then Tickets, listings and Settlement;
  - compare-and-set the Settlement from the status the caller passes (`WHERE status = $expected`) instead of `IN (1, 2)`;
  - take a refund amount and provider refund ID for the reason Dispute, and the Dispute it settles.

  Audit issuance (`issuance_repo.go`), resale sold and event removal for the same lock order (design Decision 2). Verify with DB integration tests annotated `@spec` for every scenario of "Refund recorded together", including Dispute recorded, Second dispute on a refunded order and Settlement claimed after it was read.
- [ ] 6.2 Add `DisputeUseCase.Respond` as the workflows `dispute:<id>` and `dispute:<id>:escalated`:
  - `Dispute.Sync`, then the decision of the entity rule from `Order.Get`, `Event.Get`, `Order.GetProviderOwnRefund`, `Admission.CountByEvent` and, for Fraud, `Order.IsCardholderAuthenticated`;
  - the Warn log line of design Decision 10;
  - on accept: for an inquiry, `Order.CreateRefund` first; then `Dispute.Accept`; a FailedPrecondition re-syncs and answers again; then start `dispute-settle:<id>:lost`;
  - on review: start the child workflow `dispute-review:<id>:<due time>` that ends with FailedPrecondition, then continue as for a contest;
  - on contest: `ResaleListing.CancelListedByOrder`, then start `dispute-evidence:<id>:<due time>` with `usecase.WithDelay` until the submission time;
  - Unavailable and ResourceExhausted are retried until the due time, or 1 hour from now when that is absent or nearer.

  Verify with usecase tests through the Flow runners, annotated `@spec` for every scenario of `usecase/dispute/respond`.
- [ ] 6.3 Add `DisputeUseCase.SubmitEvidence`:
  - `Dispute.Sync`, then decide again; accept as Respond does when the answer changed;
  - on review before 48 hours ahead of the due time, start the review page and reschedule once as `...:review`;
  - otherwise gather the Tickets, Admissions, resale refunds, the account (`User.Get`, tolerating NotFound) and the Venue, and call `Dispute.SubmitEvidence`;
  - on FailedPrecondition, sync: stop when closed or escalated, and accept when still Open.

  Verify with usecase tests annotated `@spec` for every scenario of `usecase/dispute/submit-evidence`.
- [ ] 6.4 Add `DisputeUseCase.Settle` as the workflows `dispute-settle:<id>:lost|won`, with a 14-day deadline:
  - `Dispute.Sync`;
  - Won: the cancellation-refund-owed check, and a quiet end for an Accepted Dispute;
  - Lost or Accepted: the whole and partial branches of design Decision 7, including the Releasing re-read every 10 minutes with `f.Recv` as the durable sleep, at most 72 times; the re-read after a FailedPrecondition from a compare-and-set; and the fan-paid-twice page.

  Verify with usecase tests annotated `@spec` for every scenario of `usecase/dispute/settle`.
- [ ] 6.5 Narrow `OrderUseCase.Refund` to the reason Cancellation:
  - InvalidArgument for Dispute;
  - FailedPrecondition while the Order is disputed;
  - Internal for a Releasing or Released Settlement;
  - CommitRefund given the Settlement as Held.

  Remove its Released branch and the webhook's call to it. Verify with usecase tests annotated `@spec` for every scenario of the four modified requirements of `usecase/order/refund`, and an admin handler test that a `REFUND_REASON_DISPUTE` request returns InvalidArgument.
- [ ] 6.6 Change the Stripe webhook as design Decision 7's table says:
  - `charge.dispute.created` starts `dispute:<id>`;
  - `charge.dispute.funds_withdrawn` starts `dispute:<id>:escalated`;
  - `charge.dispute.closed` starts `dispute-settle:<id>:won` or `:lost`, including `prevented`;
  - a conflict on an existing workflow id is acknowledged.

  Verify:
  - handler and usecase tests annotated `@spec` for every scenario of "A dispute is answered" and "A closed dispute is settled";
  - a test that delivers `funds_withdrawn` before `created` and ends with one chargeback answered once.
- [ ] 6.7 Make the entity operation `ResaleListing.Create` refuse a Ticket of a disputed Order, taking the Order row `FOR SHARE` first in its transaction, before its Ticket lock (design Decision 2), and have `ResaleListingUseCase.Create` return its FailedPrecondition. Make the draw's free-listing query leave out listings of disputed Orders. Verify:
  - DB integration tests annotated `@spec` for "Refused while the payment is disputed";
  - usecase tests annotated `@spec` for "No listing while the payment is disputed" and for "Draw every stock due at a time" (all eight scenarios, including Listing of a disputed order);
  - a two-connection DB test of `ResaleListing.Create` against `Order.CommitRefund` on the same Order that shows no deadlock.

- [ ] 6.8 Make `NotificationUseCase.SendOrderRefunded` count the tickets refunded as the Order's ticket count less its Sold resale listings (`ResaleListing.ListByOrder`), and add the line saying the rest was already returned through the card issuer when the amount is below their price. Use the fan copy tone of the existing refund email, in Japanese and English. Verify with usecase tests annotated `@spec` for every scenario of "The refund notice once per refunded order", including Part returned through a dispute.

## 7. backend: 3D Secure on every card authorization (components/entity/card-authorization/create; design Decision 6)

- [ ] 7.1 Set `payment_method_options.card.request_three_d_secure = any` in `StripeCardAuthorizationProvider.Create`. Verify with a unit test annotated `@spec` for "Authentication asked for every card" that checks the parameter on every purpose (Checkout, lottery entry, resale entry). Read the frontend's confirm flow for each purpose and confirm that it handles a 3DS challenge with `handleNextAction` or `confirmCardPayment`; a purpose that does not is fixed in this change, with a Playwright run against the deployed app using the 3DS test card `4000002760003184`.

## 8. Production checks

- [ ] 8.1 After the backend merge (migrations apply to prod), check read-only:
  - the AtlasMigration status is applied;
  - the worker rolled out;
  - the worker logs one `release-due-settlements` run that claims and starts `release:` workflows for the due Settlements (or none);
  - `/worker workflow list` shows them SUCCESS.
- [ ] 8.2 Run the Stripe Sandbox E2E (`gh workflow run stripe-sandbox-e2e.yml`) extended with the dispute cases of design "Migration Plan". Each must show the expected Dispute status and Settlement state:
  - `4000000000002685`: contested, evidence submitted, won with `winning_evidence`, Settlement released afterwards;
  - `4000000000000259` after a 3DS challenge: contested;
  - an accepted chargeback: Order Refunded with the reason Dispute, Settlement Reversed;
  - `4000000000001976` (inquiry): recorded as an inquiry. Record whether an escalation arrives as `funds_withdrawn` on the same dispute or as a new dispute (design Risks);
  - `4000000404000079`: two disputes, each handled.
- [ ] 8.3 Before archiving, edit the main specs' Purposes that this change lists as (Purpose):
  - `components/entity/settlement`: Releasing in the status row, the release claim row, the release time row (empty while Held or Releasing), and the state diagram (`Held --> Releasing --> Released`, `Releasing --> Held`);
  - `components/entity/order`: the refund reason Dispute, the refund amount of an accepted inquiry, and the provider refund ID row (also present for an accepted inquiry's Dispute refund);
  - `components/usecase/settlement/release-due-settlements`: the sequence diagram claims and starts SettlementUseCase.Release instead of paying;
  - `components/usecase/order/refund`: the sequence diagram drops the Dispute and Released branches;
  - `components/adapter/fan/api/webhook/payment-events`: the Purpose says a dispute is answered, not refunded.

  Verify: `python3 scripts/check-diagrams.py` passes and each diagram matches its requirements.
