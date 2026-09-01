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

### 収納代行 determination — likely exempt (refined, 2025-2026 legal + market check)

**Why the license question exists at all:** moving other people's money
between remote parties (為替取引, 最決平成13年) is a licensed monopoly (bank
or 資金移動業). Operating unlicensed is **criminal** (銀行法 §61: up to 3yr /
¥3M, corporate 両罰 up to ¥300M) — which is why the boundary must be
*confirmed*, not assumed. 収納代行 is exempt because the buyer's debt is
**discharged on payment to the agent** → no protectable "money in flight".

**Our flow most likely sits in the exempt zone**, on two structural facts:
1. **Payee = business.** The 2020 amendment (施行 2021-05) pulls collection
   into 資金移動業 only when the **payee (受取人) is an individual acting in a
   non-business capacity** (割り勘 / C2C). Our Organizers are vetted
   **事業者** sellers-of-record → outside that trigger, so the traditional
   exemption holds.
2. **Domestic-only.** The 2025 amendment (公布 2025-06; 施行 ~2026) that newly
   regulates **cross-border 収納代行** applies to 国内⇄国外 flows only. A
   fully domestic buyer/platform/Organizer flow is untouched.

**Market corroboration:** holding buyer funds **until after the event** and
**charging lottery winners at the draw via a saved card** are the **universal
JP ticketing norm** (LivePocket, tiget, ZAIKO, Peatix, teket, e+/ぴあ/ローチケ
— none pays the organizer pre-event). **ZAIKO's terms explicitly operate as
収納代行 with the Organizer as seller and "immediate charge of the registered
card at the time of winning"** — essentially our design. So our hold-until-
event is **not** an anomaly; it is established practice, which supports the
escrow characterization rather than undermining it. The **only** genuine
divergence from incumbents is the **PSP rail** (Stripe Connect vs domestic
GMO/proprietary/イーコンテクスト) — a technology choice, not a business-model
one; Stripe Connect must be configured (manual payout) to *emulate* the
held-until-event settlement the incumbents get from delayed acquiring.

**Safe-harbor to stay clearly in exempt 収納代行** (structure in the contract
stack + T&Cs):
1. **Payee = 事業者** — contract/vet the Organizer as a business seller;
   never settle to a private individual.
2. **Discharge clause (load-bearing)** — buyer ToS: obligation **discharged
   on payment to the platform**; Organizer grants **代理受領権限**.
3. **Genuine underlying transaction** — a real ticket sale by the Organizer;
   platform = collection agent (keep the substance documented).
4. **Hold = escrow-with-counter-performance** — release gated on the
   **event occurring / ticket honored**, with evidence retained. (There is
   **no bright-line safe N-day** in the rules; safety comes from the
   discharge + counter-performance gate, not the length — this reframes the
   old "hold-duration" flag.)
5. **Collection via the licensed PSP** (Stripe).
6. **Stay domestic** — a foreign Organizer or offshore fund routing crosses
   into the 2025/2026 cross-border regime → re-analyze.

Points 1/5/6 are self-assessable; **2/3/4 need a written 弁護士 opinion**
(fact-specific + criminal downside).

## Counsel flags (confirm before launch)

1. **⚠️ 収納代行 exemption opinion (highest leverage — closes 資金決済法 +
   犯収法 together).** Get a written opinion confirming: (i) the discharge
   clause is effective and the platform is a collection agent (not
   seller/MoR), (ii) the **hold-until-event** design qualifies as exempt
   escrow (府令第1条の3, non-為替取引 / not 預り金), and (iii) no cross-border
   leg exists. Likely exempt (business-payee + domestic; see determination
   above), but the escrow/discharge boundary is where the FSA applies
   substance-over-form.
2. **Seller-of-record ↔ UX alignment** — if marketing/UX makes the *platform*
   look like the seller, the collection-agent theory weakens. Align the
   legal structure with the UX (Organizer named as 販売業者 at checkout).
3. Charge-after-win card-on-file + MIT — confirm no 割賦販売法 / 前払式 issue.
4. MoR / 特商法 seller-of-record + domestic-fee 課税 (10%) → register as
   適格請求書発行事業者; 媒介者交付特例 only if organizers are registered.
5. 消費者契約法 enforceability of refund/cancellation clauses.

### Official-resale counsel addenda (from `resale-design.md`)

Resale-specific items for the same #778 legal track. Full design +
research: [`resale-design.md`](./resale-design.md). "Δ" marks where the
resale analysis differs from or extends the primary-sale analysis above.

1. **⚠️ 資金移動業 for the resale money legs (highest leverage).** Resale is
   **two decoupled legs**: (a) buyer→Organizer fresh face-value sale =
   the same 収納代行/事業者-payee scheme as the primary sale (may hold to
   event); (b) seller refund = a **refund of the seller's own payment**.
   Confirm leg (b) avoids 資金移動業 via **both** grounds: it is a refund
   (not a payee transfer) AND, if the seller is nonetheless viewed as an
   individual payee, it fits the **資金決済法 2条の2第2号 escrow exclusion**
   (funds received before/with counter-performance, moved to the payee
   **after counter-performance = the seller's ticket delivery via
   void+reissue**). **Δ vs primary:** the seller-refund leg is **settled
   ~days-to-3-weeks after the resale completes, NOT held to the event** (ぴあ
   /ticket board/e+/tiget norm) — so the primary "hold-until-event" escrow
   framing does **not** govern this leg; confirm the "refund of own money"
   vs "代金交付" framing given the buyer funds the balance.
2. **古物営業法** — confirm **no 古物商許可** for a **no-inventory,
   organizer-consigned, electronic-ticket** resale (void-original + reissue,
   platform never buys/stocks); and the boundary if physical tickets are ever
   handled (→ 金券類 古物商許可).
3. **不正転売禁止法 — blanket organizer consent.** Confirm the **standing
   consent** in the vetted-Organizer platform agreement satisfies the
   興行主の同意 requirement for **all** that Organizer's events (no per-event
   re-consent needed), so mandatory-by-default resale is not "unauthorized".
   Flag the **artist/promoter no-resale rider** edge — an Organizer bound
   upstream cannot consent; confirm the **admin-exception** carve-out suffices.
4. **本人確認 re-bind keeps 特定興行入場券.** Confirm reissuing with the new
   holder's 本人確認 (name+contact) + the 3 face conditions preserves the
   covered-ticket protection for the new owner.
5. **特商法 §12-6 返品特約 on the buyer's 最終確認画面 (Δ: distinct from the
   fee disclosure)** — the resale buyer's fresh purchase is a 通信販売;
   displaying 返品不可 defeats the §15-3 8-day return right. **Frame the
   resale fee as 役務提供の対価 (not 違約金/キャンセル料)** to lower 消費者契約法
   §9/§10 risk on the "non-refundable / not-guaranteed-if-unsold" terms.
   (Extends counsel flag #5 and obligations-table #2 to the resale leg.)
6. **個人情報保護法 — 本人確認 lifecycle (Δ).** Define 利用目的 (resale as a
   purpose), retention through the hold-back/dispute window, then **deletion**
   of the voided seller's 本人確認; both-party anonymity avoids §27 第三者提供.
   (Beyond the Stripe 越境移転 item in obligations-table #4.)
7. **消費税 / インボイス on the resale fee (Δ).** The seller-side ~10% fee is
   課税取引 under 総額表示; decide **税抜 vs 税込** — if 税込, effective take is
   ~9.1% after consumption tax, which affects the fee-band choice.
8. **令和7年 (2025) 資金決済法改正 (施行 ~令和8年6月).** Confirm the narrowed
   收納代行 / cross-border rules do **not** pull this domestic resale flow into
   為替取引; this brief predates the amendment.

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
- MoR designation + 特商法 seller wording; fee rate; payout schedule
  (event-end-keyed, like the incumbents — the escrow *gate* matters, not a
  bright-line duration); refund/cancellation policy; 適格請求書発行事業者
  registration.

## Regulatory compliance obligations (JP) — beyond the 収納代行 scheme

Additional obligations surfaced by the 2026-08 legal sweep (issue #778).
Not legal advice — confirm the flagged items with counsel. **Owner** = who
implements/holds the duty.

| # | Obligation | Blocking | Owner | What to build / disclose |
|---|-----------|----------|-------|--------------------------|
| 1 | **総額表示義務** (消費税法 §63, since 2021-04) | **Yes** | Platform | Render every consumer-facing price **tax-inclusive** (ticket AND system/payment fee, each as its own 税込 line) + a clear grand total on listing/cart/confirmation. |
| 2 | **特商法 通信販売: 最終確認画面 + 返品特約 + no cooling-off** (§11, §12-6 2022) | **Yes** | Platform (screen) / Organizer (事業者情報) | Confirmation screen showing 分量・価格(税込)・**支払時期方法**・**引渡時期**・**返品特約**・per-Organizer **事業者情報**; make the **charge-on-lottery-win timing/amount unambiguous**; state "通信販売 = クーリングオフ無し". **Omitting 返品特約 triggers an 8-day statutory return right** — so spell out "no returns except event cancellation/postponement". |
| 3 | **割賦販売法 (2018): card-data 非保持化 / PCI** | **Yes (precondition)** | Platform (加盟店) / Stripe | Stripe Elements so **no PAN touches our systems** (store only Stripe tokens/customer ids — incl. the saved-card-at-draw flow); keep **PCI SAQ A** + EMV 3DS on file. |
| 4 | **個人情報保護法 (2022): 越境移転 to Stripe (US)** | **Yes** | Platform | Privacy policy: personal/card data is **entrusted (委託) to an overseas processor (Stripe, USA)** + **外的環境の把握** (US regime + Stripe safeguards); hold a **Stripe DPA** as 委託先監督 evidence. |
| 5 | **犯収法 / AML-KYC** | Confirm | Stripe (card-level) | A pure 収納代行 that does **not** perform 為替取引 is generally **not** a 犯収法 特定事業者. Document why the flow is 収納代行, not remittance. **Same determination as the 資金決済法 boundary** — close it once. |
| 6 | **反社会的勢力排除 (暴排条例)** | **Yes** | Platform | Organizer onboarding contract with a **暴排条項** (表明保証 + immediate termination) + a **反社チェック** step in vetting. *(Belongs to the organizer-accounts vetting flow — cross-reference.)* |
| 7 | **電子帳簿保存法 (2024 電子取引 mandatory)** | From day one | Platform | Retain fee invoices/receipts/transaction records electronically with **真実性 + 可視性** (searchable by date/amount/counterparty). |
| 8 | **領収書 + 印紙税 / 適格請求書** | Low | Organizer (ticket) / Platform (fee) | Receipts must **print "クレジットカード決済"** → 印紙-free at any amount. 適格請求書: Organizer 登録番号 on the ticket, platform 登録番号 on the fee (代理交付/媒介者交付特例). |

**Highest-leverage counsel question (closes #5 + reinforces 資金決済法):**
confirm our payout timing/holding keeps 収納代行 **out of 為替取引 /
資金移動業** — this single determination decides both the license question and
whether 犯収法 KYC applies to the platform.

## Commerce spec still to define (in ⑤ `ticket-purchase-and-issuance`)

Non-regulatory gaps to specify when ⑤ is authored:

- **Pricing model:** Organizer-set price, JPY, tax-inclusive, ticket tiers
  (adult/child sharing the capacity pool), any price cap.
- **Order ↔ Ticket ↔ Payment linkage:** one Order = N tickets (companion,
  ≤ `max_tickets_per_application`); a successful charge issues N tickets.
- **Refund taxonomy:** **postponement (延期, event still happens) vs
  cancellation (中止)**, partial refunds, and the "no returns except
  cancellation" 返品特約 wording (ties to §2 above).
- **Payout mechanics:** payout schedule, per-Organizer **settlement
  statement (支払明細)**, failed-payout + negative-balance handling, Stripe
  KYC bank onboarding.
- **Dispute/chargeback ops:** evidence/representment, Organizer↔platform
  liability split via `transfer_reversal`, reserve past the dispute window.
- **Platform-fee 適格請求書** to the Organizer + Stripe-balance
  reconciliation.
- **Webhook security** (signature verification) + idempotency keys; a
  **test/sandbox** strategy for the lottery charge flow.
- **Purchase limits** (1 account / 1 application) enforced at the
  payment/order layer (anti-scalp).

## References

- Tracking + research log: issue liverty-music/specification#778.
- Market/competitor design: `market-design-notes.md`.
