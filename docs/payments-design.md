# Payments Design (Phase 3 ⑤)

Durable design for the ticket **payment** track — the input to the roadmap
change `ticket-purchase-and-issuance` (⑤). Consolidates the research and
decisions tracked in issue liverty-music/specification#778 so they are not
lost in ephemeral notes. Not legal advice — the counsel flags below must be
confirmed before launch.

Grounded in `ticketing-platform-roadmap.md` (Deferred Payment Details) and
the competitor/market research in `market-design-notes.md`.

## Decisions (settled)

- **Provider: Stripe Connect.** Chosen for breadth + DX. Money is
  **platform-intermediated** (Liverty collects, takes a fee, pays out the
  Organizer). *Challenger to PoC:* **KOMOJU (Degica)** is arguably a better
  fit for a JP lottery (authorize→split-at-capture, deepest JP methods) —
  run a serious PoC before locking in. Adyen for Platforms is the
  enterprise-scale "graduation" target.
- **Connect charge model:** **destination charges + `on_behalf_of=<organizer>`
  + `application_fee_amount`.** The Organizer is the settlement merchant on
  the buyer's statement (matches "Organizer = seller-of-record", below).
- **Methods: card-only for MVP** (incl. **debit / prepaid** cards — the
  cardless-fan substitute — and Apple Pay / Google Pay, which are just
  `card` wallets). **Konbini / PayPay are out of scope** for MVP (async
  settlement, ¥300k caps, PayPay's Connect incompatibility). The domain
  entity is provider- and method-agnostic, so they can be added later
  without a proto break. Trade-off: card-only excludes some cardless
  students/minors — accepted for a vetted-partner MVP, revisit on demand.
- **Lottery charge mechanism: `SetupIntent`-primary, NOT auth-hold.** This
  is the load-bearing correction (see Why below). At application, save the
  card via a `SetupIntent` (`usage=off_session`) — **no hold on the buyer's
  credit**. At the draw, charge **only winners** via an off-session
  `PaymentIntent` (MIT). A full-amount authorization hold is a narrow
  exception (high-value / extreme-scarcity where a funds guarantee matters).
- **Winner-charge-failure flow (required):** a saved card can fail at draw
  (expiry / insufficient funds / authentication_required). Grace + a
  re-auth link with a deadline → else **当選無効 → 繰上げ (waitlist)** — the
  JP "unpaid-by-deadline → void" convention. Do not collect CVC at draw
  (would reclassify as CIT).
- **Payout: hold to event + dispute window.** Organizer accounts on
  **manual payout**; release via Payouts API **after the event AND a
  dispute-safety buffer** (chargebacks arrive days-to-weeks later — "after
  event" alone is too early). Refunds via `Refund` (platform balance) +
  `transfer_reversal` to claw the Organizer's share.
- **Webhooks are the source of truth** for capture / refund / dispute — never
  issue tickets on the client confirm alone. Idempotent handlers.
- **Fee model: a flat percentage, buyer-shiftable.** A single clean % (like
  LivePocket's flat 5%) reads better than a stacked per-ticket fee (tiget's
  ¥220+¥99 draws complaints). Buyer-pass-through toggle → organizer cost can
  be ¥0. Exact rate is a business decision (#778).

### Why SetupIntent, not an authorization hold (the correction)

JP competitors (ぴあ / ローチケ / LivePocket / 楽天チケット) do **not** hold the
full amount at application — only a ¥1 validity check; the full 与信枠 hold
lands at **draw** time, and winners' cards are **auto-charged** after
results. Holding the full amount at application:
- ties up credit across the **many** lotteries a fan applies to (they win
  1–2), the exact 与信枠圧迫 JP platforms avoid; and
- **breaks on prepaid/debit** (the cardless-fan substitute), which release
  holds in 1–8 days — the reservation silently vanishes before the draw.

`SetupIntent` (save at apply, charge winners) matches the JP norm, avoids
credit lock-up, works with prepaid/debit, and does 3DS once at setup (JP
EMV-3DS mandate) with MIT-exempt winner charges.

## Legal / money scheme (収納代行) — not legal advice

- **収納代行 (collection agent) + intermediary marketplace; Organizer =
  seller-of-record.** Avoid MoR, 資金移動業, 前払式支払手段.
- Buyer ToS: the buyer's obligation is **discharged on paying the platform**.
  Organizer contract: grants the platform **代理受領権限**.
- **前払式 avoidance:** charge a **specific-event ticket at win, deliver
  promptly** — no wallet / points / stored balance.
- **特商法:** Organizer is the **販売業者** (own 特商法 表記 / group page). The
  **final-confirmation screen (2022)** must state total (tax+fees) and the
  **charge timing** — for lottery: "charged only if you win, at the draw;
  card saved for that later charge." Log consent + timestamp (also MIT /
  dispute evidence).
- **未成年:** DOB + parental-consent notice (an "18+" button is legally
  insufficient); own-name card implies consent.
- **Refund norm:** on cancellation refund face value + system/発券 fee, but
  **keep the payment-processor fee** (JP standard).
- **景品表示法 / 賭博: fine as designed** — paid 抽選販売 is allocation of the
  purchased ticket, not a 懸賞/景品, and not 賭博 since **losers pay ¥0**.
  Guardrails: losers pay nothing; no purchase-scaled free bonus; wording
  "抽選販売", not "prize".

## Counsel flags (confirm before launch)

1. **⚠️ Consumer-payer 収納代行 carve-out** — the buyer is a consumer; FSA
   2020-2025 rulemaking scrutinizes consumer-facing collection. This most
   directly determines whether we avoid a 資金移動業 license.
2. **⚠️ Hold-duration line** — the max defensible "after event, within N
   business days" before held funds are 預り金 → 資金移動業; plus disclosure.
3. Charge-after-win card-on-file + MIT — confirm no 割賦販売法 / 前払式 issue.
4. MoR / 特商法 seller-of-record + domestic-fee 課税 (10%) → register as
   適格請求書発行事業者; 媒介者交付特例 only if organizers are registered.
5. 消費者契約法 enforceability of refund/cancellation clauses.

## Domain entity (provider-agnostic)

Order/Payment carries only: `provider` (stripe), opaque `payment_intent_id`
(`pi_…`) + `payment_method_id` (`pm_…`), `payment_method_type` (card now;
konbini/paypay later), own `status` (`pending`/`paid`/`failed`/`refunded` —
no `awaiting_payment` now that konbini is out), `amount`+`currency`,
`paid_at`, optional display facets (`card_brand`/`card_last4`). Never store
PAN/CVC/expiry or Stripe's raw status. This keeps ⑤'s proto stable across a
provider switch (KOMOJU) or added methods.

## Open decisions (business / counsel, long lead — start now)

- KOMOJU-vs-Stripe PoC outcome; Stripe Connect account type + KYC/審査 apply.
- MoR designation + 特商法 seller wording; fee rate; hold-duration N;
  refund/cancellation policy; 適格請求書発行事業者 registration.

## References

- Tracking + research log: issue liverty-music/specification#778.
- Market/competitor design: `market-design-notes.md`.
