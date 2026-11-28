## Why

Under 収納代行 (collection agency) the platform holds a fan's money for the Organizer, the 販売業者 (seller), and pays it out 7 days after the event. Three defects let that money end up with the wrong party:

- **A payout can stay with the Organizer after the money went back to the fan** (liverty-music/backend#922). The release sweep runs as one workflow step, so a payout made just before a failure is not recorded. The refund path also records Reversed over a Settlement it read as Held, after the sweep has already paid the Organizer.
- **Every dispute (chargeback) is conceded the moment it opens.** On the payment provider's "dispute created" notice, the platform voids the Tickets, claws back the Organizer's payout and marks the Order Refunded. It does this even when the fan entered the venue, so an Organizer that performed loses its sale to any cardholder who files a claim. The provider's own guidance for platforms is to contest with evidence and claw back only when the dispute is lost.
- **An Event can be cancelled after it took place.** Nothing limits 中止 (cancellation) in time, so an Organizer can cancel a concert after it was held. The release spec even defines a payout racing such a cancellation.

The product has no paying fans yet, so this is the moment to fix the money rules before real money flows.

## What Changes

The change follows one goal: each yen ends with the party entitled to it under the sale. A cardholder who did not authorize the payment, or whose Event was cancelled, gets the money back. An Organizer whose performance the cardholder bought and could attend keeps its split. The platform never pays out money it may have to return without being able to claw it back.

- **Cancellation ends 24 hours after the start.** An Event can be CANCELLED only until 24 hours after its start time, so a concert stopped midway late at night can still be cancelled and refunded the next day. After that it is a held concert. An Event with no start time stays cancellable, and its payout is withheld anyway.
- **A dispute is recorded and answered on its merits** (new Dispute entity):
  - **Contest**:
    - a dispute that claims neither fraud nor a fact only a person can check (not received, not recognized, cancelled, refund not processed, other);
    - a fraud claim on a payment the cardholder verified: authenticated by their card issuer (3D Secure; an attempt the issuer only acknowledged does not count) or paid with a device wallet.
  - **Accept**:
    - a fraud claim with no such verification;
    - a dispute on an Order of a CANCELLED Event that was not yet refunded. That fan is owed the money anyway.
  - **Review by an admin**: a duplicate, not-as-described or card-network-rule claim, and any claim on a concert at which no Ticket was admitted by its cancellation limit (24 hours after the start). The records cannot tell whether the fan was charged twice, got something other than what was sold, or whether the concert took place at all, so it is contested by default only if no admin answers by 48 hours before the deadline.
  - **Accept** also covers a chargeback the payment provider accepts no evidence for.
  - **Contest by showing the refund**: an Order whose own refund was made, including one the payment provider made that is not yet recorded.

  An inquiry (the issuer only asks; nothing is taken back) is answered the same way; accepting it means refunding the payment. An inquiry that escalates to a chargeback is answered again.
- **Contested: the payment stands until the outcome.** The Tickets stay valid; no ticket of the Order can be listed for resale, and a Listed one is Cancelled; nothing is clawed back. Evidence is submitted automatically:
  - the purchase and the account it is bound to;
  - the Tickets issued to that account;
  - the Admissions;
  - the refund rule shown at purchase (返品特約, no returns except 中止);
  - every refund already made from the payment, resale refunds included.

  It is submitted after the event, so that Admissions are included, and no later than 48 hours before the provider's deadline.
- **Settle on the outcome.**
  - Won: nothing changes. When the Event was cancelled while the dispute was open, an admin is paged to make the 中止 refund that could not be made during it.
  - Lost or accepted:
    - the Tickets still Issued are Voided;
    - a Held Settlement becomes Reversed;
    - each paid split of a Released Settlement is clawed back;
    - the Order is Refunded with the reason Dispute.
  - A partial dispute (less than the price of the Tickets not resold) leaves the Order and its Tickets as they are and takes back only the Organizer's share of the disputed amount.
  - Until a lost or accepted dispute's money outcome is applied, the Order stays disputed: no payout, no resale, no 中止 refund.

  The platform keeps bearing its own fee. The dispute received fee is to be borne by the Organizer when a dispute is lost or accepted and by the platform when it is won (owner's decision); passing it on needs an Organizer agreement term and a payout deduction, which are a change of their own (liverty-music/specification#1504), so until then the platform bears it.
- **No payout while an Order is disputed, and every payout is recorded or left for an admin to reconcile.** The 5-minute sweep claims each due Settlement, Held → **Releasing** under a new release claim, refused while its Order has an open or unsettled Dispute. It then starts one durable release workflow per claim, which:
  - pays each split, with the provider payout ID recorded by the workflow;
  - marks it Released.

  A claim whose workflow never started is started by the next sweep. A payout whose outcome the provider leaves unknown keeps the Settlement Releasing for an admin to reconcile, instead of being retried.

  The dispute settlement waits for a release in progress before clawing back. The race of #922 and its lost payout record go away. (Releasing is a new Settlement status: **BREAKING** for proto consumers that switch on SettlementStatus.)
- **OrderUseCase.Refund is for 中止 (cancellation) only.** A Dispute refund is no longer requested through it; the admin refund RPC gets InvalidArgument for the reason Dispute. It refuses to refund an Order with an open Dispute, since the provider refunds a disputed charge through the dispute.
- **Every card authorization asks for 3D Secure** whenever the card supports it. It is the evidence that lets the platform contest a fraud claim, and it usually shifts liability for fraud claims to the card issuer.
- **Every dispute notifies an admin**, so a concentration of disputes on one Organizer or sale is seen early.
- Supersedes the proposal-only change `dispute-representment`, which conceded every dispute without an Admission, including those before the event. It is removed in this change's plan PR.

## Capabilities

### New Capabilities

- `components/entity/dispute`: the Dispute entity: a cardholder's claim against an Order's payment, its reason, status (Open, Contested, Accepted, Won, Lost), deadlines and the rule that decides whether it is contested.
- `components/entity/dispute/sync`: record a dispute as the payment provider reports it now, moving only forward, so late, repeated or out-of-order notices are safe.
- `components/entity/dispute/get`: read a Dispute by its id.
- `components/entity/dispute/list-by-order`: the Disputes of an Order (a payment can carry more than one).
- `components/entity/dispute/accept`: concede the dispute (a chargeback to the payment provider; an inquiry by its caller's refund) and record it Accepted.
- `components/entity/dispute/submit-evidence`: hand the evidence to the payment provider and record it Contested.
- `components/entity/dispute/mark-settled`: record that a lost or accepted dispute's money outcome was applied.
- `components/entity/order/is-cardholder-authenticated`: whether the cardholder verified the Order's payment (card issuer authentication or a device wallet).
- `components/entity/order/get-provider-own-refund`: the Order's own refund at the payment provider, recorded or not, told apart from resale refunds.
- `components/entity/admission/count-by-event`: how many Tickets of an Event were admitted.
- `components/entity/ticket/list-by-order`: the Tickets an Order issued.
- `components/entity/resale-listing/cancel-listed-by-order`: cancel the Listed resale listings of an Order's Tickets.
- `components/entity/resale-listing/list-by-order`: the resale listings of an Order's Tickets, with their refunds.
- `components/entity/settlement/claim`: start a release, Held → Releasing under a release claim, refused while the Order has an open or unsettled Dispute.
- `components/entity/settlement/list-releasing`: the Releasing Settlements with their release claims.
- `components/entity/settlement/give-up-disputed-share`: lower a Held Settlement by the Organizer's share of a partial dispute, settling it.
- `components/entity/settlement/unclaim`: return a Releasing Settlement whose payout could not start to Held.
- `components/usecase/dispute/respond`: record a newly opened or escalated dispute and accept, review or contest it.
- `components/usecase/dispute/submit-evidence`: re-check the decision and submit the evidence of a contested dispute, at the time Respond scheduled.
- `components/usecase/dispute/settle`: apply the outcome of a closed dispute.
- `components/usecase/settlement/release`: pay out one claimed Settlement.

### Modified Capabilities

- `components/entity/event`: an Event can be CANCELLED only until 24 hours after its start (its cancellation limit).
- `components/entity/series/cancel-events`: a past Event cannot be cancelled.
- `components/usecase/series/cancel`: without named Events, only the Events still cancellable are taken; a named past Event fails.
- `components/entity/settlement` (Purpose): the Releasing status, the release claim and their transitions; release eligibility also needs no open or unsettled Dispute.
- `components/entity/settlement/mark-released`: records the release of a Settlement Releasing under the given release claim.
- `components/entity/settlement/reverse-payout`: once per payout and claw-back (the Order's refund, or one Dispute) however late it is retried, including after the payout was fully reversed.
- `components/usecase/settlement/release-due-settlements` (Purpose): claims each due Settlement and starts its release instead of paying in one step, and starts the release of a claim left unstarted; the scenarios about a cancellation racing a payout are removed.
- `components/entity/order` (Purpose): the refund reason Dispute means a dispute lost or accepted; its refund amount is above 0 for an accepted inquiry.
- `components/entity/order/commit-refund`: the Settlement becomes Reversed only from the status the caller read (Held or Released); a Dispute refund of an accepted inquiry carries its refund.
- `components/usecase/order/refund` (Purpose): Cancellation only; refuses an Order with an open Dispute; a Released Settlement is an inconsistency.
- `components/adapter/fan/api/webhook/payment-events` (Purpose): "dispute created" and an inquiry's escalation start DisputeUseCase.Respond, "dispute closed" starts DisputeUseCase.Settle once per outcome; the requirement "A dispute refunds the Order" is renamed "A dispute is answered".
- `components/entity/resale-listing/create`: refused, atomically, while the Ticket's Order has an open Dispute.
- `components/usecase/resale-listing/create`: returns that refusal.
- `components/usecase/resale-entry/draw`: a listing of a disputed Order is not allocated.
- `components/entity/order/create-refund`: a refund for an accepted inquiry is its own purpose, apart from the Order's own refund.
- `components/usecase/notification/send-order-refunded`: the tickets refunded are the ones not resold, and the email says when part was already returned through a dispute.
- `components/entity/concert/delete`, `components/entity/organizer/delete`: refused while an Order is disputed; the Disputes of removed Orders are removed.
- `components/entity/card-authorization/create`: asks for 3D Secure whenever the card supports it.

Unchanged and relied on: the admin refund RPC (`components/adapter/admin/api/rpc/order` already returns the usecase's InvalidArgument for a Dispute reason unchanged), Settlement.ListHeld, Settlement.GetByOrderID, Admission (its Purpose already keeps it as chargeback evidence), Admission.GetByTicket, Settlement.CreatePayout (already once per Settlement and payee, and Release retries it only within 12 hours), Order.CreateRefund, Order.Get, Order.GetByProviderPaymentID, Event.Get and Event.GetEventStartTime.

## Impact

- **specification (proto)**: `SettlementStatus` gains `SETTLEMENT_STATUS_RELEASING` (needs a Release before backend work).
- **backend**:
  - the release sweep claims and starts one workflow per claim, inside its existing single step;
  - a dispute workflow per provider dispute;
  - `disputes` table and a Settlement status migration;
  - a payment-provider dispute port (evidence, accept, provider state), and a reversal lookup in `ReversePayout`;
  - the webhook now handles dispute created, funds withdrawn (an inquiry's escalation) and dispute closed;
  - `request_three_d_secure` on PaymentIntents;
  - `OrderUseCase.Refund` (the admin handler only passes its InvalidArgument through);
  - the Event cancellation guard, with the start instant computed when cancelling as it is for the payout;
  - the lock order of `Order.CommitRefund` (Order first) and event removal's dispute guard.
- **frontend**: none required. A fan who files a dispute and then tries to list the Ticket sees the existing generic listing error.
- **cloud-provisioning**: add `charge.dispute.funds_withdrawn` to the webhook endpoint's events (`src/index.ts`; `charge.dispute.created` and `charge.dispute.closed` are already subscribed, and the latter is acknowledged without effect today), the log-based alert on every opened dispute, and a runbook section for the admin cases. The prod `pulumi up` is the owner's step.
- **Ops**: every opened dispute notifies the admin. A Review answer, a fan paid twice, a late win, a cancellation refund owed after a win, and an evidence submission that misses the deadline page through `workflow.needs_admin`; partial disputes are settled automatically.
