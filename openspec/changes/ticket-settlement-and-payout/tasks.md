## 0. Prerequisites (long-lead — gate launch, not spec)

> Legal/tax prerequisites (収納代行 counsel opinion, インボイス/適格請求書, 特商法, 総額表示,
> 個人情報越境移転, and the livemode Stripe 審査) are owned by the
> `payments-legal-compliance` change. They are deliberately NOT tracked here — do not
> re-add them to this list.

- [x] 0.1 Stripe Connect platform enablement; **recipient** config (`transfers` capability,
      `losses_collector = application`; platform responsible for connected-account negative
      balances). Verified across all three test-mode sandboxes — `local`, `ci`, and the
      older shared `pannpers.dev sandbox`: Connect is enabled on each, and every recipient
      the Connect PoC provisioned carries `capabilities.transfers = active` with **no**
      `card_payments` requested, `controller.losses.payments = application`,
      `controller.requirement_collection = application`, `controller.stripe_dashboard =
      none`, country JP / currency JPY, `details_submitted = true`. In `local` and `ci` the
      recipients are the current controller-properties shape (account `type = none`,
      `controller.fees.payer = application`); the `pannpers.dev sandbox` one predates that
      migration and is still legacy `type = custom`. Recipients show `payouts_enabled =
      false` pending `external_account` / `individual.verification.document` — that is
      per-Organizer KYC/KYB in the onboarding flow (§2), not platform config. Livemode is
      out of scope here: account 審査 is `payments-legal-compliance` §1.3.
- [ ] 0.2 Statement-descriptor strings — **decided; not yet applied to the account**:
      static `LIVERTY MUSIC` (13/22), Latin prefix `LIVERTY` (7/10), kanji-field
      `Liverty Music` (13/17), kana-field `リバティミュージック` (10/22, kana-only rule
      satisfied). Both the static descriptor **and** the prefix are set: Stripe otherwise
      derives the prefix by truncating the static value to 10 chars (`LIVERTY MU`) the
      moment a suffix is introduced. Per-event suffix is **not** in MVP — design already
      allows shipping the static descriptor alone, and the kanji field's 17-char budget
      leaves only ~8 chars after prefix + separator. Remaining work: set these on the
      platform account.

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
- [x] 1.5 protovalidate; buf lint/breaking; merge → Release → BSR gen (purely additive —
      does not touch #938's order/ticket/issuance/order_admin proto) [PR #945 → Release v0.63.0 → BSR gen ✓]

## 2. Backend — Connect onboarding

- [x] 2.1 Create Organizer connected account; onboarding link; **KYC/KYB status gate**
      (payout blocked until verified; sales/issuance unaffected)
      [`StripeSettlementPort.CreateConnectedAccount` now provisions a real Accounts v2
      recipient (POST /v2/core/accounts): `dashboard = none`, JPY/ja-JP defaults,
      fees+losses collector `application`, `stripe_balance.stripe_transfers` requested,
      `card_payments` NOT requested, `configuration.merchant.mcc = 7922` (a JP recipient's
      transfers capability will not activate without an MCC), organizer id in metadata and
      as the idempotency-key seed. Verified end-to-end against the `local` sandbox by
      `TestStripeSettlementPort_CreateConnectedAccount_Integration`, which provisions an
      account through the production adapter and asserts the returned shape, that it is
      created NOT payout-ready, that the port's status mapping agrees, and that the hosted
      onboarding link issues. The stale TODO and the `settlement_port.go` doc claiming a v1
      stand-in are corrected.]
- [x] 2.2 Persist connected-account ref + status; surface onboarding status to organizers
      [OrganizerConnectedAccount repo + OnboardingUseCase + PayoutOnboardingService handler]

## 3. Backend — payout controller (separate charges & transfers)

- [x] 3.1 Scheduled post-event process: for each settled Order past the release gate,
      **resolve `pi_` → `ch_`** (retrieve PaymentIntent, expand `latest_charge`) and create
      **`Transfer` with `source_transaction` = the captured charge `ch_`** to the
      Organizer's connected account (net share); platform fee = retained remainder;
      record the `ch_` on the settlement row
- [x] 3.2 **Release gate**: event `start_time` passed AND dispute buffer elapsed;
      **postponement resets** the clock to the new date
- [x] 3.3 **No `on_behalf_of`** (platform is the Stripe settlement merchant; seller-of-record
      is contractual). Statement descriptor = platform static prefix (set on the platform
      account, task 5.1) + optional per-event `statement_descriptor_suffix` (+ kanji/kana)
      on the charge — a small ④ charge-param enhancement, independent of the Transfer logic
- [x] 3.4 Splits engine: MVP one Organizer split; sum(splits) ≤ charge; extensible to N payees

## 4. Backend — refund / dispute execution

- [x] 4.1 Behind ⑤'s `OrderAdminService.RefundOrder`: execute `Refund` (platform balance)
      + **per-split `transfer_reversal`** clawback; handle inbound refund/dispute webhooks
      [processor-fee retention full-amount MVP + TODO; ⑤ RefundOrder policy handler done]
- [x] 4.2 Reserve past the dispute window; chargeback after payout draws on reserve /
      negative-balance responsibility
      [chargeback→reversal path done (dispute webhook → RefundOrder(DISPUTE) →
      transfer_reversal); the reserve half is the hold-to-event + dispute-buffer release
      gate (3.2); negative-balance responsibility is confirmed on the platform account
      (`controller.losses.payments = application`), verified under 0.1]
- [x] 4.3 Webhook ingest (transfer/payout/dispute): signature verify + **idempotent**
      (no double-refund, no double-reversal)

## 5. cloud-provisioning

- [ ] 5.1 cloud-provisioning plumbing: transfer/payout/dispute webhook endpoint +
      signing secret (GSM/ESO) for fan-api
      [PARTIAL: PR #489 is merged — the Pulumi-provisioned GSM secret, the `/stripe-webhook`
      HTTPRoute exact-path rule, and the optional `envFrom` are on main and applied to dev.
      The isolated `ExternalSecret` for `fan-api-stripe-webhook-secret` follows once the
      **prod** Stripe webhook endpoint is registered and the GSM key exists — a launch-time
      item, since prod is the only environment whose endpoint is ever registered]
      (Stripe-account-side config is not cloud's: `losses_collector = application` is
      done under 0.1, and the statement-descriptor prefix strings are 0.2.)

## 6. Verification

- [ ] 6.1 Stripe test-mode: capture (④) → funds on **platform** balance → post-event
      **Transfer to Organizer** (source_transaction) + retained fee; KYC-incomplete →
      payout withheld; cancellation refund → buyer refund + transfer_reversal;
      postponement resets gate; duplicate webhook idempotency
      [Runs against the `local`/`ci` sandboxes via `make test-stripe-e2e`. Inbound webhook
      legs (dispute → reversal, duplicate-delivery idempotency) are driven with the Stripe
      CLI forwarding events to the local webhook server — no registered endpoint and no
      public URL are involved, since no dev Stripe environment exists.]
- [ ] 6.2 Sync delta to main specs and archive
