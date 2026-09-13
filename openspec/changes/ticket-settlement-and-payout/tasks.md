## 0. Prerequisites (long-lead — gate launch, not spec)

- [ ] 0.1 Stripe Connect platform enablement + KYC/審査; **Accounts v2 recipient** config
      (`transfers` capability, `losses_collector = application`; platform responsible for
      connected-account negative balances)
- [ ] 0.2 収納代行 single-payee counsel opinion (payments-design flag 1): discharge +
      hold-to-event + domestic + single business payee (not multi-party)
- [ ] 0.3 Statement-descriptor strings: platform default + prefix (Latin + kanji/kana);
      per-event suffix scheme
- [ ] 0.4 Stripe account-manager: `allocated_funds` JP availability + single-manual-capture
      support (currently JP-ineligible → MVP does NOT depend on it)

## 1. Proto / entity (specification → BSR)

- [x] 1.1 Organizer **connected-account ref + recipient/transfers status** (opaque `acct_`),
      payout-eligibility from `stripe_balance.stripe_transfers.status == active`
      (v2 capability, not v1 `payouts_enabled`)
- [x] 1.2 **`SettlementSplit`** (payee ref + amount or share) as a set; MVP = 1 Organizer
      split; extensible to N payees (venue/artist) without a breaking change
- [x] 1.3 **Payout / transfer** state (opaque `tr_`/reversal refs + the captured-charge ref
      `ch_` for `source_transaction`, own enums, no raw provider status), linked to ⑤'s
      Order. **Refund RPC is ⑤'s `OrderAdminService.RefundOrder` (#938) — NOT redefined
      here**; settlement records the transfer/reversal state behind it.
- [x] 1.4 RPCs: admin/console **payout** ops + organizer **onboarding-status** read
      (refund op is ⑤'s RefundOrder)
- [ ] 1.5 protovalidate; buf lint/breaking; merge → Release → BSR gen (purely additive —
      does not touch #938's order/ticket/issuance/order_admin proto)

## 2. Backend — Connect onboarding

- [ ] 2.1 Create Organizer connected account; onboarding link; **KYC/KYB status gate**
      (payout blocked until verified; sales/issuance unaffected)
- [ ] 2.2 Persist connected-account ref + status; surface onboarding status to organizers

## 3. Backend — payout controller (separate charges & transfers)

- [ ] 3.1 Scheduled post-event process: for each settled Order past the release gate,
      **resolve `pi_` → `ch_`** (retrieve PaymentIntent, expand `latest_charge`) and create
      **`Transfer` with `source_transaction` = the captured charge `ch_`** to the
      Organizer's connected account (net share); platform fee = retained remainder;
      record the `ch_` on the settlement row
- [ ] 3.2 **Release gate**: event `start_time` passed AND dispute buffer elapsed;
      **postponement resets** the clock to the new date
- [ ] 3.3 **No `on_behalf_of`** (platform is the Stripe settlement merchant; seller-of-record
      is contractual). Statement descriptor = platform static prefix (set on the platform
      account, task 5.1) + optional per-event `statement_descriptor_suffix` (+ kanji/kana)
      on the charge — a small ④ charge-param enhancement, independent of the Transfer logic
- [ ] 3.4 Splits engine: MVP one Organizer split; sum(splits) ≤ charge; extensible to N payees

## 4. Backend — refund / dispute execution

- [ ] 4.1 Behind ⑤'s `OrderAdminService.RefundOrder`: execute `Refund` (platform balance)
      + **per-split `transfer_reversal`** clawback; handle inbound refund/dispute webhooks
- [ ] 4.2 Reserve past the dispute window; chargeback after payout draws on reserve /
      negative-balance responsibility
- [ ] 4.3 Webhook ingest (transfer/payout/dispute): signature verify + **idempotent**
      (no double-refund, no double-reversal)

## 5. cloud-provisioning

- [ ] 5.1 Stripe Connect platform config (Accounts v2; `losses_collector = application`;
      platform statement-descriptor prefix incl. kanji/kana); transfer/payout/dispute
      webhook endpoints + secrets (ESO)

## 6. Verification

- [ ] 6.1 Stripe test-mode: capture (④) → funds on **platform** balance → post-event
      **Transfer to Organizer** (source_transaction) + retained fee; KYC-incomplete →
      payout withheld; cancellation refund → buyer refund + transfer_reversal;
      postponement resets gate; duplicate webhook idempotency
- [ ] 6.2 Sync delta to main specs and archive
